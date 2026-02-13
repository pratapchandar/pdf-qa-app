import streamlit as st
import os
import tempfile
from openai import OpenAI
import PyPDF2

st.set_page_config(page_title="PDF Q&A Assistant", page_icon="📄")
st.title("📄 PDF Question & Answer Assistant")

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except:
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("Please configure your OpenAI API key")
    st.stop()

client = OpenAI(api_key=api_key)

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def answer_question(context, question):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based on the provided document content. Only answer based on the document. If the answer is not in the document, say I could not find this information in the document."
            },
            {
                "role": "user",
                "content": f"Document content: {context} Question: {question} Please answer based only on the document content above."
            }
        ],
        temperature=0
    )
    return response.choices[0].message.content

uploaded_file = st.file_uploader("Upload your PDF document", type="pdf")

if uploaded_file:
    with st.spinner("Reading your PDF..."):
        try:
            pdf_text = extract_text_from_pdf(uploaded_file)
            
            if not pdf_text.strip():
                st.error("Could not extract text from PDF.")
                st.stop()
            
            st.success("PDF processed successfully!")
            
            word_count = len(pdf_text.split())
            st.info(f"Document contains approximately {word_count} words")
            
            with st.expander("Preview document content"):
                st.write(pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text)
            
            st.write("### Ask a question about your document:")
            question = st.text_input("Your question:", placeholder="e.g. What is this document about?")
            
            if question:
                with st.spinner("Finding answer..."):
                    try:
                        answer = answer_question(pdf_text, question)
                        st.write("### Answer:")
                        st.write(answer)
                    except Exception as e:
                        st.error(f"Error getting answer: {e}")
                        
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
else:
    st.info("Please upload a PDF document to get started")
    st.write("### How to use:")
    st.write("1. Upload a PDF document using the button above")
    st.write("2. Wait for the document to be processed")
    st.write("3. Type your question in the text box")
    st.write("4. Get answers based on your document!")