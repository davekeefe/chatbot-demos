"""
GPT-in-a-Box Streamlit App
This module defines a Streamlit app for interacting with different Large Language models.
"""

import os
import yaml
import streamlit as st

from deployment import GetDeployment
from response import GetResponse

def clear_chat_history():
    """
    Clears the chat history by resetting the session state messages.
    """
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}
    ]


def add_message(chatmessage):
    """
    Adds a message to the chat history.
    Parameters:
    - chatmessage (dict): A dictionary containing role ("assistant" or "user")
                      and content of the message.
    """

    if chatmessage["role"] == "assistant":
        avatar = assistant_avatar
    else:
        avatar = user_avatar

    if llm_mode == "code":
        with st.chat_message(chatmessage["role"], avatar=avatar):
            st.code(chatmessage["content"], language="python")
    else:
        with st.chat_message(chatmessage["role"], avatar=avatar):
            st.write(chatmessage["content"])


# Generate a new response if last message is not from assistant
def add_assistant_response():
    """
    Adds the assistant's response to the chat history and displays
    it to the user.

    """
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar=assistant_avatar):
            with st.spinner("Thinking..."):
                if llm_history == "on":
                    response = chat_response.generate_chat_response(prompt)
                else:
                    response = chat_response.generate_response(prompt)
                if not response:
                    st.markdown(
                        "<p style='color:red'>Inference backend is unavailable. "
                        "Please verify if the inference server is running</p>",
                        unsafe_allow_html=True,
                    )
                    return
                if llm_mode == "code":
                    st.code(response, language="python")
                else:
                    st.write(response)
        chatmessage = {"role": "assistant", "content": response}
        st.session_state.messages.append(chatmessage)


with open('config.yaml', 'r') as f:
    configs = f.read()

language_models = yaml.load(configs, yaml.FullLoader)['language_models']
configuration = yaml.load(configs, yaml.FullLoader)

avialable_models = []

# Add supported models to the list
for k, v in language_models.items():
    if isinstance(v, dict):
        avialable_models.append(k)

if not os.path.exists(configuration['image_attribrutes']['assistant_svg']):
    assistant_avatar = None
else:
    assistant_avatar = configuration['image_attribrutes']['assistant_svg']

if not os.path.exists(configuration['image_attribrutes']['user_svg']):
    user_avatar = None
else:
    user_avatar = configuration['image_attribrutes']['user_svg']

# App title
st.title(configuration['main_page_attributes']['title'])
st.subheader(configuration['main_page_attributes']['subheader'])

with st.sidebar:
    if os.path.exists(configuration['image_attribrutes']['logo_svg']):
        _, col2, _, _ = st.columns(4)
        with col2:
            st.image(configuration['image_attribrutes']['logo_svg'], width=150)

    st.title(configuration['sidebar_attributes']['title'])
    st.subheader(configuration['sidebar_attributes']['subheader'])
    st.markdown(configuration['sidebar_attributes']['markdown'])

    st.subheader("Models")
    selected_model = st.sidebar.selectbox(
        "Choose a model", avialable_models, key="selected_model"
    )
    deployment_name = language_models[selected_model]['deployment']
    llm_mode = configuration['language_models'][selected_model]['llm_mode']
    llm_history = configuration['language_models'][selected_model]['llm_history']
    st.markdown(configuration['language_models'][selected_model]['description'])

    if "model" in st.session_state and st.session_state["model"] != selected_model:
        clear_chat_history()

    st.session_state["model"] = selected_model

deployment_args = {'deployment_name': deployment_name}
deployment_config = GetDeployment(deployment_args)
deployment_config.get_deployment_name()

chat_config = {"ingress_host": deployment_config.ingress_host, 
               "ingress_port": deployment_config.ingress_port, 
               "service_hostname": deployment_config.service_hostname, 
               "selected_model": selected_model}

chat_response = GetResponse(chat_config)

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}
    ]

# Display or clear chat messages
for message in st.session_state.messages:
    add_message(message)

st.sidebar.button("Clear Chat History", on_click=clear_chat_history)

# User-provided prompt
if prompt := st.chat_input("Ask your query"):
    message = {"role": "user", "content": prompt}
    st.session_state.messages.append(message)
    add_message(message)

add_assistant_response()
