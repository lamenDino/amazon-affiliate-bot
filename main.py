# CANVAS_OUTPUT_TYPE
html_app

# CANVAS_PROJECT_NAME
Amazon Affiliate Bot

# CANVAS_OPERATION_TYPE
html_app_update

# CANVAS_DATA

## CANVAS_EDIT_1

### CANVAS_OLD_STR
```python
def build_product_message(product_info: dict, short_url: str, user_name: str = None) -> str:
    title = product_info.get('title', 'Prodotto Amazon')
    price = product_info.get('price', '')
    rating = product_info.get('rating', '')
    condition = product_info.get('condition_status', '')
    description = product_info.get('description', '')
    promotion = product_info.get('promotion', '')
    coupon = product_info.get('coupon', '')
    
    clean_price = ''
    if price:
        clean_price = re.sub(r'€.*', '€', price).strip()
    
    rating_stars = ''
    if rating:
        try:
            rating_float = float(rating.replace(',', '.'))
            stars = int(rating_float)
            rating_stars = '⭐' * stars
        except:
            rating_stars = f"⭐ {rating}/5"
    
    msg = ""
    
    if user_name:
        msg += f"<b>👤 {user_name}</b> ha condiviso:\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    msg += f"<b>📦 {title}</b>\n\n"
    
    if description:
        msg += f"<i>💬 {description}</i>\n\n"
    
    msg += f"<b>🏷️ Stato:</b> <code>{condition if condition else 'N/D'}</code>\n"
    msg += f"<b>💵 Prezzo:</b> <code>{clean_price if clean_price else 'N/D'}</code>\n"
    
    if rating_stars:
        msg += f"<b>✨ Valutazione:</b> {rating_stars}\n"
    
    if promotion or coupon:
        msg += "\n"
        if promotion:
            msg += f"<b>🎁 Offerta:</b> <i>{promotion}</i>\n"
        if coupon:
            msg += f"<b>🎟️ Coupon:</b> <i>{coupon}</i>\n"
    
    msg += f"\n<b><a href='{short_url}'>🛒 ACQUISTA ORA</a></b>"
    
    return msg
```

### CANVAS_NEW_STR
```python
def build_product_message(product_info: dict, short_url: str, user_name: str = None) -> str:
    title = product_info.get('title', 'Prodotto Amazon')
    price = product_info.get('price', '')
    rating = product_info.get('rating', '')
    condition = product_info.get('condition_status', '')
    description = product_info.get('description', '')
    promotion = product_info.get('promotion', '')
    coupon = product_info.get('coupon', '')
    
    clean_price = ''
    if price:
        clean_price = re.sub(r'€.*', '€', price).strip()
    
    rating_stars = ''
    if rating:
        try:
            rating_float = float(rating.replace(',', '.'))
            stars = int(rating_float)
            rating_stars = '⭐' * stars
        except:
            rating_stars = f"⭐ {rating}/5"
    
    if len(title) > 80:
        words = title.split()
        line1 = ''
        line2 = ''
        for word in words:
            if len(line1) + len(word) <= 50:
                line1 += word + ' '
            else:
                line2 += word + ' '
        title = (line1.strip() + '\n' + line2.strip()) if line2.strip() else line1.strip()
    
    msg = ""
    
    if user_name:
        msg += f"<b>👤 {user_name}</b> ha condiviso:\n"
    
    msg += f"\n<b>📦 {title}</b>\n"
    
    if description:
        msg += f"\n<i>💬 {description}</i>\n"
    
    msg += f"\n<b>🏷️ Stato:</b> {condition if condition else 'N/D'}\n"
    msg += f"<b>💵 Prezzo:</b> {clean_price if clean_price else 'N/D'}\n"
    
    if rating_stars:
        msg += f"<b>✨ Valutazione:</b> {rating_stars}\n"
    
    if promotion:
        msg += f"\n<b>🎁 Offerta:</b>\n<i>{promotion}</i>\n"
    
    if coupon:
        msg += f"<b>🎟️ Coupon:</b>\n<i>{coupon}</i>\n"
    
    msg += f"\n<b><a href='{short_url}'>🛒 ACQUISTA ORA</a></b>"
    
    return msg
```

# CANVAS_DESCRIPTION
Improved formatting: Title automatically splits to max 2 lines if longer than 80 chars. Removed excessive code formatting from price/condition (cleaner look). Better spacing with single newlines instead of doubles. More compact and readable layout matching the user's reference image.

