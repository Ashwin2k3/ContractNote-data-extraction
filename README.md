# PDF Table Extractor API

This FastAPI application processes PDF files containing trade data and extracts the information into a CSV file.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the FastAPI server:
```bash
uvicorn app:app --reload
```

The server will start at `http://localhost:8000`

## API Endpoints

### POST /process-pdfs/
Upload and process multiple PDF files.

**Request:**
- Method: POST
- Endpoint: `/process-pdfs/`
- Content-Type: multipart/form-data
- Body: Multiple PDF files

**Response:**
```json
{
    "message": "Successfully processed X PDFs",
    "total_trades": Y,
    "output_file": "trades_data.csv"
}
```

### GET /
Welcome endpoint that provides basic information about the API.

## Usage Example

You can use tools like curl or Postman to interact with the API. Here's an example using curl:

```bash
curl -X POST "http://localhost:8000/process-pdfs/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "files=@file1.pdf" \
     -F "files=@file2.pdf"
```

The processed data will be saved in a CSV file named `trades_data.csv` in the current directory. 