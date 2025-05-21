import streamlit as st
from ask import ask

# ตั้งค่า Streamlit page
st.set_page_config(
    page_title="Cat Rheology RAG Assistant",
    page_icon="🐱",
    layout="centered"
)

st.title("Cat Rheology RAG Assistant")

question = st.text_input("Ask a question about cat rheology:", key="question_input")

submit_button = st.button("Get Answer")

if submit_button and question:
    with st.spinner('Retrieving information...'):
        response = ask(question)
    
    st.subheader("Answer:")
    st.write(response)
    
    with st.expander("Your question"):
        st.write(question)
    
elif submit_button and not question:
    st.warning("Please enter a question.")
