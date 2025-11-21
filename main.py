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
def build_product_message(product_info: dict, short_url: str, username: str) -> str:
    """Build a beautiful product message"""
    
    title = product_info.get('title', 'Prodotto Amazon')
    # Truncate title if too long
    if len(title) > 60:
        title = title[:57] + "..."
    
    price = product_info.get('price', '')
    rating = product_info.get('rating', '')
    reviews = product_info.get('reviews', '')
    description = product_info.get('description', '')
    condition_status = product_info.get('condition_status', '')
    condition_details = product_info.get('condition_details', '')
    
    # Build rating display with star emoji
    rating_display = ''
    if rating:
        rating_display = f"⭐ <b>{rating}</b> su 5"
        if reviews:
            rating_display += f" • <i>{reviews} recensioni</i>"
        rating_display += "\n"
    
    # Build price display - formatted nicely
    price_display = ''
    if price:
        price_display = f"💰 <b>Prezzo: {price}€</b>\n"
    
    # Build condition display for used items
    condition_display = ''
    if condition_status:
        condition_display = f"🔄 <b>{condition_status}</b>\n"
        if condition_details:
            condition_display += f"   <i>{condition_details}</i>\n"
    
    # Build description
    desc_display = ''
    if description and description != 'Scopri il prodotto su Amazon':
        desc_display = f"📝 <i>{description}</i>\n\n"
    
    message = (
        f"<b>👤 {username}</b> ha condiviso:\n\n"
        f"<b>🛍️ {title}</b>\n\n"
        f"{price_display}"
        f"{rating_display}"
        f"{condition_display}"
        f"{desc_display}"
        f"<b><a href='{short_url}'>🔗 Clicca qui per acquistare</a></b>"
    )
    
    return message
```

### CANVAS_NEW_STR
```html
def build_product_message(product_info: dict, short_url: str, username: str) -> str:
    """Build a beautiful product message - optimized for Telegram caption length limit (1024 chars)"""
    
    title = product_info.get('title', 'Prodotto Amazon')
    # Truncate title if too long
    if len(title) > 50:
        title = title[:47] + "..."
    
    price = product_info.get('price', '')
    rating = product_info.get('rating', '')
    condition_status = product_info.get('condition_status', '')
    
    # Build compact message - stay under 1024 chars for photo caption
    message_parts = []
    message_parts.append(f"<b>{title}</b>")
    
    if price:
        message_parts.append(f"💰 {price}€")
    
    if rating:
        message_parts.append(f"⭐ {rating}/5")
    
    if condition_status:
        message_parts.append(f"🔄 {condition_status}")
    
    message = "\n".join(message_parts)
    message += f"\n\n<b><a href='{short_url}'>🔗 Acquista</a></b>"
    
    return message
```

## CANVAS_EDIT_2

### CANVAS_OLD_STR
```html
        # Send product with image if available
        if product_info.get('image'):
            try:
                await update.message.chat.send_photo(
                    photo=product_info['image'],
                    caption=message,
                    parse_mode='HTML'
                )
                logger.info(f"Sent photo with message")
            except Exception as e:
                logger.warning(f"Could not send photo: {e}, sending text only")
                await update.message.chat.send_message(message, parse_mode='HTML')
        else:
            logger.info(f"No image found, sending text message only")
            await update.message.chat.send_message(message, parse_mode='HTML')
```

### CANVAS_NEW_STR
```html
        # Send product with image if available
        if product_info.get('image'):
            try:
                await update.message.chat.send_photo(
                    photo=product_info['image'],
                    caption=message,
                    parse_mode='HTML'
                )
                logger.info(f"Sent photo with message")
            except Exception as e:
                logger.warning(f"Could not send photo: {e}, sending text only")
                # Fallback: send just the link if message too long
                fallback_msg = f"<b>{product_info.get('title', 'Prodotto')}</b>\n\n<b><a href='{short_url}'>🔗 Acquista</a></b>"
                try:
                    await update.message.chat.send_message(fallback_msg, parse_mode='HTML')
                except:
                    await update.message.chat.send_message(f"Link: {short_url}")
        else:
            logger.info(f"No image found, sending text message only")
            try:
                await update.message.chat.send_message(message, parse_mode='HTML')
            except:
                # Fallback if message too long
                fallback_msg = f"<b>{product_info.get('title', 'Prodotto')}</b>\n\n<b><a href='{short_url}'>🔗 Acquista</a></b>"
                await update.message.chat.send_message(fallback_msg, parse_mode='HTML')
```

# CANVAS_DESCRIPTION
Optimized message format to stay within Telegram's 1024-character caption limit. Removed username, description, and detailed condition info to keep messages compact. Added fallback error handling for messages that are still too long - will send minimal version with just product title and link.

