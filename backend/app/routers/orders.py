import pandas as pd
import io
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import database
from app.core import security
from app.schemas import order as order_schema
from app.crud import order as order_crud
from app.models import user as user_model

router = APIRouter()

EXPECTED_COLUMNS = [
    "Exec Time", "Spread", "Side", "Qty", "Pos Effect", "Symbol",
    "Exp", "Strike", "Type", "Price", "Net Price", "Order Type"
]

@router.post("/orders/upload", status_code=201)
async def upload_orders_csv(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")

    contents = await file.read()
    
    try:
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV file: {e}")

    if list(df.columns) != EXPECTED_COLUMNS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV format. Columns must be exactly: {EXPECTED_COLUMNS}"
        )
    # Rename columns to match the schema
    df.columns = [
        "execution_time", "spread", "side", "quantity", "position_effect", "symbol",
        "expiration_date", "strike_price", "option_type", "price", "net_price", "order_type"
    ]

    # Check for missing values in required columns
    required_cols = ["side", "position_effect", "symbol", "price", "net_price"]
    for col in required_cols:
        if df[col].isnull().any():
            raise HTTPException(status_code=400, detail=f"Missing values in required column: '{col}'")

    # Convert date columns
    df['execution_time'] = pd.to_datetime(df['execution_time'])
    df['expiration_date'] = pd.to_datetime(df['expiration_date']).dt.date

    # Replace NaT with None for nullable date fields
    df['expiration_date'] = df['expiration_date'].replace({pd.NaT: None})

    # Replace inf and -inf with None
    df.replace([float('inf'), float('-inf')], None, inplace=True)

    # Convert quantity to integer, filling missing with 0
    df['quantity'] = df['quantity'].fillna(0).astype(int)

    for _, row in df.iterrows():
        order_data = order_schema.OrderCreate(**row.to_dict())
        order_crud.create_order(db=db, order=order_data, user_id=current_user.id)

    return {"message": f"{len(df)} orders have been successfully uploaded."}

@router.get("/orders", response_model=List[order_schema.Order])
def get_orders(
    db: Session = Depends(database.get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    return order_crud.get_orders_by_user(db=db, user_id=current_user.id)
