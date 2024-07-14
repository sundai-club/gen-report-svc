
# pip install langchain
# pip install --quiet openai python-dotenv
# pip install --upgrade --quiet  docx2txt


import os
import openai
import sys
from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI


sys.path.append('../..')

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']

class Nest(BaseModel):
    Content = 'Content'
    Reasoning = 'Reasoning'

class Document(BaseModel):
    Title: Nest
    Introduction: Nest
    Methods: Nest
    Results: Nest
    Discussion: Nest

parser = JsonOutputParser(pydantic_object=Document)

def load_doc(file_path):
    # "grant.docx"
    loader = Docx2txtLoader(file_path)
    docs = loader.load()

    return docs

def llm_chain_input_json(path):
    docs = load_doc(path)

    prompt_template = """
        Your job is summarize the above provided file in the text delimited by triple backquotes.
        ```{text}```
        Return your response in bullet points which covers the key points of the text.
        Arrange your response under following sections:
        TITLE : CONTENT, REASONING
        INTRODUCTION : CONTENT, REASONING
        METHODS : CONTENT, REASONING
        RESULTS : CONTENT, REASONING
        DISCUSSION : CONTENT, REASONING

        Format instructions:
        {format_instructions}

        """
    
    prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106")
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)

    summary_result = chain.run(docs)

    result_json = chain.run(docs)


    return result_json




