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
            timeout=30,  # Add timeout to prevent hanging
        )

        # The worker returns a JSON array, not streaming
        try:
            response_data = r.json()
            # Assuming the response is an array with the last item being the chat response
            if isinstance(response_data, list) and len(response_data) > 0:
                # Get the last response (chat style)
                chat_response = response_data[-1]
                if "response" in chat_response:
                    text = chat_response["response"]
                    placeholder.markdown(text)
                else:
                    st.error("Error: Unexpected response format from API")
                    st.stop()
            else:
                st.error("Error: Invalid response from API")
                st.stop()
        except json.JSONDecodeError as e:
            st.error(f"Error parsing API response: {e}")
            st.stop()
        except Exception as e:
            st.error(f"API request failed: {e}")
            st.stop()
        placeholder.markdown(text)
    st.session_state.msgs.append({"role":"assistant","content":text})
