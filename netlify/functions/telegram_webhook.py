import json
import logging

logger = logging.getLogger("axis.webhook")
logger.setLevel(logging.INFO)

def handler(event, context):
    """Netlify Serverless Function to handle inbound Telegram Webhooks."""
    
    # 1. Validate request method
    if event.get("httpMethod") != "POST":
        return {
            "statusCode": 405,
            "body": "Method Not Allowed"
        }
        
    try:
        # 2. Parse payload
        body = event.get("body", "{}")
        payload = json.loads(body)
        
        # 3. Extract key Telegram fields
        chat_id = None
        message_id = None
        data = None
        
        if "callback_query" in payload:
            # Inline button click
            query = payload["callback_query"]
            data = query.get("data", "")
            message = query.get("message", {})
            chat_id = message.get("chat", {}).get("id")
            message_id = message.get("message_id")
            logger.info("Received callback_query: chat_id=%s, msg_id=%s, data=%s", chat_id, message_id, data)
            
            # Routing inbound data payloads
            if data.startswith("rate_"):
                parts = data.split("_")
                if len(parts) == 3:
                    trade_id = parts[1]
                    score = parts[2]
                    from src.journal.outcome_recorder import process_behavioral_rating
                    process_behavioral_rating(score, trade_id)
            elif data.startswith("prs_"):
                from src.scheduling.prs_quiz import process_prs_callback
                process_prs_callback(data, message_id)
            elif data == "override_cooling_off":
                # Prompt 34: Override the cooling_off_until lock
                from src.database.supabase import get_supabase_client
                from datetime import datetime
                from zoneinfo import ZoneInfo
                import requests
                from src.config.settings import settings
                
                db = get_supabase_client()
                today = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
                
                try:
                    # Clearing the lock assuming it's tracked in trader_session_state
                    db.table("trader_session_state").update({
                        "cooling_off_until": None,
                        "is_trading_blocked": False
                    }).eq("trading_date", today).execute()
                except Exception as e:
                    logger.error("Failed to clear cooling_off_until in DB: %s", e)
                    
                # Edit the message to reflect the override
                edit_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/editMessageText"
                requests.post(edit_url, json={
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": "🔓 **OVERRIDE ACCEPTED**\n\nThe cooling-off period has been manually cleared. Trading is re-enabled. Exercise caution.",
                    "parse_mode": "Markdown"
                }, timeout=10.0)
            
        elif "message" in payload:
            # Standard text reply
            message = payload["message"]
            chat_id = message.get("chat", {}).get("id")
            message_id = message.get("message_id")
            data = message.get("text", "")
            logger.info("Received standard message: chat_id=%s, msg_id=%s, text=%s", chat_id, message_id, data)
            
            # Database parsing logic for text replies (Prompt 33)
            # If the user just typed "5" or "1" as a raw text reply for the behavioral rating
            if data and data.strip() in ["1", "2", "3", "4", "5"]:
                from src.journal.outcome_recorder import process_behavioral_rating
                process_behavioral_rating(data.strip())
            
        else:
            logger.warning("Received unhandled Telegram payload structure: %s", json.dumps(payload))
            
        # 4. Acknowledge Receipt
        # Standard 200 OK prevents Telegram from retrying the webhook
        return {
            "statusCode": 200,
            "body": "OK"
        }
        
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON body (Fail-Open): %s", e)
        # Return 200 OK to prevent Telegram retry loop on malformed JSON
        return {
            "statusCode": 200,
            "body": "OK"
        }
    except Exception as e:
        logger.error("Error processing webhook (Fail-Open): %s", e)
        # Return 200 OK to gracefully fail-open and prevent catastrophic denial-of-service
        return {
            "statusCode": 200,
            "body": "OK"
        }
