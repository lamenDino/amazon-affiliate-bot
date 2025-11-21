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
def extract_price(soup) -> str:
    try:
        price_container = soup.find('span', {'class': 'a-price'})
        if price_container:
            price_text = price_container.get_text(strip=True)
            match = re.search(r'[\d.,€\$]+', price_text)
            if match:
                return match.group(0)
        
        price_elem = soup.find('span', {'class': 'a-price-whole'})
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            parent = price_elem.parent
            if parent:
                full_price = parent.get_text(strip=True)
                return full_price
            return price_text
    except Exception as e:
        logger.error(f"Error extracting price: {e}")
    
    return None
```

### CANVAS_NEW_STR
```html
def extract_price(soup) -> str:
    try:
        price_container = soup.find('span', {'class': 'a-price'})
        if price_container:
            price_text = price_container.get_text(strip=True)
            # Extract only first price occurrence (not duplicate)
            prices = re.findall(r'[\d.,€\$]+', price_text)
            if prices:
                return prices[0]
        
        price_elem = soup.find('span', {'class': 'a-price-whole'})
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            # Return just the number, not the full parent text
            return price_text
    except Exception as e:
        logger.error(f"Error extracting price: {e}")
    
    return None
```

## CANVAS_EDIT_2

### CANVAS_OLD_STR
```html
def detect_seller_condition(url: str, soup) -> str:
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        smid = query_params.get('smid', [''])[0]
        aod = query_params.get('aod', [''])[0]
        
        logger.info(f"Detected SMID: {smid}, AOD: {aod}")
        
        if aod == '1':
            logger.info("Found aod=1 - USED items")
            return "Usato - Venduto da terzo"
        
        seller_section = soup.find('div', {'id': 'merchant-info'})
        if seller_section:
            seller_text = seller_section.get_text()
            logger.info(f"Seller section found: {seller_text[:100]}")
            if 'Amazon Seconda mano' in seller_text:
                logger.info("Found 'Amazon Seconda mano' in seller section")
                return "Usato - Venduto da Amazon Seconda mano"
        
        sold_by = soup.find('div', {'id': 'tabular-buybox-container'})
        if sold_by:
            sold_text = sold_by.get_text()
            logger.info(f"Sold by section: {sold_text[:100]}")
            if 'Amazon Seconda mano' in sold_text:
                logger.info("Found 'Amazon Seconda mano' in sold by section")
                return "Usato - Venduto da Amazon Seconda mano"
        
        offers = soup.find('div', {'id': 'aod-offer-list'})
        if offers:
            offers_text = offers.get_text()
            logger.info(f"Offers section: {offers_text[:100]}")
            if 'Amazon Seconda mano' in offers_text:
                logger.info("Found 'Amazon Seconda mano' in offers section")
                return "Usato - Venduto da Amazon Seconda mano"
        
        if smid in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info("Amazon official seller - NEW")
            return "Nuovo - Venduto da Amazon"
        
        if smid and smid not in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info(f"Third party seller with SMID: {smid}")
            return "Usato - Venduto da terzo"
        
        logger.info("No condition info found - assuming NEW")
        return "Nuovo - Venduto da Amazon"
        
    except Exception as e:
        logger.error(f"Error detecting condition: {e}")
    
    return None
```

### CANVAS_NEW_STR
```html
def detect_seller_condition(url: str, soup) -> str:
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        smid = query_params.get('smid', [''])[0]
        aod = query_params.get('aod', [''])[0]
        
        logger.info(f"Detected SMID: {smid}, AOD: {aod}")
        
        # CHECK FULL PAGE FIRST for "Amazon Seconda mano"
        full_page_text = soup.get_text()
        if 'Amazon Seconda mano' in full_page_text:
            logger.info("Found 'Amazon Seconda mano' in page - USED item")
            return "Usato - Venduto da Amazon Seconda mano"
        
        if aod == '1':
            logger.info("Found aod=1 - USED items")
            return "Usato - Venduto da terzo"
        
        seller_section = soup.find('div', {'id': 'merchant-info'})
        if seller_section:
            seller_text = seller_section.get_text()
            logger.info(f"Seller section: {seller_text[:100]}")
            if 'Amazon Seconda mano' in seller_text:
                logger.info("Found 'Amazon Seconda mano' in seller")
                return "Usato - Venduto da Amazon Seconda mano"
        
        if smid in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info("Amazon official seller - NEW")
            return "Nuovo - Venduto da Amazon"
        
        if smid and smid not in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info(f"Third party seller - USED")
            return "Usato - Venduto da terzo"
        
        logger.info("No condition - assume NEW")
        return "Nuovo - Venduto da Amazon"
        
    except Exception as e:
        logger.error(f"Error detecting condition: {e}")
    
    return None
