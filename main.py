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
def detect_seller_condition(url: str, soup) -> str:
    """Detect if item is new or used based on seller SMID"""
    try:
        # Amazon official seller SMIDs (new items)
        amazon_smids = [
            'A11IL2PNWYJU7H',  # Amazon.it official
            'AQKAJJZN6SNBQ',   # Amazon.it marketplace
            'A1HO9729ND375Y',  # Could be third-party - check URL
        ]
        
        # Extract SMID from URL
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        smid = query_params.get('smid', [''])[0]
        
        logger.info(f"Detected SMID: {smid}")
        
        # If SMID is in Amazon official list, check if it's actually from Amazon
        if smid in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info("Detected as NEW item - Official Amazon seller")
            return "Nuovo - Venduto da Amazon"
        
        # Try to find seller info in page
        seller_section = soup.find('div', {'id': 'merchant-info'})
        if seller_section:
            seller_text = seller_section.get_text(strip=True)
            logger.info(f"Seller info: {seller_text}")
            
            if 'Amazon' in seller_text and 'Warehouse' not in seller_text:
                return "Nuovo - Venduto da Amazon"
            elif 'Warehouse' in seller_text or 'Ricondizionato' in seller_text:
                return "Ricondizionato - Venduto da Amazon"
        
        # Look for condition indicators in page
        for elem in soup.find_all(['span', 'div']):
            text = elem.get_text(strip=True)
            
            # Check for explicit new/used indicators
            if 'Nuovo' in text or 'New' in text:
                if any(keyword in text for keyword in ['Venduto', 'Sold', 'da']):
                    logger.info(f"Found NEW indicator: {text}")
                    return "Nuovo - Venduto da terzo"
            
            if 'Usato' in text or 'Used' in text or 'Ricondizionato' in text:
                if any(cond in text for cond in ['condizioni', 'Condition', 'stato', 'State']):
                    logger.info(f"Found USED indicator: {text}")
                    return text
        
        # Default: if has SMID that's not Amazon, it's likely third party (could be new or used)
        if smid and smid not in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info("Detected as likely USED or third-party seller")
            return "Usato - Venduto da terzo"
    
    except Exception as e:
        logger.error(f"Error detecting condition: {e}")
    
    return None
```

### CANVAS_NEW_STR
```html
def detect_seller_condition(url: str, soup) -> str:
    """Detect if item is new or used based on seller SMID and page content"""
    try:
        # Extract SMID from URL
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        smid = query_params.get('smid', [''])[0]
        
        logger.info(f"Detected SMID: {smid}")
        
        # FIRST: Check for "Amazon Seconda mano" indicator - ALWAYS means used
        page_text = soup.get_text()
        if 'Amazon Seconda mano' in page_text or 'Venduto da Amazon Seconda mano' in page_text:
            logger.info("Found 'Amazon Seconda mano' - USED item")
            return "Usato - Venduto da Amazon Seconda mano"
        
        # If SMID is in Amazon official list, it's new
        if smid in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info("Detected as NEW item - Official Amazon seller")
            return "Nuovo - Venduto da Amazon"
        
        # Try to find seller info in page
        seller_section = soup.find('div', {'id': 'merchant-info'})
        if seller_section:
            seller_text = seller_section.get_text(strip=True)
            logger.info(f"Seller info: {seller_text}")
            
            if 'Amazon Seconda mano' in seller_text:
                logger.info("Found seller as Amazon Seconda mano - USED")
                return "Usato - Venduto da Amazon Seconda mano"
            
            if 'Amazon' in seller_text and 'Warehouse' not in seller_text and 'Seconda mano' not in seller_text:
                return "Nuovo - Venduto da Amazon"
            elif 'Warehouse' in seller_text or 'Ricondizionato' in seller_text:
                return "Ricondizionato - Venduto da Amazon"
        
        # Look for condition indicators in page
        for elem in soup.find_all(['span', 'div']):
            text = elem.get_text(strip=True)
            
            # Check for "Venduto da Amazon Seconda mano" link
            if 'Venduto da' in text and 'Amazon Seconda mano' in text:
                logger.info(f"Found Amazon Seconda mano seller: {text}")
                return "Usato - Venduto da Amazon Seconda mano"
            
            # Check for explicit new/used indicators
            if 'Nuovo' in text or 'New' in text:
                if any(keyword in text for keyword in ['Venduto', 'Sold', 'da']):
                    logger.info(f"Found NEW indicator: {text}")
                    return "Nuovo - Venduto da terzo"
            
            if 'Usato' in text or 'Used' in text or 'Ricondizionato' in text:
                if any(cond in text for cond in ['condizioni', 'Condition', 'stato', 'State']):
                    logger.info(f"Found USED indicator: {text}")
                    return text
        
        # Default: if has SMID that's not Amazon, it's likely third party
        if smid and smid not in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info("Detected as likely USED or third-party seller")
            return "Usato - Venduto da terzo"
    
    except Exception as e:
        logger.error(f"Error detecting condition: {e}")
    
    return None
```

# CANVAS_DESCRIPTION
Enhanced detect_seller_condition to explicitly check for "Amazon Seconda mano" text on the page. Now detects used items sold by Amazon's used marketplace, returning "Usato - Venduto da Amazon Seconda mano" when this pattern is found in the page content or seller section.

