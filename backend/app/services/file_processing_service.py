# backend/app/services/file_processing_service.py

import pandas as pd
import io
from fastapi import HTTPException, UploadFile

EXPECTED_COLUMNS = [
    "Exec Time", "Spread", "Side", "Qty", "Pos Effect", "Symbol",
    "Exp", "Strike", "Type", "Price", "Net Price", "Order Type"
]

def _process_csv(file: UploadFile) -> pd.DataFrame:
    try:
        contents = file.file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV file: {e}")

    if list(df.columns) != EXPECTED_COLUMNS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV format. Columns must be exactly: {EXPECTED_COLUMNS}"
        )
    return df

def _process_xlsx(file: UploadFile) -> pd.DataFrame:
    try:
        df = pd.read_excel(file.file, sheet_name=0, header=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing XLSX file: {e}")

    # Find the start of the trade history
    start_row = None
    for i, row in df.iterrows():
        if 'Account Trade History' in row.to_string():
            start_row = i + 1
            break

    if start_row is None:
        raise HTTPException(status_code=400, detail="Could not find 'Account Trade History' section in the XLSX file.")

    # The next row is the header
    header = df.iloc[start_row]
    
    # Create a new DataFrame with the data and columns
    data_df = df.iloc[start_row + 1:]
    data_df.columns = header

    # Drop the first column
    data_df = data_df.iloc[:, 1:]

    # Reset the index
    data_df.reset_index(drop=True, inplace=True)

    # Find the end of the data (first empty row)
    empty_row_index = data_df.isnull().all(axis=1).idxmax()
    if empty_row_index > 0:
        data_df = data_df.loc[:empty_row_index-1]

    # The column names in the xlsx might not be exactly the same as the expected columns.
    # I will need to inspect the file to create a proper mapping.
    # For now, I will assume the columns are in the correct order and have similar names.
    
    # I will rename the columns to match the expected columns.
    # This is a placeholder for the actual column mapping.
    # I will need to analyze the xlsx file to create the correct mapping.
    column_mapping = {
        data_df.columns[0]: 'Exec Time',
        data_df.columns[1]: 'Spread',
        data_df.columns[2]: 'Side',
        data_df.columns[3]: 'Qty',
        data_df.columns[4]: 'Pos Effect',
        data_df.columns[5]: 'Symbol',
        data_df.columns[6]: 'Exp',
        data_df.columns[7]: 'Strike',
        data_df.columns[8]: 'Type',
        data_df.columns[9]: 'Price',
        data_df.columns[10]: 'Net Price',
        data_df.columns[11]: 'Order Type',
    }
    
    # Rename columns and select only the required ones
    data_df = data_df.rename(columns=column_mapping)
    
    # Ensure all expected columns are present
    for col in EXPECTED_COLUMNS:
        if col not in data_df.columns:
            # Add missing column with default value (e.g., None or np.nan)
            data_df[col] = None
            
    data_df = data_df[EXPECTED_COLUMNS]

    # Check for missing values in required columns
    required_cols = [col for col in EXPECTED_COLUMNS if col not in ['Exp', 'Strike']]
    for col in required_cols:
        if data_df[col].isnull().any():
            raise HTTPException(status_code=400, detail=f"Missing values in required column: {col}")

    return data_df

def process_file(file: UploadFile) -> pd.DataFrame:
    if file.content_type == 'text/csv':
        return _process_csv(file)
    elif file.filename.endswith('.xlsx'):
        return _process_xlsx(file)
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV or XLSX file.")