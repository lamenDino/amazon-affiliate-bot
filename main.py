#!/usr/bin/env python3
"""
Amazon Affiliate Bot for Telegram
Shortens Amazon links and adds affiliate tags using YOURLS
"""

import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import re
import json
from urllib.parse import urlencode, parse_qs, urlparse
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import httpx
from bs4 import BeautifulSoup

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
YOURLS_URL = os.environ.get("YOURLS_URL", "https://url.nelloonrender.duckdns.org")
YOURLS_SIGNATURE = os.environ.get("YOURLS_SIGNATURE", "def05e4247")
AFFILIATE_TAG = os.environ.get("AFFILIATE_TAG", "ruciferia-21")
PORT = int(os.environ.get("PORT", 10000))

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set")

logger.info(f"Bot Configuration:")
logger.info(f"  TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:10]}...")
logger.info(f"  YOURLS_URL: {YOURLS_URL}")
logger.info(f"  AFFILIATE_TAG: {AFFILIATE_TAG}")
logger.info(f"  PORT: {PORT}")

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running')
    
    def log_message(self, format, *args):
        pass

def start_health_check_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"Health check server started on port {PORT}")

def extract_amazon_url_from_text(text: str) -> str:
    url_pattern = r'https?://[^\s\)\]]+'
    urls = re.findall(url_pattern, text)
    for url in urls:
        url = url.rstrip(')]')
        if is_amazon_url(url):
            logger.info(f"Extracted Amazon URL: {url}")
            return url
    return None

async def resolve_short_url(url: str) -> str:
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
    try:
        url = url.rstrip('/')
        url = url.replace('?&', '?')
        asin = extract_asin_from_url(url)
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        preserved_params = {}
        for param in ['smid', 'condition', 'psc', 'aod', 'm']:
            if param in query_params:
                preserved_params[param] = query_params[param][0]
        
        if asin:
            normalized = f"https://www.amazon.it/dp/{asin}"
            if preserved_params:
                params_str = '&'.join([f"{k}={v}" for k, v in preserved_params.items()])
                normalized = f"{normalized}?{params_str}"
            logger.info(f"Normalized URL: {normalized}")
            return normalized
        return url
    except Exception as e:
        logger.error(f"Error normalizing URL: {e}")
        return url

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

def extract_title(soup) -> str:
    for selector in [{'id': 'productTitle'}, {'class': 'a-size-large'}]:
        elem = soup.find('span', selector)
        if elem:
            title = elem.get_text(strip=True)
            if title and len(title) > 5:
                return title
    return 'Prodotto Amazon'

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

def extract_image(soup) -> str:
    for selector in [{'id': 'landingImage'}, {'id': 'imageBlockContainer'}, {'class': 'a-dynamic-image'}]:
        img_elem = soup.find('img', selector)
        if img_elem:
            image_url = img_elem.get('src')
            if image_url:
                return image_url
    return None

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
        
        page_text = soup.get_text()
        if 'Amazon Seconda mano' in page_text:
            logger.info("Found 'Amazon Seconda mano'")
            return "Usato - Venduto da Amazon Seconda mano"
        
        if smid in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info("Amazon official seller")
            return "Nuovo - Venduto da Amazon"
        
        if smid and smid not in ['A11IL2PNWYJU7H', 'AQKAJJZN6SNBQ']:
            logger.info("Third party seller")
            return "Usato - Venduto da terzo"
    except Exception as e:
        logger.error(f"Error detecting condition: {e}")
    
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome = (
        "👋 Ciao! Sono il tuo Bot per i Link Amazon con Affiliazione\n\n"
        "📝 Cosa faccio:\n"
        "• 📸 Scarico l'immagine\n"
        "• ⭐ Mostro valutazioni\n"
        "• 💬 Aggiungo descrizione\n"
        "• 🔗 Accorcio il link\n"
        "• 🔄 Rilevo articoli usati\n\n"
        "🚀 Invia un link Amazon!\n\n"
        f"💰 Tag: `{AFFILIATE_TAG}`"
    )
    await update.message.reply_text(welcome)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user = update.message.from_user
    
    original_url = extract_amazon_url_from_text(text)
    
    if not original_url:
        logger.info(f"No Amazon URL found")
        return
    
    status_msg = await update.message.reply_text("⏳ Elaborando...")
    
    try:
        logger.info(f"Received URL from {user.username}: {original_url}")
        
        url = original_url
        if is_short_amazon_url(url):
            await status_msg.edit_text("🔗 Risolvendo...")
            url = await resolve_short_url(url)
        
        normalized_url = normalize_amazon_url(url)
        affiliate_url = add_affiliate_tag(normalized_url, AFFILIATE_TAG)
        
        await status_msg.edit_text("📸 Scaricando...")
        product_info = await get_amazon_product_info(normalized_url)
        
        await status_msg.edit_text("🔗 Accorciando...")
        short_url = await shorten_with_yourls(affiliate_url)
        
        if not short_url:
            await status_msg.edit_text("❌ Errore accorciamento.\nRiprova.")
            return
        
        logger.info(f"Shortened to: {short_url}")
        
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
                logger.info("Sent photo")
            except Exception as e:
                logger.warning(f"Photo error: {e}")
                fallback = f"<b>{product_info.get('title', 'Prodotto')}</b>\n\n<b><a href='{short_url}'>🔗 Acquista</a></b>"
                try:
                    await update.message.chat.send_message(fallback, parse_mode='HTML')
                except:
                    await update.message.chat.send_message(f"Link: {short_url}")
        else:
            logger.info("No image")
            try:
                await update.message.chat.send_message(message, parse_mode='HTML')
            except:
                fallback = f"<b>{product_info.get('title', 'Prodotto')}</b>\n\n<b><a href='{short_url}'>🔗 Acquista</a></b>"
                await update.message.chat.send_message(fallback, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error: {e}")
        try:
            await status_msg.edit_text("❌ Errore.\nRiprova.")
        except:
            pass

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

def is_amazon_url(url: str) -> bool:
    domains = ["amazon.it", "amazon.com", "amzn.eu", "amzn.to", "amzlink.to"]
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        return any(d in domain for d in domains)
    except:
        return False

def is_short_amazon_url(url: str) -> bool:
    short_domains = ["amzn.eu", "amzn.com", "amzn.to", "amzlink.to"]
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        return any(d in domain for d in short_domains)
    except:
        return False

def add_affiliate_tag(url: str, tag: str) -> str:
    url = url.rstrip('/')
    url = re.sub(r'[?&]tag=[^&]*', '', url)
    separator = '&' if '?' in url else '?'
    return f"{url}{separator}tag={tag}"

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

def main():
    start_health_check_server()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    logger.info("Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
