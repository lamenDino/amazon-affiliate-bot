# CANVAS_OUTPUT_TYPE
html_app

# CANVAS_PROJECT_NAME
Amazon Affiliate Bot

# CANVAS_OPERATION_TYPE
html_app_update

# CANVAS_DATA

## CANVAS_EDIT_1

### CANVAS_OLD_STR
```html
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URL messages"""
    text = update.message.text
    user = update.message.from_user
    
    # Extract Amazon URL from text (might be in a list or with other text)
    original_url = extract_amazon_url_from_text(text)
    
    if not original_url:
        await update.message.reply_text(
            "❌ Non ho trovato link Amazon nel tuo messaggio!\n\n"
            "Invia un link di Amazon.it e farò il resto."
        )
        return
```

### CANVAS_NEW_STR
```html
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URL messages"""
    text = update.message.text
    user = update.message.from_user
    
    # Extract Amazon URL from text (might be in a list or with other text)
    original_url = extract_amazon_url_from_text(text)
    
    if not original_url:
        # Silently ignore if no Amazon URL found - don't send any response
        logger.info(f"No Amazon URL found in message from {user.username}: {text}")
        return
```

# CANVAS_DESCRIPTION
Modified handle_url function to silently ignore messages without valid Amazon links instead of sending an error message. Now when a user sends an invalid/non-Amazon link, the bot won't respond at all.

