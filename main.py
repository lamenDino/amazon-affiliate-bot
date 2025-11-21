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
def detect_seller_condition(url: str, soup) -> str:
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        smid = query_params.get('smid', [''])[0]
        aod = query_params.get('aod', [''])[0]
        
        logger.info(f"Detected SMID: '{smid}', AOD: '{aod}'")
        
        if aod == '1':
            logger.info("Found aod=1 - USED items view")
            return "Usato - Venduto da terzo"
        
        if not smid:
            logger.info("No SMID in URL - Sold by Amazon = NEW")
            return "Nuovo - Venduto da Amazon"
        
        if smid in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info(f"Official Amazon SMID: {smid} - NEW")
            return "Nuovo - Venduto da Amazon"
        
        seller_section = soup.find('div', {'id': 'merchant-info'})
        if seller_section:
            seller_text = seller_section.get_text(strip=True)
            logger.info(f"Seller section text: {seller_text[:150]}")
            if 'Amazon Seconda mano' in seller_text:
                logger.info("Found 'Amazon Seconda mano' in seller section - USED")
                return "Usato - Venduto da Amazon Seconda mano"
        
        if smid:
            logger.info(f"Third party SMID: {smid} - USED")
            return "Usato - Venduto da terzo"
        
        logger.info("Default: NEW")
        return "Nuovo - Venduto da Amazon"
        
    except Exception as e:
        logger.error(f"Error detecting condition: {e}")
        return "Nuovo - Venduto da Amazon"
```

### CANVAS_NEW_STR
```python
def detect_seller_condition(url: str, soup) -> str:
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        smid = query_params.get('smid', [''])[0]
        aod = query_params.get('aod', [''])[0]
        s_param = query_params.get('s', [''])[0]
        
        logger.info(f"Detected SMID: '{smid}', AOD: '{aod}', S: '{s_param}'")
        
        if aod == '1':
            logger.info("Found aod=1 - USED items view")
            return "Usato - Venduto da terzo"
        
        if 'warehouse-deals' in s_param.lower():
            logger.info("Found warehouse-deals parameter - USED from warehouse")
            return "Usato - Warehouse Deals Amazon"
        
        if not smid:
            logger.info("No SMID in URL - Sold by Amazon = NEW")
            return "Nuovo - Venduto da Amazon"
        
        if smid in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info(f"Official Amazon SMID: {smid} - NEW")
            return "Nuovo - Venduto da Amazon"
        
        seller_section = soup.find('div', {'id': 'merchant-info'})
        if seller_section:
            seller_text = seller_section.get_text(strip=True)
            logger.info(f"Seller section text: {seller_text[:150]}")
            if 'Amazon Seconda mano' in seller_text:
                logger.info("Found 'Amazon Seconda mano' in seller section - USED")
                return "Usato - Venduto da Amazon Seconda mano"
        
        if smid:
            logger.info(f"Third party SMID: {smid} - USED")
            return "Usato - Venduto da terzo"
        
        logger.info("Default: NEW")
        return "Nuovo - Venduto da Amazon"
        
    except Exception as e:
        logger.error(f"Error detecting condition: {e}")
        return "Nuovo - Venduto da Amazon"
```

## CANVAS_EDIT_2

### CANVAS_OLD_STR
```python
def build_product_message(product_info: dict, short_url: str, user_name: str = None) -> str:
    title = product_info.get('title', 'Prodotto Amazon')
    price = product_info.get('price', '')
    rating = product_info.get('rating', '')
    condition = product_info.get('condition_status', '')
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
        msg += f"<b>👤 Chi ha condiviso:</b> {user_name}\n\n"
    
    msg += f"<b>📌 Nome articolo:</b>\n{title}\n\n"
    msg += f"<b>🔄 Se usato o nuovo:</b> {condition if condition else 'N/D'}\n\n"
    msg += f"<b>💰 Prezzo:</b> {clean_price if clean_price else 'N/D'}\n\n"
    
    if rating_stars:
        msg += f"<b>⭐ Valutazione:</b> {rating_stars}\n\n"
    
    if promotion:
        msg += f"<b>🎉 Promozione:</b> {promotion}\n\n"
    
    if coupon:
        msg += f"<b>🎟️ Coupon:</b> {coupon}\n\n"
    
    msg += f"<b><a href='{short_url}'>👉 Clicca qui per acquistare</a></b>"
    
    return msg
```

### CANVAS_NEW_STR
```python
def build_product_message(product_info: dict, short_url: str, user_name: str = None) -> str:
    title = product_info.get('title', 'Prodotto Amazon')
    price = product_info.get('price', '')
    rating = product_info.get('rating', '')
    condition = product_info.get('condition_status', '')
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
        msg += f"<b>👤:</b> {user_name} ha inviato questo grande articolo\n\n"
    
    msg += f"<b>📌 Nome articolo:</b>\n{title}\n\n"
    msg += f"<b>🔄 Chi lo vende:</b> {condition if condition else 'N/D'}\n\n"
    msg += f"<b>💰 Prezzo:</b> {clean_price if clean_price else 'N/D'}\n\n"
    
    if rating_stars:
        msg += f"{rating_stars}\n\n"
    
    if promotion:
        msg += f"<b>🎉 Promozione:</b> {promotion}\n\n"
    
    if coupon:
        msg += f"<b>🎟️ Coupon:</b> {coupon}\n\n"
    
    msg += f"<b><a href='{short_url}'>👉 Clicca qui per acquistare</a></b>"
    
    return msg
```

# CANVAS_DESCRIPTION
Fixed: (1) Added detection for warehouse-deals parameter (`&s=warehouse-deals`) to identify used items from Amazon Warehouse Deals. (2) Improved message formatting with new style: "👤: [Nome] ha inviato questo grande articolo", changed "Chi lo vende:" label, and stars displayed without bold label. Now correctly identifies warehouse deals as used items.

