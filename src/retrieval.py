"""Hybrid lexical retrieval over current KB sections and the supplied product catalog."""
from pathlib import Path
import csv, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PRIORITY = {"policy": 5, "agent_guide": 4, "help": 3, "faq": 2, "marketing": 1, "meta": 0}

def _metadata(text, filename):
    meta = {"doc_id": filename, "title": filename, "doc_type": "faq", "status": "current", "effective_from": ""}
    for line in text.splitlines()[:18]:
        m = re.match(r"^\s*([a-zA-Z_]+):\s*(.*?)\s*$", line)
        if m: meta[m.group(1)] = m.group(2).strip().strip('"')
    return meta

def load_chunks(kb_dir):
    kb_dir=Path(kb_dir); chunks=[]
    for path in sorted(kb_dir.glob("*.md")):
        raw=path.read_text(encoding="utf-8")
        meta=_metadata(raw,path.name)
        if meta.get("status","current").lower()=="superseded" or "superseded" in path.name:
            continue
        sections=re.split(r"(?m)^(## \[[^\]]+\].*)$", raw)
        current_heading=meta.get("title",path.name)
        for part in sections:
            if part.startswith("## ["):
                current_heading=part.strip()
            elif part.strip():
                paras=re.split(r"\n\s*\n",part.strip()); buf=""
                for para in paras:
                    if len(buf)+len(para)>1100 and buf:
                        chunks.append({**meta,"section":current_heading,"text":buf.strip(),"source":path.name,"kind":"kb"}); buf=para
                    else: buf=(buf+"\n\n"+para).strip()
                if buf: chunks.append({**meta,"section":current_heading,"text":buf.strip(),"source":path.name,"kind":"kb"})
    # Product attributes are factual structured data supplied with the capstone.
    products=kb_dir.parent/'data'/'products.csv'
    if products.exists():
        with products.open(encoding='utf-8-sig',newline='') as f:
            for row in csv.DictReader(f):
                text=' | '.join(f'{k}: {v}' for k,v in row.items() if v not in (None,''))
                sku=row.get('sku','unknown')
                chunks.append({'doc_id':f'product:{sku}','title':row.get('name',sku),'doc_type':'product_catalog','status':'current','effective_from':'','section':f'PRODUCT {sku}','text':text,'source':'products.csv','kind':'product'})
    return chunks

class Retriever:
    def __init__(self,kb_dir):
        self.chunks=load_chunks(kb_dir)
        if not self.chunks: raise RuntimeError(f"No knowledge documents found in {kb_dir}")
        corpus=[c['section']+' '+c['text'] for c in self.chunks]
        # Word features preserve meaningful policy terms; character features help with
        # ASR spelling variation, SKU speech-to-text, and mixed-language queries.
        self.word_vectorizer=TfidfVectorizer(ngram_range=(1,2),stop_words='english',sublinear_tf=True)
        self.char_vectorizer=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=1,sublinear_tf=True,max_features=180000)
        self.word_matrix=self.word_vectorizer.fit_transform(corpus)
        self.char_matrix=self.char_vectorizer.fit_transform(corpus)
    def search(self,query,k=5):
        qw=self.word_vectorizer.transform([query]); qc=self.char_vectorizer.transform([query])
        ws=cosine_similarity(qw,self.word_matrix).ravel(); cs=cosine_similarity(qc,self.char_matrix).ravel()
        # Word similarity gets more weight; char n-grams rescue ASR variants.
        scores=0.72*ws+0.28*cs
        # Small tie-break preference follows the brief's source authority order.
        priority={'policy':0.018,'agent_guide':0.014,'help':0.010,'faq':0.006,'product_catalog':0.005,'marketing':0.001,'meta':0.0}
        scores=scores+__import__('numpy').array([priority.get(c.get('doc_type','faq'),0.0) for c in self.chunks])
        order=scores.argsort()[::-1]; results=[]
        for i in order[:max(k,0)]:
            if scores[i] <= 0.015: continue
            c=dict(self.chunks[i]); c['score']=float(scores[i]); results.append(c)
        return results
