import streamlit as st
import requests
import time
import json

BASE_URL = "http://localhost:8000"

st.title("Interact with the API")
st.write("Configure the model parameters and endpoint from the sidebar and send your message!")

# Sidebar configurations
st.sidebar.image("assets/thumbnail.png")
st.sidebar.title("zephyr-7b-alpha API demo")

# Endpoint selection
endpoints = ["zephyr/python", "zephyr/raw", "zephyr/system-message", "zephyr/structured-code-doc", "zephyr/code-doc", "zephyr/ws/gpu-stats"]
selected_endpoint = st.sidebar.selectbox("Choose Endpoint:", endpoints)

## Endpoint specific configurations
if selected_endpoint == "zephyr/system-message":
    system_message = st.sidebar.text_input("System Message:", value="You are a friendly chatbot who always responds in the style of a python developer that uses a combination of natural language and python to answer questions.")

# Global model configurations (applies to all endpoints)
max_new_tokens = st.sidebar.slider("Max New Tokens:", 50, 500, 256)
do_sample = st.sidebar.checkbox("Do Sample:", value=True)
temperature = st.sidebar.slider("Temperature:", 0.1, 1.0, 0.7, 0.1)
top_k = st.sidebar.slider("Top K:", 1, 100, 50)
top_p = st.sidebar.slider("Top P:", 0.1, 1.0, 0.95, 0.05)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):

    # Initialize response_data
    system_message = "Describe the code you receive in markdown format."
    # Construct the data dictionary based on the selected endpoint
    if selected_endpoint == "zephyr/python":
        data = {
            "user_message": prompt,
            "max_new_tokens": max_new_tokens,
            "do_sample": do_sample,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p
        }
    elif selected_endpoint == "zephyr/code-doc":
        data = {
            "code": prompt,
            "language": "python",
            "include_comments": True,
            "max_new_tokens": max_new_tokens,
            "do_sample": do_sample,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p
        }
    elif selected_endpoint == "zephyr/system-message" or selected_endpoint == "zephyr/structured-code-doc":
        data = {
            "user_message": prompt,
            "max_new_tokens": max_new_tokens,
            "do_sample": True,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "system_message": system_message  # Ensure system_message is defined
        }
    # Convert the data payload into a compact JSON string
    compact_json_payload = json.dumps(data)
    url = f"{BASE_URL}/{selected_endpoint}"

    # Send POST request to API
    response = requests.post(url, data=compact_json_payload)
    response_data = response.json()

    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = response_data["response"]
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.code(full_response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})


