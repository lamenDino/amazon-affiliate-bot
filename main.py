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
def extract_image(soup) -> str:
    for selector in [{'id': 'landingImage'}, {'id': 'imageBlockContainer'}, {'class': 'a-dynamic-image'}]:
        img_elem = soup.find('img', selector)
        if img_elem:
            image_url = img_elem.get('src')
            if image_url:
                return image_url
    return None
```

### CANVAS_NEW_STR
```python
def extract_image(soup) -> str:
    for selector in [{'id': 'landingImage'}, {'id': 'imageBlockContainer'}, {'class': 'a-dynamic-image'}]:
        img_elem = soup.find('img', selector)
        if img_elem:
            image_url = img_elem.get('src')
            if image_url:
                return image_url
    return None

def extract_description(soup) -> str:
    try:
        desc_elem = soup.find('div', {'id': 'feature-bullets'})
        if desc_elem:
            bullets = desc_elem.find_all('li')
            if bullets:
                first_bullet = bullets[0].get_text(strip=True)
                if len(first_bullet) > 200:
                    return first_bullet[:200] + "..."
                return first_bullet
        
        desc_elem = soup.find('div', {'id': 'aplus'})
        if desc_elem:
            text = desc_elem.get_text(strip=True)
            if len(text) > 150:
                return text[:150] + "..."
            return text
    except:
        pass
    return None
```

## CANVAS_EDIT_2

### CANVAS_OLD_STR
```python
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = extract_title(soup)
                    price = extract_price(soup)
                    rating, reviews_count = extract_rating(soup)
                    image_url = extract_image(soup)
                    condition_status = detect_seller_condition(normalized_url, soup)
                    promotion = extract_promotion(soup)
                    coupon = extract_coupon(soup)
```

### CANVAS_NEW_STR
```python
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = extract_title(soup)
                    price = extract_price(soup)
                    rating, reviews_count = extract_rating(soup)
                    image_url = extract_image(soup)
                    description = extract_description(soup)
                    condition_status = detect_seller_condition(normalized_url, soup)
                    promotion = extract_promotion(soup)
                    coupon = extract_coupon(soup)
```

## CANVAS_EDIT_3

### CANVAS_OLD_STR
```python
                        return {
                            'title': title,
                            'price': price,
                            'rating': rating,
                            'reviews': reviews_count,
                            'image': image_url,
                            'condition_status': condition_status,
                            'promotion': promotion,
                            'coupon': coupon,
                        }
```

### CANVAS_NEW_STR
```python
                        return {
                            'title': title,
                            'price': price,
                            'rating': rating,
                            'reviews': reviews_count,
                            'image': image_url,
                            'description': description,
                            'condition_status': condition_status,
                            'promotion': promotion,
                            'coupon': coupon,
                        }
```

## CANVAS_EDIT_4

### CANVAS_OLD_STR
```python
        return {
            'title': 'Prodotto Amazon',
            'price': None,
            'rating': None,
            'reviews': None,
            'image': None,
            'condition_status': None,
            'promotion': None,
            'coupon': None,
        }
    except Exception as e:
        logger.error(f"Error scraping: {e}")
        return {
            'title': 'Prodotto Amazon',
            'price': None,
            'rating': None,
            'reviews': None,
            'image': None,
            'condition_status': None,
            'promotion': None,
            'coupon': None,
        }
```

### CANVAS_NEW_STR
```python
        return {
            'title': 'Prodotto Amazon',
            'price': None,
            'rating': None,
            'reviews': None,
            'image': None,
            'description': None,
            'condition_status': None,
            'promotion': None,
            'coupon': None,
        }
    except Exception as e:
        logger.error(f"Error scraping: {e}")
        return {
            'title': 'Prodotto Amazon',
            'price': None,
            'rating': None,
            'reviews': None,
            'image': None,
            'description': None,
            'condition_status': None,
            'promotion': None,
            'coupon': None,
        }
```

## CANVAS_EDIT_5

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

# CANVAS_DESCRIPTION
Added description extraction from product feature bullets. Improved message formatting with: visual separators, better spacing, italicized descriptions and offers, inline code for pricing, better visual hierarchy with emojis, and eye-catching "ACQUISTA ORA" button. Message is now more attractive and user-friendly.

