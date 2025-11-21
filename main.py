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
    try:
        api_url = f"{YOURLS_URL}/yourls-api.php"
        url = url.replace('?&', '?')
        
        data = {
            'signature': YOURLS_SIGNATURE,
            'action': 'shorturl',
            'format': 'json',
            'url': url
        }
        
        logger.info(f"Shortening: {url}")
        logger.info(f"API URL: {api_url}")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(api_url, data=data)
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Response: {response.text[:200]}")
            
            try:
                result = response.json()
            except Exception as e:
                logger.error(f"JSON parse error: {e}")
                logger.error(f"Raw: {response.text}")
                return None
            
            logger.info(f"Result: {result}")
            
            if result.get('status') == 'success':
                short = result.get('shorturl')
                logger.info(f"Shortened: {short}")
                return short
            else:
                if 'already exists' in result.get('message', ''):
                    kw = result.get('url', {}).get('keyword')
                    if kw:
                        short = f"{YOURLS_URL}/{kw}"
                        logger.info(f"Exists: {short}")
                        return short
                
                logger.error(f"Error: {result.get('message', 'Unknown')}")
                logger.error(f"Full: {result}")
                return None
                
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return None
```

### CANVAS_NEW_STR
```html
async def shorten_with_yourls(url: str) -> str:
    try:
        api_url = f"{YOURLS_URL}/yourls-api.php"
        url = url.replace('?&', '?')
        
        data = {
            'signature': YOURLS_SIGNATURE,
            'action': 'shorturl',
            'format': 'json',
            'url': url
        }
        
        logger.info(f"Shortening: {url}")
        logger.info(f"API URL: {api_url}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(api_url, data=data)
                logger.info(f"Status: {response.status_code}")
                logger.info(f"Response: {response.text[:200]}")
                
                try:
                    result = response.json()
                except Exception as e:
                    logger.error(f"JSON parse error: {e}")
                    logger.error(f"Raw: {response.text}")
                    logger.warning("YOURLS JSON error - returning original URL")
                    return url
                
                logger.info(f"Result: {result}")
                
                if result.get('status') == 'success':
                    short = result.get('shorturl')
                    logger.info(f"Shortened: {short}")
                    return short
                else:
                    if 'already exists' in result.get('message', ''):
                        kw = result.get('url', {}).get('keyword')
                        if kw:
                            short = f"{YOURLS_URL}/{kw}"
                            logger.info(f"Exists: {short}")
                            return short
                    
                    logger.error(f"Error: {result.get('message', 'Unknown')}")
                    logger.warning("YOURLS error - returning original URL")
                    return url
        
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            logger.error(f"YOURLS timeout/connection error: {e}")
            logger.warning("YOURLS unreachable - returning original URL as fallback")
            return url
                
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        logger.warning("Unexpected error - returning original URL")
        return url
```

# CANVAS_DESCRIPTION
Added YOURLS timeout/connection error handling with fallback. Now returns the original affiliate URL if YOURLS is unreachable or times out, instead of returning None and failing. Catches TimeoutException and ConnectError specifically and returns the unshortened URL as fallback.

