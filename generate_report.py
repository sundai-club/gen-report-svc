import json
import requests
import os

from load_input import llm_chain_input_json

def read_json_file(file_path):
  try:
    with open(file_path, 'r') as file:
      data = json.load(file)
    return data
  except FileNotFoundError:
    print(f"File not found: {file_path}")
  except json.JSONDecodeError:
    print(f"Error decoding JSON file: {file_path}")
  except Exception as e:
    print(f"Error reading file: {e}")

def download_public_s3_file(s3_url, local_file_path):
    try:
        # Send a GET request to the S3 URL
        response = requests.get(s3_url)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Create the tmp folder if it doesn't exist
        if not os.path.exists('tmp'):
          os.makedirs('tmp')
        
        # Write the content to a local file
        with open('tmp/'+local_file_path, 'wb') as file:
            file.write(response.content)
        
        print(f"File downloaded successfully: {local_file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")

def trigger_report(report_url, data_url):
    download_public_s3_file(report_url, "report.docx")
    download_public_s3_file(data_url, "data.xlsx")
    
    return llm_chain_input_json("tmp/report.docx")
    