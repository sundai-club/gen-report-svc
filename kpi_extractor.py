
import json
import glob

from dotenv import load_dotenv

from openai import OpenAI

from langchain_community.document_loaders import Docx2txtLoader


from kpi_extractor_tools import *

# Load API keys from .env.local file
load_dotenv('.env.local')  # or alternatively, use os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


def test_api_key():
    client = OpenAI()

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say this is a test. The API worked."}],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
            
def system_prompt():

    return """
    You are a grant reviewer.
    Your job is to extract the proposed Key Performance Indicators (KPIs) from the grant data provided.
    You must output them in the following format as json file:
    {
        "KPIs": {
            "KPI1":{"description":""},
            "KPI2":{"description":""},
            ...
        }
    }

    Please justify your choices for KPIs from the provided grant data. You must limit the number of KPIs to minimum of 3 and maximum of 5.
    """


def kpi_to_graphs_prompt(graphs_json_str):
    return f"""
    Here is a list of graphs that had been produced by another datalist that describe the outcomes of the work done for this grant. 
    {graphs_json_str}

    For each KPI that you had identified above, you need to identify multiple graphs that describe the outcomes of the work done for this grant for that KPI.

    You must update your list in the following json structure:
    {{
        "KPIs": {{
            "KPI1": {{"description":"", "dashboard_ids":[["dashboard_id", "reasoning"],["dashboard_id", "reasoning"],...]}},
            "KPI2": {{"description":"", "dashboard_ids":[["dashboard_id", "reasoning"],["dashboard_id", "reasoning"],...]}},
            ...
        }}
    }}

    where 'reasoning' as to why the particular set of graphs, based on their description, should be included in the list of this KPI.


    You must write the KPI as you outlined above.

    You must use the dashboard_id from the list of graphs and its description. do not use PNGs in the original report 

    You must make sure that ALL graphs listed are added to a KPI or added into a separate category called 'discarded' in the output. No graphs should be left unaccounted for. Minimize discards.

    Output only the final json object, nothing else.

    """
    
    

# Function to get response from the model
def get_response(client, messages,model="gpt-3.5-turbo",verbose=False):
    stream = client.chat.completions.create(
        model=model,  # or gpt-4
        messages=messages,
        stream=True,
    )
    response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            response += chunk.choices[0].delta.content
            if verbose:
                print(chunk.choices[0].delta.content, end="")
    if verbose:
        print()  # For a new line after the complete response
    return response

    
if __name__=='__main__':
    test_api_key()
    
    docs = glob.glob('sample_input/grant.docx')
    assert docs
    
    # load document
    loader = Docx2txtLoader(docs[0])
    data = loader.load()
    document = str(data[0])
    # from IPython import embed; embed()
    
    # start client 
    client = OpenAI()
    

    # Create the initial message list with the system prompt
    messages = [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": document}
    ]    
    
    
    # get KPIs 
    response = get_response(client, messages, verbose=True)
    messages.append({"role": "assistant", "content": response})
    
    # analyse images 
    graphs_analysed='sample_output/graphs_analysed.json'
    analyse_dashboard_json(path="sample_input/dashboard.json",overwrite=False,output=graphs_analysed)

    with open(graphs_analysed, 'r') as file:
        graphs_json = json.load(file)

    # Create a mapping from dashboard_id to image_path
    dashboard_id_to_image_path = {graph["id"]: graph["image_path"] for graph in graphs_json["graphs"]}
    print(dashboard_id_to_image_path)
        
    # some helper conversions         
    graphs_json_str = json.dumps(graphs_json, indent=4)
    graphs_json_outline = "{\n" + generate_json_outline(graphs_json) + "}\n"
    
    # get next prompt 
    next_prompt = kpi_to_graphs_prompt(graphs_json_str)
    
    # match kpis to graphs 
    messages.append({"role": "user", "content": next_prompt})

    response = get_response(client, messages, verbose=True)
    

    # append final result
    messages.append({"role": "assistant", "content": response})

    # Save the final result as a json
    kpi_final_json_str = messages[-1]['content']
    import json
    import re
    from kpi_extractor_tools import merge_images_in_grid
    # Extract the JSON content using regular expressions
    json_match = re.search(r'\{.*\}', kpi_final_json_str, re.DOTALL)
    if json_match:
        kpi_final_json_str = json_match.group(0)

    kpi_data = json.loads(kpi_final_json_str)

    # Ensure the output directory exists
    output_dir = "merged_images"
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through each KPI and merge the relevant images
    # Also call Serge's function to get the caption
    # And add to a new json object called kpi_data_final which has the caption, the merged image path, the KPI description, and the dashboard_ids
    kpi_data_final = {}
    for kpi, details in kpi_data["KPIs"].items():
        image_paths = [dashboard_id_to_image_path[item[0]] for item in details["dashboard_ids"]]
        output_path = f"merged_images/{kpi}.png"
        merge_images_in_grid(image_paths, output_path)
        print(f"Merged images for {kpi} saved to {output_path}")
        # TO INSERT: CALL SERGE'S FUNCTION TO GET CAPTION
        caption = "DEFAULT CAPTION"

        kpi_data_final[kpi] = {
            "caption": caption,
            "image_path": output_path,
            "description": details["description"],
            "dashboard_ids": details["dashboard_ids"]
        }

    print(kpi_data_final)
        
    
    



    
    from IPython import embed; embed()
    
    

    
    




    

    
    
    
    
    
    