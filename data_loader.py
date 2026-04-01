import pandas as pd
import requests
import zipfile
import io
import os
import numpy as np

def download_and_clean_data():
    print("Starting data download from UCI Machine Learning Repository...")
    # The URL for the standard Online Retail II dataset
    url = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    parquet_path = 'data/online_retail_cleaned.parquet'
    
    if os.path.exists(parquet_path):
        print("Cleaned data already exists. Skipping download.")
        return pd.read_parquet(parquet_path)
    
    print("Downloading zip file...")
    response = requests.get(url)
    response.raise_for_status()
    
    # Extract the excel file from the zip
    print("Extracting zip file...")
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        excel_filename = z.namelist()[0] # Should be 'online_retail_II.xlsx'
        with z.open(excel_filename) as f:
            print(f"Reading {excel_filename} (this may take a minute due to file size)...")
            # The dataset has two sheets (Year 2009-2010 and Year 2010-2011)
            # We will concat both to get the full 1 million rows dataset.
            df_dict = pd.read_excel(f, sheet_name=None)
            df = pd.concat(df_dict.values(), ignore_index=True)
            
    print(f"Initial raw data shape: {df.shape}")
    
    # Clean the Data
    print("Cleaning data...")
    # 1. Drop rows with missing Customer ID as we can't use them for Churn/CLV analysis
    df = df.dropna(subset=['Customer ID'])
    
    # 2. Add Revenue column
    df['Revenue'] = df['Quantity'] * df['Price']
    
    # 3. Filter out strange/cancelled transactions (Invoice starts with 'C')
    # But wait, returns are part of profitability. Let's keep them but we might want them flagged.
    # Actually, for standard RFM, we often remove cancellations or treat them as negative revenue.
    # Let's keep them as negative revenue to reflect true CLV.
    
    # 4. Standardize Data Types
    df['Customer ID'] = df['Customer ID'].astype(int).astype(str)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    print(f"Cleaned data shape: {df.shape}")
    
    # Save optimized parquet format
    print("Saving to parquet for fast loading...")
    df.to_parquet(parquet_path, index=False)
    print("Data processing complete!")
    return df

if __name__ == "__main__":
    download_and_clean_data()
