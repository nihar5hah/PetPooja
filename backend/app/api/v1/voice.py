from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.voice_schemas import VoiceWebhookIn, VoiceWebhookOut
from app.services.voice_order_service import process_voice_order, verify_retell_signature


router = APIRouter(tags=["voice"])


@router.post("/voice/retell-webhook", response_model=VoiceWebhookOut)
async def retell_webhook(
    request: Request,
    payload: VoiceWebhookIn,
    db: Session = Depends(get_db),
    x_retell_signature: str | None = Header(default=None),
):
    raw_body = await request.body()
    if not verify_retell_signature(raw_body, x_retell_signature):
        raise HTTPException(status_code=401, detail="Invalid Retell signature")

    result = process_voice_order(db, payload.model_dump())
    return VoiceWebhookOut(**result)
