# gen-report-svc

## How to Run

### Create a virtual environment

 macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv env
.\env\Scripts\activate
```

### Install the requirements

```bash
pip install -r requirements.txt
```

## Run locally

```bash
fastapi run main.py
```


## Deploy Docker

### Update the requirements

```bash
pip install pipreqs
pipreqs --force --ignore bin,etc,include,lib,lib64
```

### Generate docker

```bash
docker build -t gen-report-svc .
```

### Run the Docker container

```bash
docker run -d -p 8000:8000 gen-report-svc
```

