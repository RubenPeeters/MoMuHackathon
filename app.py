# import chat
import streamlit as st
from streamlit_chat import message
import ollama
import base64
from chat import chat_llm_multilingual, chat_llm
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain.chat_models import ChatOllama
from langchain_core.messages import AIMessage
import pickle

import faiss
from uuid import uuid4
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

st.set_page_config(
    page_title="MoMu Chatbot",  
    page_icon="🤖",  
    layout="centered",  
    initial_sidebar_state="expanded" 
)

st.title("Welcome to MoMu Chatbot")
st.write("This is a chatbot powered by LLM and MoMu metadata.")
# st.sidebar.image("images\chatrobot.png", width=200, use_column_width=True)

page_bg_img = '''
<style>
.stApp {
    background-image: url("https://github.com/RubenPeeters/MoMuHackathon/blob/main/images/background_img.png?raw=true");
    background-size: 60%; 
    background-repeat: no-repeat; 
    background-position: left; 
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)



# Storing the chat
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

# Define a function to clear the input text
def clear_input_text():
    global input_text
    input_text = ""

# We will get the user's input by calling the get_text function
def get_text():
    global input_text
    input_text = st.text_input("Ask your Question", key="input", on_change=clear_input_text)
    return input_text

# def chat(user_input):


def main():
    llm = ChatOllama(model="llama3.2:1b", temperature=0)
    vec_path = "Data/vector_store"
    context_path = "Data/context.pkl"

    with open(context_path, 'rb') as f:
        context_dict = pickle.load(f)

    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    vector_store = FAISS.load_local(vec_path, embeddings, allow_dangerous_deserialization=True)

    user_input = get_text()

    progress_text = "Responsing..."
    my_bar = st.progress(0, text=progress_text)
    if user_input:
        # output = chat.answer(user_input)
        
        # response = ollama.chat(model="llama3.2:1b", messages=[{"role": "user", "content": user_input}])

        # output = response["message"]["content"]
        # output = chat_llm(llm, user_input, context_dict, vector_store)

        item_id = '16157'
        output = chat_llm_multilingual(llm, user_input, item_id, context_dict)

        # store the output 
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            # message(st.session_state["generated"][i], key=str(i))
            # message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(
                st.session_state["generated"][i],
                key=str(i),
                avatar_style="bottts"  
            )
           
            message(
                st.session_state['past'][i],
                is_user=True,
                key=str(i) + '_user',
                avatar_style="adventurer"  
            )
    my_bar.empty()
# Run the app
if __name__ == "__main__":
    main()

