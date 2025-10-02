from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import database
from app.core import security
from app.schemas import trade as trade_schema
from app.crud import trade as trade_crud
from app.models import user as user_model

router = APIRouter()

@router.post("/trades", response_model=trade_schema.Trade)
def create_trade(
    trade: trade_schema.TradeCreate,
    db: Session = Depends(database.get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    return trade_crud.create_trade(db=db, trade=trade, user_id=current_user.id)

@router.get("/trades", response_model=List[trade_schema.Trade])
def get_trades(
    db: Session = Depends(database.get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    return trade_crud.get_trades_by_user(db=db, user_id=current_user.id)

@router.get("/trades/{trade_id}", response_model=trade_schema.Trade)
def get_trade(
    trade_id: int,
    db: Session = Depends(database.get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    db_trade = trade_crud.get_trade_by_id(db=db, trade_id=trade_id, user_id=current_user.id)
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return db_trade

@router.put("/trades/{trade_id}", response_model=trade_schema.Trade)
def update_trade(
    trade_id: int,
    trade: trade_schema.TradeUpdate,
    db: Session = Depends(database.get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    db_trade = trade_crud.update_trade(db=db, trade_id=trade_id, trade=trade, user_id=current_user.id)
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return db_trade

@router.delete("/trades/{trade_id}", response_model=trade_schema.Trade)
def delete_trade(
    trade_id: int,
    db: Session = Depends(database.get_db),
    current_user: user_model.User = Depends(security.get_current_user)
):
    db_trade = trade_crud.delete_trade(db=db, trade_id=trade_id, user_id=current_user.id)
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return db_trade
