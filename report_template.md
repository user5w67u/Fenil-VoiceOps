# VoiceOps 2026 — ZentroMart Support Agent Report

**Team:** [Team name]  
**Repository:** [Public GitHub URL]

## 1. What we built
- Step 1: LLM baseline with ZentroMart support role and explicit uncertainty policy.
- Step 2: TF-IDF retrieval over current policy/help/FAQ documents with section-level source traces; superseded returns policy excluded.
- Step 3: conversational state, verified order lookup, ticket creation and human handover.
- Step 4: Gnani STT/TTS batch pipeline and spoken reply files.

## 2. Evaluation
| Metric | Step 1 baseline | Step 2 RAG | Method |
|---|---:|---:|---|
| Correct decisions / 52 | [measure] | [measure] | Practice questions |
| Grounded / correct abstention | [measure] | [measure] | Gold facts and evidence |
| Retrieval evidence hit rate | N/A | [measure] | `gold_evidence` |
| Conversation turns handled / 96 | N/A | [measure] | Expected decisions/tool calls |

**Do not fill in unmeasured results.** Use the supplied practice files and record your actual runs.

## 3. What went wrong and fixes
[Document concrete failures found in evaluation, the root cause, and the change made.]

## 4. Bonus work
[Only list features that were implemented and tested.]

## 5. Reproducibility
- Install: `pip install -r requirements.txt`
- Configure `.env` locally using `.env.example`.
- Run: `python run.py --audio-dir <folder> --out-dir outputs`
