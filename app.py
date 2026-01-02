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
            if r.status_code != 200:
                st.error(f"API request failed with status {r.status_code}: {r.text}")
                st.stop()

            response_data = r.json()

            # Check if response contains an error
            if "error" in response_data:
                st.error(f"API Error: {response_data['error']}")
                st.stop()

            # Handle single response object
            if "response" in response_data:
                response_content = response_data["response"]

                # Handle different response formats
                if isinstance(response_content, str):
                    # Clean the text - remove any JSON formatting if present
                    text = response_content.strip()
                    if text.startswith('{') and text.endswith('}'):
                        # If it looks like JSON, try to extract just the message
                        try:
                            parsed = json.loads(text)
                            if "response" in parsed:
                                text = parsed["response"]
                            elif "message" in parsed:
                                text = parsed["message"]
                            else:
                                text = str(parsed)
                        except:
                            pass  # Keep original text if parsing fails
                    placeholder.markdown(text)
                elif isinstance(response_content, dict):
                    # If response is a dict, look for the actual message
                    if "response" in response_content:
                        text = str(response_content["response"])
                    elif "message" in response_content:
                        text = str(response_content["message"])
                    else:
                        text = str(response_content)
                    placeholder.markdown(text)
                else:
                    placeholder.markdown(str(response_content))
            else:
                st.error("Error: Unexpected response format from API")
                st.stop()

        except requests.exceptions.Timeout:
            st.error("API request timed out. Please try again.")
            st.stop()
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to API. Please check your internet connection.")
            st.stop()
        except json.JSONDecodeError as e:
            st.error(f"Error parsing API response: {e}")
            st.stop()
        except Exception as e:
            # Check if the response contains an error message
            try:
                error_data = r.json()
                if "error" in error_data:
                    st.error(f"API Error: {error_data['error']}")
                else:
                    st.error(f"Unexpected error: {e}")
            except:
                st.error(f"Unexpected error: {e}")
            st.stop()
    st.session_state.msgs.append({"role":"assistant","content":text})
