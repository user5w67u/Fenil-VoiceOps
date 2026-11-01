# Fenil VoiceOps — ZentroMart AI Support Agent

A VoiceOps 2026 capstone implementation for ZentroMart, the fictional ecommerce store in the supplied dataset. The app combines document-grounded retrieval, structured product data, conversational state, privacy-gated order lookup, human-handover tickets, and an optional Gnani speech pipeline.

> **Honest status:** the chat/RAG path, dataset validation, retrieval evaluation, and seven automated tests have been run in the development environment. The full LLM answer benchmark and end-to-end Gnani audio test have **not** been measured here. Gnani audio mode requires your own `GNANI_API_KEY`. Do not claim voice was tested until you record a successful audio run.

## Features

- **RAG:** current Markdown policies and FAQs plus the supplied product catalog; word and character TF-IDF retrieval; visible source/chunk traces.
- **Version handling:** excludes superseded documents, including `pol_returns_v3_superseded.md`.
- **Conversation:** maintains recent context for follow-up questions and asks clarifying questions when information is missing.
- **Order privacy:** calls the supplied `lookup_order` tool and reveals order data only after the tool returns `verified=True`; allows one retry after a failed verification; redacts verification inputs from chat history.
- **Human handover:** calls the supplied `create_ticket` tool and confirms ticket creation only if the tool returns `created=True`.
- **Voice:** optional batch STT → same agent → TTS path using Gnani only, with a JSON trace, retrieved chunks and WAV reply for each input file.
- **Evaluation:** retrieval hit@k / reciprocal-rank report over the 52 supplied practice questions and unit tests for privacy, retries, handover and retrieval behavior.

## Dataset setup

1. Extract `Capstone_Project_Dataset_FTTT_2026.zip`.
2. Keep the extracted `Capstone_Project_Dataset_FTTT_2026` folder beside this `zentromart_voiceops` folder, or set `DATASET_DIR` to its absolute path in `.env`.
3. The dataset is synthetic and must remain outside the submission ZIP.

Recommended layout:

```text
Capstone_Project/
├── Capstone_Project_Dataset_FTTT_2026/
└── zentromart_voiceops/
```

## Install on Windows

Use the Python version already working on your machine (Python 3.12 or 3.13 is recommended for dependency compatibility):

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` if needed. The default LLM is `Qwen/Qwen2.5-0.5B-Instruct`, which downloads on first use and runs locally; no LLM API key is required. CPU inference may be slow. Alternatively, set `LLM_PROVIDER=api` and supply your own compatible API credentials locally. Never commit `.env` or share API keys.

Example `.env` settings:

```dotenv
LLM_PROVIDER=local
LOCAL_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct
GNANI_API_KEY=
DATASET_DIR=../Capstone_Project_Dataset_FTTT_2026
TOP_K=5
```

## Run the app

```powershell
streamlit run app.py
```

The sidebar includes a new-conversation reset. Expand **Evidence & tool trace** under a reply to inspect retrieved source sections and tool actions.

## Run the required batch interface

Put short customer audio clips (up to 60 seconds each) in `sample_audio/`, then run:

```powershell
python run.py --audio-dir sample_audio --out-dir outputs
```

This command uses Gnani STT and TTS only. Set `GNANI_API_KEY` in `.env` and install the official SDK using the package name specified in the brief (`pip install gnani-vachana`). The runner uses `en-IN`, the `Kaveri` voice and `timbre-v2.5`. It saves each transcript, answer, retrieved source chunks, tool actions and reply audio, plus a `manifest.json`. Each audio file starts a fresh agent session to prevent customer context leaking between files.

Without Gnani credentials, test the text path instead:

```powershell
python run.py --text-file sample_text_test.txt --out-dir outputs_text
```

## Evaluation and tests

Run the supplied dataset's integrity validator from the dataset folder:

```powershell
python validate_dataset.py
```

Run the retrieval evaluation (52 questions, `asr_text` when provided):

```powershell
python evaluate.py --top-k 5 --out-dir evaluation
```

Run automated tests:

```powershell
python -m unittest discover -s tests -v
```

### Retrieval results measured in this workspace

- Questions: **52**; answerable: **47**; unsupported: **5**.
- Gold evidence hit@5 on answerable questions: **36/47 = 76.6%**.
- Mean reciprocal rank on answerable questions: **0.4989**.
- Automated tests: **7 passed**.

These are retrieval-only metrics. They do **not** measure generated-answer correctness, the Step 1 prompt-only baseline, refusal quality, all 96 conversation turns, or voice quality. Use `evaluation/retrieval_results.csv` to inspect misses. Do not present retrieval hit rate as answer accuracy.

## Required final checks before submission

- [ ] Run and review all 52 practice questions for Step 1 prompt-only vs Step 2 RAG answer quality; report actual measured scores.
- [ ] Evaluate the 23 supplied multi-turn conversations, including expected tool calls and verification gates.
- [ ] Add your own Gnani API key locally and complete at least one recorded-voice end-to-end test. Gnani is the only permitted STT/TTS provider.
- [ ] Record a demo video of at most 2 minutes showing a grounded answer, follow-up, and a handover or abstention.
- [ ] Publish this code to a public Git repository and add its URL here before packaging.
- [ ] Include the completed report PDF and demo video in the final ZIP.
- [ ] Never include `.env`, API keys, `.venv`, the dataset copy, or real customer data.

## Submission structure

The submission ZIP should contain this project code, `.env.example`, `requirements.txt`, `run.py`, `src/`, evaluation artifacts, tests, `report.pdf`, and `demo.mp4` once you create the final report/demo. It must not contain a dataset copy or secrets.

## Data and policy notes

- Reference date: **20 October 2026**.
- Business days: Monday–Saturday, excluding dates in `holidays.csv`; return windows use calendar days.
- IDs and pincodes are strings in the source data.
- The supplied order tool is a synthetic educational mock, not production-grade authentication.
- Voice audio is not included in the dataset; use your own voice only, and do not record other people without written consent.
