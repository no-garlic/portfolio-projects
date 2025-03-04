"""
PDF Question & Answer Application

This Streamlit application allows users to:

1. Upload a PDF document
2. Extract and process text from the PDF
3. Create vector embeddings of text chunks using OpenAI embeddings
4. Perform semantic search on the document content
5. Ask questions about the document content and receive AI-generated answers
"""
import os
import streamlit as st
import streamlit_antd_components as sac
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains.question_answering import load_qa_chain


class PdfSearchRagApp:
    def __init__(self):
        """Initialize the PDF Search RAG Application."""
        pass

    def streamlit_main(self, subpage=False):
        """
        Main function to run the Streamlit app.
        """
        # load environment variables and get the OpenAI API key
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")

        # set the page title and header unless this is a subpage
        if not subpage:
            st.set_page_config(page_title="Load PDF for semantic search")
            st.header("PDF Questions & Answer Bot")

        # create a file uploader for PDF files
        pdf = st.file_uploader("load PDF file", type="pdf")

        # initialize an empty string to hold the extracted text
        text = ""

        # clear the session state if the PDF file is cleared
        if pdf is None:
            st.session_state.clear()

        # if a PDF file is uploaded, read and extract text from it
        if pdf is not None:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()

        # if text is not empty, split it into chunks and create a vector store
        if len(text) > 0:
            text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_text(text)

            # create the embeddings and save it to a local vector store file
            embeddings = OpenAIEmbeddings()
            st.session_state.vector_store = FAISS.from_texts(chunks, embeddings)

        # if the vector store is available, allow users to ask questions
        if "vector_store" in st.session_state:
            # create a text input for asking questions
            question_text = st.text_input("Ask a question from vector store?")
            if len(question_text) > 0:
                # perform semantic search and generate an answer
                docs = st.session_state.vector_store.similarity_search(question_text)

                # load the QA chain and get the answer
                llm = OpenAI()
                chain = load_qa_chain(llm, chain_type="stuff")
                with get_openai_callback() as cb:
                    response = chain.run(input_documents=docs, question=chain)
                
                    # display the answer
                    st.write(response)


if __name__ == "__main__":
    app = PdfSearchRagApp()
    app.streamlit_main(subpage=False)
