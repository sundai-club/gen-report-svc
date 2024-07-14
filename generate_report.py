import boto3

def download_from_s3(bucket_name, s3_file_key, local_file_path):
  # Create an S3 client
  s3 = boto3.client('s3')

  try:
      # Download the file
      s3.download_file(bucket_name, s3_file_key, local_file_path)
      print(f"File downloaded successfully: {local_file_path}")
  except Exception as e:
      print(f"Error downloading file: {e}")

# Example usage
bucket_name = 'your-bucket-name'
s3_file_key = 'path/to/your/file.txt'
local_file_path = '/file.txt'

download_from_s3(bucket_name, s3_file_key, local_file_path)

def generate_report(proposal_pdf, data_csv):
  pdf_file = download_from_s3(bucket_name, proposal_pdf, '/tmp/proposal.pdf')
  csv_file = download_from_s3(bucket_name, data_csv, '/tmp/data.csv')
  url = 'this is the report'
  return url
  

  