```

## CANVAS_EDIT_3

### CANVAS_OLD_STR
```html
async def get_amazon_product_info(url: str) -> dict:
    try:
        normalized_url = normalize_amazon_url(url)
        logger.info(f"Scraping from: {normalized_url}")
        
        for user_agent in USER_AGENTS:
            try:
                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
                }
                
                async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                    response = await client.get(normalized_url, headers=headers)
                    if response.status_code != 200:
                        logger.warning(f"Got status {response.status_code}")
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = extract_title(soup)
                    price = extract_price(soup)
                    rating, reviews_count = extract_rating(soup)
                    image_url = extract_image(soup)
                    condition_status = detect_seller_condition(normalized_url, soup)
                    
                    logger.info(f"Scraped - Title: {title}, Price: {price}, Condition: {condition_status}")
                    
                    if title and title != 'Prodotto Amazon':
                        return {
                            'title': title,
                            'price': price,
                            'rating': rating,
                            'reviews': reviews_count,
                            'image': image_url,
                            'condition_status': condition_status,
                        }
            except Exception as e:
                logger.warning(f"Error with user agent: {e}")
                continue
        
        return {
            'title': 'Prodotto Amazon',
            'price': None,
            'rating': None,
            'reviews': None,
            'image': None,
            'condition_status': None,
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
        }
```

### CANVAS_NEW_STR
```html
async def get_amazon_product_info(url: str) -> dict:
    try:
        normalized_url = normalize_amazon_url(url)
        logger.info(f"Scraping from: {normalized_url}")
        
        for user_agent in USER_AGENTS:
            try:
                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
                }
                
                async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                    response = await client.get(normalized_url, headers=headers)
                    if response.status_code != 200:
                        logger.warning(f"Got status {response.status_code}")
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = extract_title(soup)
                    price = extract_price(soup)
                    rating, reviews_count = extract_rating(soup)
                    image_url = extract_image(soup)
                    condition_status = detect_seller_condition(normalized_url, soup)
                    promotion = extract_promotion(soup)
                    coupon = extract_coupon(soup)
                    
                    logger.info(f"Scraped - Title: {title}, Price: {price}, Condition: {condition_status}, Promo: {promotion}, Coupon: {coupon}")
                    
                    if title and title != 'Prodotto Amazon':
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
            except Exception as e:
                logger.warning(f"Error with user agent: {e}")
                continue
        
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

## CANVAS_EDIT_4

### CANVAS_OLD_STR
```html
def build_product_message(product_info: dict, short_url: str) -> str:
    title = product_info.get('title', 'Prodotto Amazon')
    if len(title) > 50:
        title = title[:47] + "..."
    
    price = product_info.get('price', '')
    rating = product_info.get('rating', '')
    condition = product_info.get('condition_status', '')
    
    parts = [f"<b>{title}</b>"]
    
    if price:
        parts.append(f"💰 {price}€")
    if rating:
        parts.append(f"⭐ {rating}/5")
    if condition:
        parts.append(f"🔄 {condition}")
    
    msg = "\n".join(parts)
    msg += f"\n\n<b><a href='{short_url}'>🔗 Acquista</a></b>"
    
    return msg
```

