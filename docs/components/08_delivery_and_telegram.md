# Component 08 — Delivery and Telegram

## 1. What This Component Is For (plain language, 2-3 sentences)
Formats and sends user-facing alerts and behavioral prompts over Telegram. Provides a Netlify webhook handler for inbound callback/query processing and routes user ratings and override commands back into outcome recording and session-state mutation.

## 2. Files in This Component
- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/delivery/telegram_formatter.py (127 lines)
  - One-line purpose: Build safe MarkdownV2 payloads, rate-limit, and post to Telegram's HTTP API; provides send_telegram_alert and send_behavioral_rating_prompt helpers.
  - Key functions/classes:
    - send_telegram_payload(bot_token, method, payload, timeout=10.0) -> bool: posts to constructed URL
    - sanitize_telegram_md(text) -> str: escapes MarkdownV2 specials
    - send_telegram_alert(bot_token, chat_id, text) -> bool: wraps send_telegram_payload with fallback plain text
  - STATUS: VERIFIED — evidence: file read shows url = f"https://api.telegram.org/bot{bot_token}/{method}" and requests.post usage.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/delivery/alert_builder.py (135 lines)
  - One-line purpose: Compose structured alert bodies (title, scoring rationale, position size, governance tags) handed to telegram_formatter for delivery.
  - Key functions: build_trade_alert(...), build_system_alert(...)
  - STATUS: VERIFIED — evidence: file read.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/netlify/functions/telegram_webhook.py (139 lines)
  - One-line purpose: Netlify serverless function handling inbound Telegram webhook payloads (callback_query and message), verifying secret, routing ratings and override commands back into outcome_recorder and prs_quiz.
  - STATUS: VERIFIED — evidence: file read; handler verifies x-telegram-bot-api-secret-token and routes callback_query actions to process_behavioral_rating/process_prs_callback.

## 3. How It Actually Works (the real internal logic, step by step)
1. Outbound send path: send_telegram_alert builds payload with parse_mode="MarkdownV2" and calls send_telegram_payload(bot_token, "sendMessage", payload). send_telegram_payload constructs the URL exactly as "https://api.telegram.org/bot{bot_token}/{method}" and posts JSON via requests.post (rate-limited to TELEGRAM_SEND_INTERVAL_SECONDS). If the first attempt raises, a fallback plain-text payload is sent. (See src/delivery/telegram_formatter.py.)
2. Inbound webhook: Netlify function receives POST event, optionally validates secret via x-telegram-bot-api-secret-token, parses callback_query or message, routes inline button clicks (data starting with rate_ and prs_) to process_behavioral_rating and process_prs_callback respectively, and acknowledges with HTTP 200 to prevent Telegram retries. For override_cooling_off it updates trader_session_state in the DB and edits the Telegram message via send_telegram_payload(editMessageText).
3. Sanitization: sanitize_telegram_md escapes every Telegram MarkdownV2 special character before sending; this sanitizer is used for behavioral prompts and editMessageText flows.

## 4. Connections — What This Depends On, What Depends On This
- Upstream: alert_builder constructs alert payloads; outcome_recorder triggers behavioral prompts and calls send_behavioral_rating_prompt.
- Downstream: observed actions include editing messages (editMessageText) and sendMessage; webhook routes user interactions back to journal/outcome processing and PRS quiz flows.
- External dependencies: requests library and network access to api.telegram.org. Netlify function expects TELEGRAM_WEBHOOK_SECRET in environment.

## 5. Current Status — What's Actually Working vs. Not
sub-feature | status label | evidence
---|---|---
Single HTTP delivery path to api.telegram.org | VERIFIED | src/delivery/telegram_formatter.py constructs https://api.telegram.org/bot... URL and uses requests.post
MarkdownV2 sanitizer applied on send paths | VERIFIED | sanitize_telegram_md used before payload text construction
Netlify inbound webhook handler present | VERIFIED | netlify/functions/telegram_webhook.py exists and routes callback_query/message
Webhook registration state with Telegram servers | UNABLE TO VERIFY (network access required) | No live network checks performed in this offline workspace; getWebhookInfo not executed

## 6. What's Remaining, Specific to This Component Only
- Confirm webhook registration (call getWebhookInfo) and that TELEGRAM_WEBHOOK_SECRET is set in the deployment environment — requires network/remote environment access.
- Add integration test that mocks requests.post to assert rate-limiting and markdown escaping behavior (tests exist but could not be run due to missing dependencies in this workspace).

## 7. Last Verified
2026-07-26 — commit aabcce72ac767f99149bda30dac255721c784e3b
