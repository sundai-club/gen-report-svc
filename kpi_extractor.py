import glob
import json 
from dotenv import load_dotenv

from openai import OpenAI

from langchain_community.document_loaders import Docx2txtLoader


from kpi_extractor_tools import *

# Load API keys from .env.local file
load_dotenv('.env.local')  # or alternatively, use os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


def test_api_key():
    client = OpenAI()

    stream = client.chat.completions.create(
        model="gpt-4o",
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

    You must make sure that ALL graphs listed are added to one or more KPI or added into a separate category called 'discarded' in the output. No graphs should be left unaccounted for. Minimize discards.

    Output only the final json object, nothing else.

    """
    
    
def caption_prompt(KPI, graphs):
  return f"""
    You are an expert in writing grant applications. 
    In your grant progress report you need to provide evidence of having met key performance indicators that had
    been devised for the grant. 
    Please provide a caption for a figure that shows how the current KPI had been met. 

    Here is the KPI: {KPI}. 

    Here is the description of the graphs that describe how the KPI had been met.
    {graphs}
    Please generate a short caption that summarizes all these graphs. 
    Please refer to each graph separately in one short sentence. 
    Please do not mention reference to ID at all. 
    Please do not start the caption with 'Caption:'. 

    """
    
def caption_prompt_2(KPI, graphs):
  return f"""
    You are an expert in writing grant applications. 
    In your grant progress report you need to provide evidence of having met key performance indicators that had
    been devised for the grant. 
    Please provide a caption for a figure that shows how the current KPI had been met. 

    Here is the KPI: {KPI}. 

    Here is the description of the graphs that describe how the KPI had been met.
    {graphs}
    Please generate a short caption that summarizes all these graphs. 
    Please refer to each graph separately in one short sentence. 
    Please do not mention reference to ID at all. 
    Please do not start the caption with 'Caption:'. 

    """

# Function to get response from the model
def get_response(client, messages,model="gpt-4o",verbose=False):
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

def generate_captions(response_prev,messages):
    figure_captions = {}
    for figure_id,key in enumerate(response_prev['KPIs'].keys()):
        kpi = response_prev['KPIs'][key]
        KPI = kpi['description']
        graphs = [i[1] for i in kpi['dashboard_ids']]

        next_prompt = caption_prompt(KPI, graphs)

        # Append the previous output to the messages
        messages.append({"role": "user", "content": next_prompt})

        response = get_response(client, messages)

        messages.append({"role": "assistant", "content": response})
        
        figure_captions[key] = response
        
    return figure_captions


def kpi_pipeline(docs_path, dashboard_json):
    test_api_key()
    # docs_path = 'sample_input/grant.docx'
    docs = glob.glob(docs_path)
    assert docs
    
    # load document
    loader = Docx2txtLoader(docs[0])
    data = loader.load()
    document = str(data[0])
    
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
    graphs_analysed = "sample_output/" + dashboard_json + "_analysed.json"
    graphs_json = analyse_dashboard_json(dashboard_json,False,graphs_analysed)
    # print("\n\n\nHERE!!!!!")
    # print(graphs_json)
    # graphs_analysed='sample_output/graphs_analysed.json'
    # with open(graphs_analysed, 'r') as file:
    #     graphs_json = json.load(file)

    # Create a mapping from dashboard_id to image_path
    dashboard_id_to_image_path = {graph["id"]: graph["image_path"] for graph in graphs_json["graphs"]}
    print(dashboard_id_to_image_path)
    dashboard_id_to_description = {graph["id"]: graph["description"] for graph in graphs_json["graphs"]}
    dashboard_id_to_title = {graph["id"]: graph["title"] for graph in graphs_json["graphs"]}
        
    # some helper conversions 
    import json        
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
    # And add to a new json object called kpi_data_final which has the caption, the merged image path, the KPI description, and the dashboard_ids
    kpi_data_final = {}
    for kpi, details in kpi_data["KPIs"].items():

        if 'kpi' == 'discarded' or isinstance(details, list):
            continue
            #from IPython import embed; embed()
        # from IPython import embed; embed()
        image_paths = [dashboard_id_to_image_path[int(item[0])] for item in details["dashboard_ids"]]
        output_path = f"merged_images/{kpi}.png"
        merge_images_in_grid(image_paths, output_path)
        print(f"Merged images for {kpi} saved to {output_path}")
        # TO INSERT: CALL SERGE'S FUNCTION TO GET CAPTION
        graph_descriptions = [
            f"{dashboard_id_to_title[int(item[0])]}: {dashboard_id_to_description[int(item[0])]}"
            for item in details["dashboard_ids"]
        ]
        graph_descriptions_str = "\n".join(graph_descriptions)
        caption = get_response(client, [{"role": "user", "content": caption_prompt_2(details["description"], graph_descriptions_str)}])
        # Save the merged image to Vercel Storage
        from vercel_storage import blob
        with open(output_path, 'rb') as fp:
            resp = blob.put(
                pathname=output_path,
                body=fp.read(),
                options={"no_suffix": True}
            )
        ############################
        img_url = resp['url']
        print(f"Image URL: {img_url}")
        kpi_data_final[kpi] = {
            "caption": caption,
            "image_path": img_url,
            "description": details["description"],
            "dashboard_ids": details["dashboard_ids"]
        }

    return kpi_data_final
    
if __name__=='__main__':

    print(kpi_pipeline('sample_input/grant.docx', "sample_input/dashboard.json"))
    
        
    
    

    
    




    

    
    
    
    
    
    