import streamlit as st
from src.config import DATASET_DIR
from src.retrieval import Retriever
from src.agent import SupportAgent

st.set_page_config(page_title="ZentroMart VoiceOps",page_icon="🎧",layout="wide")
st.title("🎧 ZentroMart | VoiceOps Support Agent")
st.caption("Grounded customer support · Retrieval-augmented answers · Verified order tools")
if "agent" not in st.session_state:
    kb=DATASET_DIR/"kb"
    if not kb.exists():
        st.error(f"Dataset not found at {DATASET_DIR}. Extract the supplied ZIP and set DATASET_DIR in .env.")
        st.stop()
    st.session_state.agent=SupportAgent(Retriever(kb))
if "messages" not in st.session_state: st.session_state.messages=[]
with st.sidebar:
    st.subheader("Session controls")
    st.write("Reference date: **20 October 2026**")
    st.write("Order data stays behind the supplied verification tool.")
    if st.button("New conversation"):
        st.session_state.agent.reset(); st.session_state.messages=[]; st.rerun()
    st.markdown("---")
    st.write("For voice batch testing, use `python run.py --audio-dir sample_audio --out-dir outputs`.")
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])
prompt=st.chat_input("Ask about delivery, returns, refunds, warranty, or an order…")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Checking company documents…"):
            result=st.session_state.agent.respond(prompt)
        st.markdown(result["answer"])
        with st.expander("Evidence & tool trace"):
            st.json({"sources":result["sources"],"actions":result["actions"]})
    st.session_state.messages.append({"role":"assistant","content":result["answer"]})
