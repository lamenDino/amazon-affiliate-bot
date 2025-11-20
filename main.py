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
def is_amazon_url(url: str) -> bool:
    """Check if URL is from Amazon"""
    amazon_domains = [
        "amazon.it", "amazon.com", "amazon.co.uk", "amazon.de",
        "amazon.fr", "amazon.es", "amazon.ca", "amazon.in",
        "amazon.co.jp", "amazon.com.br",
        "amzn.eu", "amzn.com", "amzn.to"
    ]
```

### CANVAS_NEW_STR
```html
def is_amazon_url(url: str) -> bool:
    """Check if URL is from Amazon"""
    amazon_domains = [
        "amazon.it", "amazon.com", "amazon.co.uk", "amazon.de",
        "amazon.fr", "amazon.es", "amazon.ca", "amazon.in",
        "amazon.co.jp", "amazon.com.br",
        "amzn.eu", "amzn.com", "amzn.to", "amzlink.to"
    ]
```

## CANVAS_EDIT_2

### CANVAS_OLD_STR
```html
def is_short_amazon_url(url: str) -> bool:
    """Check if URL is a short Amazon URL"""
    short_domains = ["amzn.eu", "amzn.com", "amzn.to"]
```

### CANVAS_NEW_STR
```html
def is_short_amazon_url(url: str) -> bool:
    """Check if URL is a short Amazon URL"""
    short_domains = ["amzn.eu", "amzn.com", "amzn.to", "amzlink.to"]
```

# CANVAS_DESCRIPTION
Added support for amzlink.to shortener. Now recognizes and processes amzlink.to shortened URLs in addition to existing Amazon shorteners (amzn.eu, amzn.com, amzn.to).
