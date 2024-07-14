

import base64
import requests

import matplotlib.pyplot as plt
import json
import os


# Function to plot and save a graph from a json object
def plot_graph(graph):
  # Create the directory if it doesn't exist
  output_directory = 'sample_output/images/'
  if not os.path.exists(output_directory):
    os.makedirs(output_directory)

  title = graph['title'].replace(' ', '_')

  if graph['graph_type'] == 'bar chart':
    for dataset in graph['data']:
        plt.figure(figsize=(10, 6))
        plt.bar(graph['options']['xaxis']['categories'], dataset['data'], label=dataset['name'])
        plt.title(graph['title'])
        plt.xlabel('Categories')
        plt.ylabel('Values')
        plt.legend()
        plt.savefig(f"{output_directory}{title}.png")
        plt.close()
  elif graph['graph_type'] == 'line chart':
    for dataset in graph['data']:
        plt.figure(figsize=(10, 6))
        plt.plot(graph['options']['xaxis']['categories'], dataset['data'], label=dataset['name'])
        plt.title(graph['title'])
        plt.xlabel('Categories')
        plt.ylabel('Values')
        plt.legend()
        plt.savefig(f"{output_directory}{title}.png")
        plt.close()
  elif graph['graph_type'] == 'pie chart':
    for dataset in graph['data']:
        plt.figure(figsize=(8, 8))
        plt.pie(dataset['series'], labels=dataset['labels'], autopct='%1.1f%%')
        plt.title(graph['title'])
        plt.savefig(f"{output_directory}{graph['title'].replace(' ', '_')}.png")
        plt.close()

  return f"{output_directory}{title}.png"




def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')



def generate_graph_description(image_path,api_key):

  # Getting the base64 string
  base64_image = encode_image(image_path)

  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }

  payload = {
    "model": "gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Provide a description for this graph (what is its purpose, and what does it tell us). Only output the description."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          }
        ]
      }
    ],
    "max_tokens": 300
  }
  
  

  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

  print(response.json())
  # Extract the content from the response JSON
  content = response.json()["choices"][0]["message"]["content"]
  # Print the content
  print(content)
  return content



def append_json_object_to_file(json_object, file_path):
  """
  Appends a json object to a json file that has a list of json objects.

  Args:
      json_object: The json object to append.
      file_path: The path to the json file.
  """

  # Check if the file exists
  try:
    with open(file_path, "r") as f:
      data = json.load(f)
  except FileNotFoundError:
    data = {"graphs": []}

  # Append the new json object to the list
  data["graphs"].append(json_object)

  # Save the json file
  with open(file_path, "w") as f:
    json.dump(data, f, indent=4)
    
    
def analyse_dashboard_json(path,overwrite=False,output='sample_output/graphs_analysed.json'):
    api_key = os.environ["OPENAI_API_KEY"]

        
    #assert os.path.exists(path)

    if overwrite or not os.path.exists(output):
        with open(path) as f:
            dashboard_data = json.load(f)
        
        graph_data = dashboard_data['graphs']
        for graph in graph_data:
            image_path = plot_graph(graph)
            title = graph['title']
            id = graph['id']
            dashboard_id = graph['dashboard_id']
            description = generate_graph_description(image_path,api_key)
            json_content = {
            "title": title,
            "id": id,
            "dashboard_id": dashboard_id,
            "description": description,
            "image_path": image_path
            }
            append_json_object_to_file(json_content, output)
            
            
            
def describe_json_structure(json_obj, indent=0):
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            print('  ' * indent + f"Key: {key} (Type: {type(value).__name__})")
            describe_json_structure(value, indent + 1)
    elif isinstance(json_obj, list):
        print('  ' * indent + f"List of {len(json_obj)} items (Type: list)")
        if len(json_obj) > 0:
            print('  ' * (indent + 1) + f"Item type: {type(json_obj[0]).__name__}")
            describe_json_structure(json_obj[0], indent + 2)
    else:
        print('  ' * indent + f"Value: {json_obj} (Type: {type(json_obj).__name__})")





def generate_json_outline(json_obj, indent=0):
    outline = ""
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            outline += '  ' * indent + f'"{key}": '
            if isinstance(value, dict):
                outline += '{\n'
                outline += generate_json_outline(value, indent + 1)
                outline += '  ' * indent + '},\n'
            elif isinstance(value, list):
                outline += '[\n'
                if len(value) > 0 and isinstance(value[0], (dict, list)):
                    outline += generate_json_outline(value[0], indent + 1)
                else:
                    outline += '  ' * (indent + 1) + '"item",\n'
                outline += '  ' * indent + '],\n'
            else:
                outline += f'"{type(value).__name__}",\n'
    elif isinstance(json_obj, list):
        for item in json_obj:
            outline += '  ' * indent + '[\n'
            outline += generate_json_outline(item, indent + 1)
            outline += '  ' * indent + '],\n'
    return outline
