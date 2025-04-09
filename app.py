from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import camelot
import pandas as pd
from pathlib import Path
import re
import os
import shutil
from typing import List
import tempfile

app = FastAPI(title="PDF Table Extractor API")

# Create a temporary directory for storing uploaded files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# def extract_tables_from_pdf(pdf_path):
#     # Use Camelot to extract tables
#     tables = camelot.read_pdf(str(pdf_path), pages='all', flavor='lattice')
#     return tables
def extract_tables_from_pdf(pdf_path):
    try:
        tables = camelot.read_pdf(str(pdf_path), pages='all', flavor='lattice')
        if tables.n == 0:
            raise ValueError("No tables found with lattice.")
    except Exception:
        tables = camelot.read_pdf(str(pdf_path), pages='all', flavor='stream')
    return tables



def process_table_data(tables, filename):
    all_rows = []
    
    # Define the expected columns
    columns = [
        "Order No.",
        "Order Time",
        "Trade No.",
        "Trade Time",
        "Security/Contract Description",
        "Buy (B) / Sell (S)",
        "Quantity",
        "Gross Rate/Trade Price Per unit (in foreign currency)",
        "Gross Rate/trade price per Unit (Rs)",
        "Brokerage per Unit (Rs)",
        "Net Rate per Unit (Rs)",
        "Closing Rate Per Unit(Rs)",
        "** Net Total (Before Levies)(Rs.)",
        "R e m a r k"
    ]
    
    for table in tables:
        # Get the DataFrame from the table
        df = table.df
        
        # Skip if the table is too small
        if len(df) < 2:
            continue
            
        # Process each row
        for _, row in df.iterrows():
            # Skip header rows
            if any(col in str(row[0]).upper() for col in ["ORDER", "TRADE", "SECURITY", "BUY", "SELL"]):
                continue
                
            # Create a dictionary for the row
            row_data = {
                "Order No.": row[0] if len(row) > 0 else "",
                "Order Time": row[1] if len(row) > 1 else "",
                "Trade No.": row[2] if len(row) > 2 else "",
                "Trade Time": row[3] if len(row) > 3 else "",
                "Security/Contract Description": row[4] if len(row) > 4 else "",
                "Buy (B) / Sell (S)": row[5] if len(row) > 5 else "",
                "Quantity": row[6] if len(row) > 6 else "",
                "Gross Rate/Trade Price Per unit (in foreign currency)": row[7] if len(row) > 7 else "",
                "Gross Rate/trade price per Unit (Rs)": row[8] if len(row) > 8 else "",
                "Brokerage per Unit (Rs)": row[9] if len(row) > 9 else "",
                "Net Rate per Unit (Rs)": row[10] if len(row) > 10 else "",
                "Closing Rate Per Unit(Rs)": row[11] if len(row) > 11 else "",
                "** Net Total (Before Levies)(Rs.)": row[12] if len(row) > 12 else "",
                "R e m a r k": row[13] if len(row) > 13 else "",
                "Source File": filename,
                "Date": filename.split()[0]  # Extract date from filename
            }
            
            # Only add rows that have meaningful data
            if any(str(value).strip() for value in row_data.values() if value != "Source File" and value != "Date"):
                all_rows.append(row_data)
    
    return all_rows

@app.post("/process-pdfs/")
async def process_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    all_trades = []
    
    # Process each uploaded file
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        
        # Save the uploaded file temporarily
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            # Extract tables from PDF
            tables = extract_tables_from_pdf(file_path)
            
            # Process the table data
            trades = process_table_data(tables, file.filename)
            all_trades.extend(trades)
            
            # Clean up the temporary file
            os.remove(file_path)
            
        except Exception as e:
            # Clean up the temporary file in case of error
            if file_path.exists():
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Error processing {file.filename}: {str(e)}")
    
    # Convert to DataFrame and save to CSV
    if all_trades:
        df = pd.DataFrame(all_trades)
        output_file = "trades_data.csv"
        df.to_csv(output_file, index=False)
        
        return JSONResponse({
            "message": f"Successfully processed {len(files)} PDFs",
            "total_trades": len(all_trades),
            "output_file": output_file
        })
    else:
        return JSONResponse({
            "message": "No trade data was extracted from the PDFs",
            "total_trades": 0
        })

@app.get("/")
async def read_root():
    return {"message": "Welcome to the PDF Table Extractor API. Use the /process-pdfs/ endpoint to upload and process PDFs."} 