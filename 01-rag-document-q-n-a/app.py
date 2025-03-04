import os
from dotenv import load_dotenv
import streamlit as st
import streamlit_antd_components as sac
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import openai
from langchain.callbacks import get_openai_callback
from langchain.chains.question_answering import load_qa_chain


api_key = os.getenv("OPENAI_API_KEY")


def main():
    load_dotenv()
    st.set_page_config(page_title="Load PDF for semantic search")
    st.header("PDF Q&A Bot")

    index = sac.tabs([
        sac.TabsItem(label="Read PDF File", icon="file-earmark-pdf"),
        sac.TabsItem(label="Load Vector Store", icon="file-earmark-text")
    ], align='center', size='xl', variant='outline', use_container_width=True, return_index=True)

    if index == 0:
        upload_pdf()
    else:
        load_vector_store()

def upload_pdf():
    pdf = st.file_uploader("load PDF file", type="pdf")

    text = ""

    # read the pdf file page by page and extract the text
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()

    # split the text into chunks
    if len(text) > 0:
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        st.write(chunks)

        # create the embeddings and save it to a local vector store file
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_texts(chunks, embeddings)
        vector_store.save_local("faiss_doc_idx")
    
def load_vector_store():
    embeddings = OpenAIEmbeddings()
    
    vector_store = FAISS.load_local("faiss_doc_idx", embeddings, allow_dangerous_deserialization=True)

    question_sem_search = st.text_input("Ask a question from vector store?")
    if question_sem_search != None:
        docs = vector_store.similarity_search(question_sem_search)




if __name__ == "__main__":
    main()
