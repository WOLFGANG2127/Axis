"""Personal Readiness Score (PRS) Telegram workflow via the shared queue."""
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
from src.config.settings import settings
from src.database.supabase import get_supabase_client
from src.delivery.telegram_formatter import sanitize_telegram_md, send_telegram_payload

logger=logging.getLogger("axis.prs")
IST=ZoneInfo("Asia/Kolkata")

def send_prs_quiz() -> None:
    payload={"chat_id":settings.TELEGRAM_CHAT_ID,"text":sanitize_telegram_md("Morning Personal Readiness Score (PRS)\n\nQ1/3: How was your Sleep Quality?"),"parse_mode":"MarkdownV2","reply_markup":{"inline_keyboard":[[{"text":"Excellent (3)","callback_data":"prs_sleep_3"},{"text":"Average (2)","callback_data":"prs_sleep_2"},{"text":"Poor (1)","callback_data":"prs_sleep_1"}]]}}
    try:
        if not send_telegram_payload(settings.TELEGRAM_BOT_TOKEN,"sendMessage",payload): raise RuntimeError("Telegram PRS quiz delivery failed")
        today=datetime.now(IST).date().isoformat(); db=get_supabase_client()
        if not db.table("trader_session_state").select("id").eq("trading_date",today).execute().data:
            db.table("trader_session_state").insert({"trading_date":today,"is_trading_blocked":False,"prs_score":0,"prs_completed":False,"prs_completed_at":None,"prs_block_reason":None}).execute()
    except Exception as exc: logger.error("Failed to send PRS Quiz: %s",exc)

def process_prs_callback(callback_data: str, message_id: int) -> None:
    parts=callback_data.split("_")
    if len(parts)!=3 or parts[0]!="prs": return
    db=get_supabase_client(); today=datetime.now(IST).date().isoformat(); score=int(parts[2])
    rows=db.table("trader_session_state").select("prs_score").eq("trading_date",today).execute().data or []
    total=int(rows[0].get("prs_score",0) if rows else 0)+score
    db.table("trader_session_state").update({"prs_score":total}).eq("trading_date",today).execute()
    if parts[1]=="sleep": text,markup="Q2/3: How is your Mental Clarity?",[[{"text":"Sharp (3)","callback_data":"prs_clarity_3"}]]
    elif parts[1]=="clarity": text,markup="Q3/3: What is your Emotional State?",[[{"text":"Calm (3)","callback_data":"prs_emotion_3"}]]
    else:
        blocked=total<6; db.table("trader_session_state").update({"prs_completed":True,"is_trading_blocked":blocked,"prs_completed_at":datetime.now(IST).isoformat(),"prs_block_reason":"PRS_SCORE_BLOCKED" if blocked else None}).eq("trading_date",today).execute(); text="PRS blocked" if blocked else "PRS approved"; markup=None
    payload={"chat_id":settings.TELEGRAM_CHAT_ID,"message_id":message_id,"text":sanitize_telegram_md(text),"parse_mode":"MarkdownV2"}
    if markup: payload["reply_markup"]={"inline_keyboard":markup}
    send_telegram_payload(settings.TELEGRAM_BOT_TOKEN,"editMessageText",payload)
