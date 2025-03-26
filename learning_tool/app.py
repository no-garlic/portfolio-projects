import os
import streamlit as st
import streamlit_antd_components as sac
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
import re

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from llms import get_llm

system_message="""
Context:
You will assist me in learning some advanced features of C++.
I am a senior C++ programmer, with 20 years of experience, however I have little experience with the modern C++ features.
You can assume I have a strong understanding of C++ and the STL.

Your Role:
You will act as a tutor and technical writer, helping to provide me with written material to teach me how to use these C++ features.

Format:
For my request, format the output as an article with text description, and code examples.
Be thorough, cover all aspects of the feature, and write a long and detailed description with multiple code examples.
Your article should be enough to fully teach me about the feature.

Actions:
You will do nothing until I provide you with a topic to write about, if I have not provided you with a specific topic then you will ask me to provide you with that first.
"""

# https://github.com/streamlit/llm-examples/blob/main/Chatbot.py


class LearningToolApp():
    def __init__(self):
        """
        Initialize the Application.
        """
        # load environment variables and get the LLM keys
        load_dotenv()

        # get the LLM
        self.llm = get_llm()
        

    def streamlit_main(self, subpage=False):
        """
        Main function to run the Streamlit app.
        """
        # set the page title and header unless this is a subpage
        if not subpage:
            st.set_page_config(page_title="Learning Tool")
            st.header("Learning Tool")

        response_container = st.container()

        if user_input := st.chat_input():
            
            response_stream = self.llm.stream(
                [
                    SystemMessage(content=system_message),
                    HumanMessage(content=user_input),
                ]
            )
            with response_container:
                st.write_stream(response_stream)


if __name__ == "__main__":
    app = LearningToolApp()
    app.streamlit_main(subpage=False)
