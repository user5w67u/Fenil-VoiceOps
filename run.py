"""Batch audio runner required by the VoiceOps capstone."""
import argparse, json, os, sys, traceback
from pathlib import Path
from src.config import DATASET_DIR, GNANI_API_KEY
from src.retrieval import Retriever
from src.agent import SupportAgent

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--audio-dir",default="sample_audio",help="Folder of customer audio files (not needed with --text-file)")
    p.add_argument("--out-dir",default="outputs",help="Output folder for transcripts, replies and traces")
    p.add_argument("--text-file",help="Optional text input file for testing without audio")
    args=p.parse_args()
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    kb=DATASET_DIR/"kb"
    if not kb.exists(): raise SystemExit(f"Knowledge base not found: {kb}. Set DATASET_DIR in .env.")
    agent=SupportAgent(Retriever(kb))
    if args.text_file:
        lines=Path(args.text_file).read_text(encoding="utf-8").splitlines()
        for idx,line in enumerate(lines,1):
            if not line.strip(): continue
            result=agent.respond(line)
            (out/f"turn_{idx:03}.json").write_text(json.dumps({"input_text":line,**result},ensure_ascii=False,indent=2),encoding="utf-8")
        print(f"Saved text test outputs to {out.resolve()}"); return
    if not GNANI_API_KEY: raise SystemExit("Set GNANI_API_KEY in .env before audio mode.")
    os.environ["GNANI_API_KEY"]=GNANI_API_KEY
    try:
        from gnani.stt import GnaniSTTClient
        from gnani.tts import GnaniTTSClient
    except ImportError: raise SystemExit("Install Gnani SDK: pip install gnani-vachana")
    stt=GnaniSTTClient(); tts=GnaniTTSClient()
    audio_dir=Path(args.audio_dir)
    audios=sorted([x for x in audio_dir.iterdir() if x.suffix.lower() in {".wav",".mp3",".m4a",".flac",".ogg"}])
    if not audios: raise SystemExit(f"No supported audio files found in {audio_dir}")
    manifest=[]
    for idx,audio in enumerate(audios,1):
        try:
            # Each file is treated as an independent test call to avoid cross-customer context leakage.
            agent.reset()
            heard=stt.transcribe(str(audio),language_code="en-IN")["transcript"]
            result=agent.respond(heard)
            reply_file=out/f"{audio.stem}_reply.wav"
            tts.synthesize(result["answer"],voice="Kaveri",model="timbre-v2.5",language="en-IN",output_file=str(reply_file))
            record={"audio_file":audio.name,"transcript":heard,**result,"reply_audio":reply_file.name}
            (out/f"{audio.stem}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
            manifest.append(record); print(f"[{idx}/{len(audios)}] {audio.name}: OK")
        except Exception as e:
            record={"audio_file":audio.name,"error":f"{type(e).__name__}: {e}"}
            (out/f"{audio.stem}.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
            manifest.append(record); print(f"[{idx}/{len(audios)}] {audio.name}: FAILED")
    (out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Completed. Outputs: {out.resolve()}")
if __name__=="__main__": main()