### CANVAS_NEW_STR
```html
def build_product_message(product_info: dict, short_url: str) -> str:
    title = product_info.get('title', 'Prodotto Amazon')
    if len(title) > 50:
        title = title[:47] + "..."
    
    price = product_info.get('price', '')
    rating = product_info.get('rating', '')
    condition = product_info.get('condition_status', '')
    promotion = product_info.get('promotion', '')
    coupon = product_info.get('coupon', '')
    
    parts = [f"<b>{title}</b>"]
    
    if price:
        # Extract just the number without duplicates
        clean_price = re.sub(r'€.*', '€', price).strip()
        parts.append(f"💰 {clean_price}")
    if rating:
        parts.append(f"⭐ {rating}/5")
    if condition:
        parts.append(f"🔄 {condition}")
    if promotion:
        parts.append(f"🎉 {promotion}")
    if coupon:
        parts.append(f"🎟️ {coupon}")
    
    msg = "\n".join(parts)
    msg += f"\n\n<b><a href='{short_url}'>🔗 Acquista</a></b>"
    
    return msg
```

## CANVAS_EDIT_5

### CANVAS_OLD_STR
```html
def extract_rating(soup) -> tuple:
    rating = None
    reviews = None
    try:
        rating_elem = soup.find('span', {'class': 'a-icon-star-small'})
        if not rating_elem:
            rating_elem = soup.find('span', {'class': 'a-icon-star'})
        
        if rating_elem:
            rating_span = rating_elem.find('span')
            if rating_span:
                rating_text = rating_span.get_text(strip=True)
                match = re.search(r'[\d,]+', rating_text)
                if match:
                    rating = match.group(0)
        
        reviews_elem = soup.find('span', {'id': 'acrCustomerReviewText'})
        if reviews_elem:
            reviews_text = reviews_elem.get_text(strip=True)
            match = re.search(r'[\d.]+', reviews_text.replace('.', ''))
            if match:
                reviews = match.group(0)
    except:
        pass
    
    return rating, reviews
```

### CANVAS_NEW_STR
```html
def extract_rating(soup) -> tuple:
    rating = None
    reviews = None
    try:
        rating_elem = soup.find('span', {'class': 'a-icon-star-small'})
        if not rating_elem:
            rating_elem = soup.find('span', {'class': 'a-icon-star'})
        
        if rating_elem:
            rating_span = rating_elem.find('span')
            if rating_span:
                rating_text = rating_span.get_text(strip=True)
                match = re.search(r'[\d,]+', rating_text)
                if match:
                    rating = match.group(0)
        
        reviews_elem = soup.find('span', {'id': 'acrCustomerReviewText'})
        if reviews_elem:
            reviews_text = reviews_elem.get_text(strip=True)
            match = re.search(r'[\d.]+', reviews_text.replace('.', ''))
            if match:
                reviews = match.group(0)
    except:
        pass
    
    return rating, reviews

def extract_promotion(soup) -> str:
    try:
        # Look for "Limited time deal", "Sconto", "Offerta"
        for elem in soup.find_all(['span', 'div', 'a']):
            text = elem.get_text(strip=True)
            if any(word in text.lower() for word in ['offerta', 'sconto', 'limited time', 'deal', 'promoz']):
                if len(text) < 100:
                    logger.info(f"Found promotion: {text}")
                    return text
    except:
        pass
    return None

def extract_coupon(soup) -> str:
    try:
        # Look for coupon badge
        coupon_elem = soup.find('div', {'class': re.compile('coupon|promotion-badge', re.I)})
        if coupon_elem:
            coupon_text = coupon_elem.get_text(strip=True)
            if 'coupon' in coupon_text.lower() or 'sconto' in coupon_text.lower():
                logger.info(f"Found coupon: {coupon_text}")
                return coupon_text
        
        # Alternative: search in page text
        for elem in soup.find_all(['span', 'div']):
            text = elem.get_text(strip=True)
            if 'coupon' in text.lower() and len(text) < 150:
                logger.info(f"Found coupon text: {text}")
                return text
    except:
        pass
    return None
```

# CANVAS_DESCRIPTION
Fixed: (1) Amazon Seconda mano detection - now checks full page first before checking SMID. (2) Removed duplicate price in message formatting. (3) Added extract_promotion() function to detect promotional offers. (4) Added extract_coupon() function to detect coupon badges. (5) Updated build_product_message() to show promotions and coupons with emoji indicators.

