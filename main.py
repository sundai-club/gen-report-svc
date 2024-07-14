from fastapi import FastAPI

from generate_report import trigger_report

app = FastAPI()

@app.get("/")
def read_root():
  return {"Welcome": "Report Generation Service"}

@app.post("/generate_report")
def generate_report(report_url: str, data_url: str):
  # Process the report and data URLs
  # Generate the report
  # Return the generated report
  return trigger_report(report_url, data_url)


