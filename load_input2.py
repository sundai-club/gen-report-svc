
import os
import openai
import sys


from langchain_community.document_loaders import Docx2txtLoader

from openai import OpenAI
import os
import json

import sys

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file


import json

sys.path.append('../..')

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']



sys.path.append('../..')


def llm_chain_input_json(path = "grant.docx"):

    prompt_gpt_new = """ 

    You are a data analyst for this company writing an introduction for a paper that discusses the impact of the company.
    You job is to summarize the provided file.

    Write one line for TITLE 
    Write 4 paragraphs each of INTRODUCTION and METHODS

    Provide Reasoning for your response

    Please structure the introduction in four of the following paragraphs (do not use bullet points):
    
    Paragraph 1: Company Overview
    Data pulled from context data
    1-3 sentences to briefly introduce the company, including its name, industry, and key products or services.
    1-3 sentences to mention the company’s mission, vision, and core values
    
    Paragraph 2: Purpose of the Report
    1 sentence to clearly state the purpose of the impact report.
    1-3 sentences include relevant historical or recent developments with the company
    1-3 sentences highlighting the key objectives of the report.
    1 sentence on specify the time period covered by the report.
    
    Paragraph 3: Key Areas of Focus
    
    1-3 sentences to discuss in specific detail the results of the report such as financial performance, market trends, or what ever is relevant in the context data
    1-3 sentences on any notable achievements or areas of concern as more of future directions.
    
    Paragraph 4: Conclusion and future directions
    
    1-3 sentences to discuss the conclusions
    1-3 sentences on future directions


    Please structure the methods section in the following paragraphs (do not use bullet points):
    Paragraph 1: Data Collection
    1-3 sentences to describe the sources of data used in the report, including any specific documents, databases, or tools (e.g., globalgrant.docx and dashboard.json). 
    1-3 sentences to explain the time period during which the data was collected. 
    1-3 sentences to describe the process of data collection, including any specific methods or techniques used to gather the data.
    Paragraph 2: Data Processing
    1-3 sentences to describe the methods used to process and clean the collected data. 
    1-3 sentences to mention any software or tools used for data processing (e.g., Excel, Python). 
    1-3 sentences to explain how the data was organized and prepared for analysis.
    Paragraph 3: Data Analysis
    1-3 sentences to describe the analytical methods used to interpret the data. 
    1-3 sentences to explain any statistical tests, models, or algorithms applied to the data. 
    1-3 sentences to discuss any tools or software used for data analysis (e.g., HeronAI for dashboard analysis).


    Arrange your response under sections as TITLE, INTRODUCTION, METHODS 
    in a json file format as follows:
    {
        "Title":{"Content":TITLE, "Reasoning":""},
        "Introduction":{"Content":INTRODUCTION, "Reasoning":""},
        "Methods":{"Content":METHODS, "Reasoning":""}
    }

    do not make any other keys in the json file. 

    where 'reasoning' as to why the you are classifiying the sentences as TITLE, INTRODUCTION, METHODS.

    You must write the output as you outlined above.

    """

    loader = Docx2txtLoader(path)
    docs = loader.load()

    client = OpenAI()

    def get_completion(prompt, client, model="gpt-4o"): # Andrew mentioned that the prompt/ completion paradigm is preferable for this class
        messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content":  str(docs[0])}
        ]
        
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream = True,
            response_format={"type": "json_object"},
            temperature=0, # this is the degree of randomness of the model's output
        )

        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
        return response 
       
    response = get_completion(prompt_gpt_new,client)
    content = json.loads(response)

    return content

    # file_path = "check1.json"

    # # Write the data to the JSON file
    # with open(file_path, "w") as f:
    #     json.dump(content, f, indent=4)
