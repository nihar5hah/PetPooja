from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.schemas import IngestionResponse
from app.db.session import get_db
from app.services.ingestion_service import ingest_pos_dataframe, parse_csv


router = APIRouter(tags=["ingestion"])


@router.post("/ingestion/pos-transactions", response_model=IngestionResponse)
async def ingest_pos_transactions(
    restaurant_id: str = "default_restaurant",
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    try:
        df = parse_csv(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    inserted = ingest_pos_dataframe(db, restaurant_id, df)

    return IngestionResponse(
        restaurant_id=restaurant_id,
        rows_received=len(df),
        rows_inserted=inserted,
    )
