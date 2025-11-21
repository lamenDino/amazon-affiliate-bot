#!/usr/bin/env python3
"""
Amazon Affiliate Bot for Telegram
Shortens Amazon links and adds affiliate tags using YOURLS
With beautiful product cards featuring images, ratings, and descriptions
"""

import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import re
import json
from urllib.parse import urlencode, parse_qs, urlparse
from telegram import Update, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import httpx
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
YOURLS_URL = os.environ.get("YOURLS_URL", "https://url.nelloonrender.duckdns.org")
YOURLS_SIGNATURE = os.environ.get("YOURLS_SIGNATURE", "def05e4247")
AFFILIATE_TAG = os.environ.get("AFFILIATE_TAG", "ruciferia-21")
PORT = int(os.environ.get("PORT", 10000))

# Validate environment variables
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in environment variables")

logger.info(f"Bot Configuration:")
logger.info(f"  TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:10]}...")
logger.info(f"  YOURLS_URL: {YOURLS_URL}")
logger.info(f"  YOURLS_SIGNATURE: {YOURLS_SIGNATURE}")
logger.info(f"  AFFILIATE_TAG: {AFFILIATE_TAG}")
logger.info(f"  PORT: {PORT}")

# User agents to try
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

# ============================================================================
# Health Check HTTP Server (Required by Render)
# ============================================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for Render's health checks"""
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running')
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def start_health_check_server():
    """Start HTTP server for Render's health checks"""
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"Health check server started on port {PORT}")

# ============================================================================
# URL Extraction and Validation
# ============================================================================

def extract_amazon_url_from_text(text: str) -> str:
    """Extract Amazon URL from text using regex"""
    url_pattern = r'https?://[^\s\)\]]+'
    urls = re.findall(url_pattern, text)
    
    for url in urls:
        url = url.rstrip(')]')
        if is_amazon_url(url):
            logger.info(f"Extracted Amazon URL: {url}")
            return url
    
    return None

async def resolve_short_url(url: str) -> str:
    """Resolve shortened URLs (amzn.eu, etc) to full Amazon URL"""
    try:
        for user_agent in USER_AGENTS:
            headers = {'User-Agent': user_agent}
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    response = await client.get(url, headers=headers, follow_redirects=True)
                    resolved_url = str(response.url)
                    logger.info(f"Resolved {url} to {resolved_url}")
                    return resolved_url
            except:
                continue
        return url
    except Exception as e:
        logger.error(f"Error resolving short URL: {e}")
        return url

