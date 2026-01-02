import streamlit as st, requests, json

st.title("☠️ Free-Monster Chat")
if "msgs" not in st.session_state:
    st.session_state.msgs = []

for m in st.session_state.msgs:
    st.chat_message(m["role"]).markdown(m["content"])

prompt = st.chat_input("talk")
if prompt:
    st.session_state.msgs.append({"role":"user","content":prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        text = ""
        r = requests.post(
            "https://tiny-lab-eef2.tiwarinaren.workers.dev/chat",
            json={"messages": st.session_state.msgs, "stream": True},
            headers={"Content-Type": "application/json"},
            stream=True,
        )
        for line in r.iter_lines():
            if line:
                token = json.loads(line)["response"]
                text += token
                placeholder.markdown(text + "▌")
        placeholder.markdown(text)
    st.session_state.msgs.append({"role":"assistant","content":text})
