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
async def shorten_with_yourls(url: str) -> str:
    """Shorten URL using YOURLS API"""
    try:
        api_url = f"{YOURLS_URL}/yourls-api.php"
        url = url.replace('?&', '?')
        
        data = {
            'signature': YOURLS_SIGNATURE,
            'action': 'shorturl',
            'format': 'json',
            'url': url
        }
        
        logger.info(f"Shortening URL: {url}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(api_url, data=data)
            logger.info(f"YOURLS HTTP Status: {response.status_code}")
            
            try:
                result = response.json()
            except:
                logger.error("Failed to parse JSON from YOURLS response")
                return None
            
            logger.info(f"YOURLS response: {result}")
            
            if result.get('status') == 'success':
                short_url = result.get('shorturl')
                logger.info(f"Successfully shortened to: {short_url}")
                return short_url
            else:
                if 'already exists' in result.get('message', ''):
                    logger.info("URL already exists in database")
                    keyword = result.get('url', {}).get('keyword')
                    if keyword:
                        short_url = f"{YOURLS_URL}/{keyword}"
                        logger.info(f"Found existing short URL from database: {short_url}")
                        return short_url
                
                logger.error(f"YOURLS error: {result.get('message', 'Unknown error')}")
                return None
                
    except Exception as e:
        logger.error(f"Error shortening URL: {e}")
        return None
```

### CANVAS_NEW_STR
```html
async def shorten_with_yourls(url: str) -> str:
    """Shorten URL using YOURLS API"""
    try:
        api_url = f"{YOURLS_URL}/yourls-api.php"
        url = url.replace('?&', '?')
        
        data = {
            'signature': YOURLS_SIGNATURE,
            'action': 'shorturl',
            'format': 'json',
            'url': url
        }
        
        logger.info(f"Shortening URL: {url}")
        logger.info(f"YOURLS API URL: {api_url}")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(api_url, data=data)
            logger.info(f"YOURLS HTTP Status: {response.status_code}")
            logger.info(f"YOURLS Response Text: {response.text[:200]}")
            
            try:
                result = response.json()
            except Exception as json_err:
                logger.error(f"Failed to parse JSON from YOURLS response: {json_err}")
                logger.error(f"Raw response: {response.text}")
                return None
            
            logger.info(f"YOURLS response: {result}")
            
            if result.get('status') == 'success':
                short_url = result.get('shorturl')
                logger.info(f"Successfully shortened to: {short_url}")
                return short_url
            else:
                if 'already exists' in result.get('message', ''):
                    logger.info("URL already exists in database")
                    keyword = result.get('url', {}).get('keyword')
                    if keyword:
                        short_url = f"{YOURLS_URL}/{keyword}"
                        logger.info(f"Found existing short URL from database: {short_url}")
                        return short_url
                
                logger.error(f"YOURLS error: {result.get('message', 'Unknown error')}")
                logger.error(f"Full YOURLS response: {result}")
                return None
                
    except Exception as e:
        logger.error(f"Error shortening URL: {e}", exc_info=True)
        return None
```

## CANVAS_EDIT_2

### CANVAS_OLD_STR
```html
def extract_price(soup) -> str:
    """Extract price"""
    try:
        price_elem = soup.find('span', {'class': 'a-price-whole'})
        if price_elem:
            return price_elem.get_text(strip=True)
    except:
        pass
    
    return None
```

### CANVAS_NEW_STR
```html
def extract_price(soup) -> str:
    """Extract price with decimal part"""
    try:
        # Try to find the whole price with decimals
        price_container = soup.find('span', {'class': 'a-price'})
        if price_container:
            # Get the full text including decimals
            price_text = price_container.get_text(strip=True)
            # Extract currency and amount
            match = re.search(r'[\d.,€\$]+', price_text)
            if match:
                return match.group(0)
        
        # Fallback to just whole part
        price_elem = soup.find('span', {'class': 'a-price-whole'})
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            # Try to find decimal part next to it
            parent = price_elem.parent
            if parent:
                full_price = parent.get_text(strip=True)
                return full_price
            return price_text
    except Exception as e:
        logger.error(f"Error extracting price: {e}")
    
    return None
```

# CANVAS_DESCRIPTION
Enhanced error logging in shorten_with_yourls function to show raw responses and detailed exception info. Improved extract_price to capture full price including decimals instead of just the whole part. Now logs API URL and full response text for debugging YOURLS connection issues.