def extract_asin_from_url(url: str) -> str:
    """Extract ASIN from any Amazon URL format"""
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    
    match = re.search(r'/gp/product/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    
    match = re.search(r'/d/([A-F0-9]+)', url)
    if match:
        return match.group(1)
    
    return None

def normalize_amazon_url(url: str) -> str:
    """Normalize Amazon URL to remove unnecessary parameters but keep seller/condition info"""
    try:
        url = url.rstrip('/')
        url = url.replace('?&', '?')
        
        asin = extract_asin_from_url(url)
        
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        preserved_params = {}
        if 'smid' in query_params:
            preserved_params['smid'] = query_params['smid'][0]
        if 'condition' in query_params:
            preserved_params['condition'] = query_params['condition'][0]
        if 'psc' in query_params:
            preserved_params['psc'] = query_params['psc'][0]
        
        if asin:
            normalized = f"https://www.amazon.it/dp/{asin}"
            
            if preserved_params:
                params_str = '&'.join([f"{k}={v}" for k, v in preserved_params.items()])
                normalized = f"{normalized}?{params_str}"
            
            logger.info(f"Normalized URL from {url} to {normalized}")
            return normalized
        
        return url
    
    except Exception as e:
        logger.error(f"Error normalizing URL: {e}")
        return url

# ============================================================================
# Amazon Product Scraping
# ============================================================================

async def get_amazon_product_info(url: str) -> dict:
    """Scrape Amazon product information"""
    try:
        normalized_url = normalize_amazon_url(url)
        logger.info(f"Scraping from: {normalized_url}")
        
        for user_agent in USER_AGENTS:
            try:
                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                    response = await client.get(normalized_url, headers=headers)
                    
                    if response.status_code != 200:
                        logger.warning(f"Got status {response.status_code}, trying next user agent")
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    title = extract_title(soup)
                    price = extract_price(soup)
                    rating, reviews_count = extract_rating(soup)
                    image_url = extract_image(soup)
                    description = extract_description(soup)
                    condition_status = extract_condition_status(soup)
                    condition_details = extract_condition_details(soup)
                    
                    logger.info(f"Scraped - Title: {title}, Price: {price}, Condition: {condition_status}")
                    
                    if title and title != 'Prodotto Amazon':
                        return {
                            'title': title,
                            'price': price,
                            'rating': rating,
                            'reviews': reviews_count,
                            'image': image_url,
                            'description': description or 'Scopri il prodotto su Amazon',
                            'condition_status': condition_status,
                            'condition_details': condition_details
                        }
                    
            except Exception as e:
                logger.warning(f"Error with user agent, trying next: {e}")
                continue
        
        logger.warning(f"Could not scrape product info from {normalized_url}")
        return {
            'title': 'Prodotto Amazon',
            'price': None,
            'rating': None,
            'reviews': None,
            'image': None,
            'description': 'Scopri il prodotto su Amazon',
            'condition_status': None,
            'condition_details': None
        }
    
    except Exception as e:
        logger.error(f"Error scraping Amazon product: {e}")
        return {
            'title': 'Prodotto Amazon',
            'price': None,
            'rating': None,
            'reviews': None,
            'image': None,
            'description': 'Scopri il prodotto su Amazon',
            'condition_status': None,
            'condition_details': None
        }

def extract_title(soup) -> str:
    """Extract product title"""
    title_selectors = [
        ('span', {'id': 'productTitle'}),
        ('h1', {'class': 'a-size-large'}),
    ]
    
    for tag, selector in title_selectors:
        elem = soup.find(tag, selector)
        if elem:
            title = elem.get_text(strip=True)
            if title and len(title) > 5:
                return title
    
    return 'Prodotto Amazon'

def extract_price(soup) -> str:
    """Extract price"""
    try:
        price_elem = soup.find('span', {'class': 'a-price-whole'})
        if price_elem:
            return price_elem.get_text(strip=True)
    except:
        pass
    
    return None

def extract_rating(soup) -> tuple:
    """Extract rating and review count"""
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

def extract_image(soup) -> str:
    """Extract product image"""
    image_selectors = [
        {'id': 'landingImage'},
        {'id': 'imageBlockContainer'},
        {'class': 'a-dynamic-image'},
    ]
    
    for selector in image_selectors:
        img_elem = soup.find('img', selector)
        if img_elem:
            image_url = img_elem.get('src')
            if image_url:
                return image_url
    
    return None

def extract_description(soup) -> str:
    """Extract product description"""
    desc_elem = soup.find('div', {'id': 'feature-bullets'})
    if desc_elem:
        features = desc_elem.find_all('li')
        if features:
            description = features[0].get_text(strip=True)
            if len(description) > 100:
                description = description[:97] + "..."
            return description
    
    return 'Scopri il prodotto su Amazon'

def extract_condition_status(soup) -> str:
    """Extract condition status for used items"""
    try:
        for elem in soup.find_all(['span', 'div']):
            text = elem.get_text(strip=True)
            if any(keyword in text for keyword in ['Usato', 'Used', 'Ricondizionato']):
                if any(cond in text for cond in ['condizioni', 'Condition', 'stato']):
                    logger.info(f"Found condition status: {text}")
                    return text
    except:
        pass
    
    return None

def extract_condition_details(soup) -> str:
    """Extract detailed condition information"""
    try:
        details = []
        for elem in soup.find_all(['p', 'li', 'div']):
            text = elem.get_text(strip=True)
            if any(ind in text for ind in ['graffi', 'scratch', 'usura', 'wear', 'ammaccature', 'dent']):
                if 10 < len(text) < 200:
                    details.append(text)
        
        if details:
            logger.info(f"Found condition details: {details[0]}")
            return details[0]
    except:
        pass
    
    return None

# ============================================================================
# Telegram Bot Functions
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    welcome_message = (
        "👋 Ciao! Sono il tuo Bot per i Link Amazon con Affiliazione\n\n"
        "📝 Cosa faccio:\n"
        "• 📸 Scarico l'immagine del prodotto\n"
        "• ⭐ Mostro valutazioni e recensioni\n"
        "• 💬 Aggiungo una descrizione breve\n"
        "• 🔗 Accorcio il link con tag affiliazione\n"
        "• 🔄 Rilevo articoli usati e condizioni\n\n"
        "🚀 Basta inviare un link Amazon e io farò il resto!\n\n"
        f"💰 Tag affiliazione: `{AFFILIATE_TAG}`"
    )
    await update.message.reply_text(welcome_message)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URL messages"""
    text = update.message.text
    user = update.message.from_user
    
    original_url = extract_amazon_url_from_text(text)
    
    if not original_url:
        logger.info(f"No Amazon URL found in message from {user.username}: {text}")
        return
    
    status_msg = await update.message.reply_text("⏳ Sto elaborando il link...")
    
    try:
        logger.info(f"Received URL from {user.username}: {original_url}")
        
        url = original_url
        if is_short_amazon_url(url):
            await status_msg.edit_text("🔗 Sto risolvendo il link accorciato...")
            url = await resolve_short_url(url)
            logger.info(f"Resolved to: {url}")
        
        normalized_url = normalize_amazon_url(url)
        logger.info(f"Normalized URL: {normalized_url}")
        
        affiliate_url = add_affiliate_tag(normalized_url, AFFILIATE_TAG)
        logger.info(f"Affiliate URL: {affiliate_url}")
        
        await status_msg.edit_text("📸 Scarico info prodotto...")
        product_info = await get_amazon_product_info(normalized_url)
        
        await status_msg.edit_text("🔗 Sto accorciando il link...")
        short_url = await shorten_with_yourls(affiliate_url)
        
        if not short_url:
            await status_msg.edit_text("❌ Errore nell'accorciamento del link.\nRiprova più tardi.")
            return
        
        logger.info(f"Successfully shortened to: {short_url}")
        
        message = build_product_message(product_info, short_url)
        
        await status_msg.delete()
        
        try:
            await update.message.delete()
        except:
            pass
        
        if product_info.get('image'):
            try:
                await update.message.chat.send_photo(
                    photo=product_info['image'],
                    caption=message,
                    parse_mode='HTML'
                )
                logger.info("Sent photo with message")
            except Exception as e:
                logger.warning(f"Could not send photo: {e}, sending text only")
                fallback_msg = f"<b>{product_info.get('title', 'Prodotto')}</b>\n\n<b><a href='{short_url}'>🔗 Acquista</a></b>"
                try:
                    await update.message.chat.send_message(fallback_msg, parse_mode='HTML')
                except:
                    await update.message.chat.send_message(f"Link: {short_url}")
        else:
            logger.info("No image found, sending text message only")
            try:
                await update.message.chat.send_message(message, parse_mode='HTML')
            except:
                fallback_msg = f"<b>{product_info.get('title', 'Prodotto')}</b>\n\n<b><a href='{short_url}'>🔗 Acquista</a></b>"
                await update.message.chat.send_message(fallback_msg, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        try:
            await status_msg.edit_text("❌ Si è verificato un errore.\nRiprova più tardi.")
        except:
            pass

def build_product_message(product_info: dict, short_url: str) -> str:
    """Build compact message optimized for Telegram"""
    title = product_info.get('title', 'Prodotto Amazon')
    if len(title) > 50:
        title = title[:47] + "..."
    
    price = product_info.get('price', '')
    rating = product_info.get('rating', '')
    condition_status = product_info.get('condition_status', '')
    
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

def is_amazon_url(url: str) -> bool:
    """Check if URL is from Amazon"""
    amazon_domains = [
        "amazon.it", "amazon.com", "amazon.co.uk", "amazon.de",
        "amazon.fr", "amazon.es", "amazon.ca", "amazon.in",
        "amazon.co.jp", "amazon.com.br",
        "amzn.eu", "amzn.com", "amzn.to", "amzlink.to"
    ]
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        logger.info(f"URL domain check: {domain}")
        return any(d in domain for d in amazon_domains)
    except Exception as e:
        logger.error(f"Error checking URL domain: {e}")
        return False

def is_short_amazon_url(url: str) -> bool:
    """Check if URL is a short Amazon URL"""
    short_domains = ["amzn.eu", "amzn.com", "amzn.to", "amzlink.to"]
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        return any(d in domain for d in short_domains)
    except:
        return False

def add_affiliate_tag(url: str, tag: str) -> str:
    """Add affiliate tag to Amazon URL"""
    url = url.rstrip('/')
    url = re.sub(r'[?&]tag=[^&]*', '', url)
    separator = '&' if '?' in url else '?'
    return f"{url}{separator}tag={tag}"

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

def main():
    """Main function to run the bot"""
    start_health_check_server()
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
