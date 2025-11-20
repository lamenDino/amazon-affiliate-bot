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
# Amazon Product Scraping
# ============================================================================

async def get_amazon_product_info(url: str) -> dict:
    """Scrape Amazon product information"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = None
            title_elem = soup.find('span', {'id': 'productTitle'})
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            # Extract price
            price = None
            price_elem = soup.find('span', {'class': 'a-price-whole'})
            if price_elem:
                price = price_elem.get_text(strip=True)
            
            # Extract rating
            rating = None
            rating_elem = soup.find('span', {'class': 'a-star-small'})
            if rating_elem:
                rating_text = rating_elem.find('span', {'class': 'a-icon-star-small'})
                if rating_text:
                    rating = rating_text.get_text(strip=True).split()[0]
            
            # Extract number of reviews
            reviews_count = None
            reviews_elem = soup.find('span', {'id': 'acrCustomerReviewText'})
            if reviews_elem:
                reviews_count = reviews_elem.get_text(strip=True)
            
            # Extract image
            image_url = None
            img_elem = soup.find('img', {'id': 'landingImage'})
            if img_elem:
                image_url = img_elem.get('src')
            
            # Extract description (first few lines from product description)
            description = None
            desc_elem = soup.find('div', {'id': 'feature-bullets'})
            if desc_elem:
                features = desc_elem.find_all('li')
                if features:
                    description = features[0].get_text(strip=True)
                    # Limit to 100 characters
                    if len(description) > 100:
                        description = description[:97] + "..."
            
            return {
                'title': title or 'Prodotto Amazon',
                'price': price,
                'rating': rating,
                'reviews': reviews_count,
                'image': image_url,
                'description': description or 'Scopri il prodotto su Amazon'
            }
    
    except Exception as e:
        logger.error(f"Error scraping Amazon product: {e}")
        return {
            'title': 'Prodotto Amazon',
            'price': None,
            'rating': None,
            'reviews': None,
            'image': None,
            'description': 'Scopri il prodotto su Amazon'
        }

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
        "• 🔗 Accorcio il link con tag affiliazione\n\n"
        "🚀 Basta inviare un link Amazon e io farò il resto!\n\n"
        f"💰 Tag affiliazione: `{AFFILIATE_TAG}`"
    )
    await update.message.reply_text(welcome_message)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URL messages"""
    url = update.message.text
    user = update.message.from_user
    
    # Acknowledge message
    status_msg = await update.message.reply_text(
        "⏳ Sto elaborando il link...",
    )
    
    try:
        # Check if URL is Amazon
        if not is_amazon_url(url):
            await status_msg.edit_text(
                "❌ Questo non è un link Amazon!\n\n"
                "Invia un link di Amazon.it e farò il resto."
            )
            return
        
        logger.info(f"Received URL from {user.username}: {url}")
        
        # Add affiliate tag
        affiliate_url = add_affiliate_tag(url, AFFILIATE_TAG)
        logger.info(f"Affiliate URL: {affiliate_url}")
        
        # Get product info
        await status_msg.edit_text("📸 Scarico info prodotto...")
        product_info = await get_amazon_product_info(affiliate_url)
        
        # Shorten with YOURLS
        await status_msg.edit_text("🔗 Sto accorciando il link...")
        short_url = await shorten_with_yourls(affiliate_url)
        
        if not short_url:
            await status_msg.edit_text(
                "❌ Errore nell'accorciamento del link.\n"
                "Riprova più tardi."
            )
            return
        
        logger.info(f"Successfully shortened to: {short_url}")
        
        # Build beautiful message
        message = build_product_message(
            product_info=product_info,
            short_url=short_url,
            username=user.username or user.first_name
        )
        
        # Delete status message
        await status_msg.delete()
        
        # Send product with image if available
        if product_info.get('image'):
            try:
                await update.message.reply_photo(
                    photo=product_info['image'],
                    caption=message,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.warning(f"Could not send image: {e}")
                await update.message.reply_text(message, parse_mode='HTML')
        else:
            await update.message.reply_text(message, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        await status_msg.edit_text(
            "❌ Si è verificato un errore.\n"
            "Riprova più tardi."
        )

def build_product_message(product_info: dict, short_url: str, username: str) -> str:
    """Build a beautiful product message"""
    
    title = product_info.get('title', 'Prodotto Amazon')
    # Truncate title if too long
    if len(title) > 60:
        title = title[:57] + "..."
    
    price = product_info.get('price', '')
    rating = product_info.get('rating', '')
    reviews = product_info.get('reviews', '')
    description = product_info.get('description', '')
    
    # Build rating display
    rating_display = ''
    if rating:
        rating_display = f"⭐ {rating}"
        if reviews:
            rating_display += f" ({reviews})"
        rating_display += "\n"
    
    # Build price display
    price_display = ''
    if price:
        price_display = f"💰 <b>{price}</b>\n"
    
    message = (
        f"<b>👤 {username}</b> ha condiviso:\n\n"
        f"<b>{title}</b>\n"
        f"{price_display}"
        f"{rating_display}"
        f"📝 {description}\n\n"
        f"🔗 <b><a href='{short_url}'>Clicca qui per acquistare</a></b>"
    )
    
    return message

def is_amazon_url(url: str) -> bool:
    """Check if URL is from Amazon"""
    amazon_domains = [
        "amazon.it", "amazon.com", "amazon.co.uk", "amazon.de",
        "amazon.fr", "amazon.es", "amazon.ca", "amazon.in",
        "amazon.co.jp", "amazon.com.br"
    ]
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        
        logger.info(f"URL domain check: {domain}")
        
        return any(d in domain for d in amazon_domains)
    except Exception as e:
        logger.error(f"Error checking URL domain: {e}")
        return False

def add_affiliate_tag(url: str, tag: str) -> str:
    """Add affiliate tag to Amazon URL"""
    # Remove existing tag if present
    url = re.sub(r'[?&]tag=[^&]*', '', url)
    
    # Add new tag
    separator = '&' if '?' in url else '?'
    affiliate_url = f"{url}{separator}tag={tag}"
    
    return affiliate_url

async def shorten_with_yourls(url: str) -> str:
    """Shorten URL using YOURLS API"""
    try:
        api_url = f"{YOURLS_URL}/yourls-api.php"
        params = {
            'signature': YOURLS_SIGNATURE,
            'action': 'shorturl',
            'format': 'json',
            'url': url
        }
        
        logger.info(f"Shortening URL via {api_url}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"YOURLS response: {data}")
            
            if data.get('status') == 'success':
                return data.get('shorturl')
            else:
                logger.error(f"YOURLS error: {data}")
                return None
                
    except httpx.HTTPStatusError as e:
        logger.error(f"Request error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error shortening URL: {e}")
        return None

def main():
    """Main function to run the bot"""
    
    # Start health check server
    start_health_check_server()
    
    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Start bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
