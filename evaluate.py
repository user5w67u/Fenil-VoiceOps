"""Reproducible offline retrieval evaluation on the supplied 52 practice questions.

This evaluates retrieval only; it does not claim LLM answer accuracy. Outputs are saved
as JSON/CSV so the results can be reviewed and reported honestly.
"""
import argparse, csv, json, re, sys
from pathlib import Path
from src.config import DATASET_DIR, TOP_K
from src.retrieval import Retriever

SECTION_RE = re.compile(r"\b[A-Z]{2,8}(?:v\d+)?-\d+(?:\.\d+)?\b")
SKU_RE = re.compile(r"\b[A-Z]{3}-\d{4}\b")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--top-k',type=int,default=TOP_K)
    parser.add_argument('--out-dir',default='evaluation')
    args=parser.parse_args()
    kb=DATASET_DIR/'kb'; qfile=DATASET_DIR/'practice'/'questions.csv'
    if not kb.exists() or not qfile.exists():
        raise SystemExit(f'Dataset files not found. Set DATASET_DIR in .env. Expected {kb} and {qfile}')
    retriever=Retriever(kb)
    with qfile.open(encoding='utf-8-sig',newline='') as f: questions=list(csv.DictReader(f))
    rows=[]; answerable=0; evidence_hits=0; unsupported=0; unsupported_zero=0; reciprocal=[]
    for q in questions:
        query=(q.get('asr_text') or '').strip() or q.get('question','')
        hits=retriever.search(query,args.top_k)
        gold=set(SECTION_RE.findall(q.get('gold_evidence','')))
        gold_skus=set(SKU_RE.findall(q.get('gold_evidence','')))
        retrieved_sections=[]
        for h in hits:
            retrieved_sections.extend(SECTION_RE.findall(h.get('section','')))
            # Some IDs appear in chunk body rather than section heading.
            retrieved_sections.extend(SECTION_RE.findall(h.get('text','')))
        ranks=[]
        for idx,h in enumerate(hits,1):
            combined=h.get('section','')+' '+h.get('text','')
            found=set(SECTION_RE.findall(combined)); found_skus=set(SKU_RE.findall(combined))
            if (gold and found.intersection(gold)) or (gold_skus and found_skus.intersection(gold_skus)): ranks.append(idx)
        is_answerable=str(q.get('answerable','')).lower()=='true'
        if is_answerable:
            answerable+=1
            if ranks:
                evidence_hits+=1; reciprocal.append(1/min(ranks))
            else: reciprocal.append(0.0)
        else:
            unsupported+=1
            if not hits: unsupported_zero+=1
        rows.append({
            'id':q.get('id',''),'language':q.get('language',''),'query':query,
            'answerable':is_answerable,'expected_decision':q.get('expected_decision',''),
            'gold_evidence':q.get('gold_evidence',''),'retrieved_evidence_hit':bool(ranks),
            'first_matching_rank':min(ranks) if ranks else '',
            'top_sources':' | '.join(f"{h['source']}::{h['section']} ({h['score']:.3f})" for h in hits),
            'top_scores':' | '.join(f"{h['score']:.3f}" for h in hits),
        })
    n=len(rows)
    summary={
      'dataset_reference_date':'2026-10-20','question_count':n,'top_k':args.top_k,
      'retriever':'Hybrid word/character TF-IDF over current KB sections plus product catalog; superseded documents excluded',
      'answerable_questions':answerable,
      'answerable_gold_evidence_hit_at_k':round(evidence_hits/answerable,4) if answerable else None,
      'answerable_gold_evidence_hits':evidence_hits,
      'mean_reciprocal_rank_on_answerable_questions':round(sum(reciprocal)/answerable,4) if answerable else None,
      'unsupported_questions':unsupported,
      'unsupported_questions_with_zero_retrieval_results':unsupported_zero,
      'limitations':'Retrieval-only metrics. They do not measure generated answer correctness, refusal quality, conversation handling, or speech quality.'
    }
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    with (out/'retrieval_results.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (out/'retrieval_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    print(f'\nDetailed results: {(out/"retrieval_results.csv").resolve()}')
if __name__=='__main__': main()
