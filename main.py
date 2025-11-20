#!/usr/bin/env python3
"""
Amazon Affiliate Link Bot for Telegram (Render Edition)
Converts Amazon links to shortened affiliate links using YOURLS
Optimized for deployment on Render
"""

import os
import re
import sys
import logging
import requests
from urllib.parse import urlparse, parse_qs, urlunparse
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YOURLS_URL = os.getenv("YOURLS_URL", "http://localhost:8082")
YOURLS_SIGNATURE = os.getenv("YOURLS_SIGNATURE")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG", "ruciferia-21")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


def add_affiliate_tag_to_url(url: str, tag: str) -> str:
    """
    Add affiliate tag parameter to Amazon URL
    Handles both new and old URL formats
    """
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query, keep_blank_values=True)
        
        # Remove existing tag if present
        query_params.pop('tag', None)
        query_params.pop('linkCode', None)
        
        # Add new affiliate tag
        query_params['tag'] = [tag]
        
        # Rebuild query string (flatten the list values)
        new_query = '&'.join(
            f"{key}={value[0] if isinstance(value, list) else value}"
            for key, value in query_params.items()
        )
        
        # Reconstruct URL
        new_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        return new_url
    except Exception as e:
        logger.error(f"Error adding affiliate tag: {e}")
        return url


def shorten_with_yourls(long_url: str, custom_alias: str = None) -> str:
    """
    Shorten a URL using YOURLS API
    Optimized for Render with better error handling
    """
    try:
        # YOURLS API endpoint
        api_url = f"{YOURLS_URL}/yourls-api.php"
        
        # Prepare parameters
        params = {
            'signature': YOURLS_SIGNATURE,
            'action': 'shorturl',
            'format': 'json',
            'url': long_url,
        }
        
        if custom_alias:
            params['keyword'] = custom_alias
        
        logger.info(f"Shortening URL: {long_url} via {api_url}")
        
        # Make request to YOURLS API with timeout
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"YOURLS response: {data}")
        
        if data.get('status') == 'success':
            short_url = data.get('shorturl')
            logger.info(f"Successfully shortened to: {short_url}")
            return short_url
        else:
            error_msg = data.get('message', 'Unknown error')
            logger.error(f"YOURLS API error: {error_msg}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("Timeout connecting to YOURLS - service may be initializing")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to YOURLS: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error shortening URL: {e}")
        return None


def is_amazon_link(url: str) -> bool:
    """
    Check if the URL is an Amazon link
    Supports all Amazon marketplaces worldwide
    """
    amazon_domains = [
        'amazon.com', 'amazon.it', 'amazon.es', 'amazon.fr', 'amazon.de',
        'amazon.co.uk', 'amazon.ca', 'amazon.co.jp', 'amazon.in', 'amazon.com.br',
        'amazon.com.au', 'amazon.nl', 'amazon.se', 'amazon.pl', 'amazon.com.mx',
        'amazon.ae', 'amazon.sg'
    ]
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        is_amazon = any(amazon_domain in domain for amazon_domain in amazon_domains)
        logger.info(f"URL domain check: {domain} - is_amazon: {is_amazon}")
        return is_amazon
    except Exception as e:
        logger.error(f"Error checking Amazon link: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    welcome_text = """
🔗 **Amazon Affiliate Link Bot**

Invia un link Amazon e riceverai il link accorciato con il tuo tag di affiliazione!

**Comandi:**
/start - Mostra questo messaggio
/help - Aiuto

**Esempio:**
Invia: `https://www.amazon.it/Smartphone-MediaTek-Dimensity-processore/dp/B0FHBS428L/`

Riceverai il link accorciato con affiliazione! ✨
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command handler"""
    help_text = """
📖 **Aiuto**

Questo bot trasforma i link Amazon in link di affiliazione accorciati.

**Come usarlo:**
1. Copia un link da Amazon
2. Invialo al bot
3. Riceverai un link accorciato con il tuo codice di affiliazione

**Tag di affiliazione utilizzato:** `{}`

**Formati supportati:**
Amazon.it, Amazon.com, Amazon.es, Amazon.fr, Amazon.de, Amazon.co.uk, e molti altri!

Per problemi, contatta lo sviluppatore.
    """.format(AFFILIATE_TAG)
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages - process Amazon links"""
    text = update.message.text
    logger.info(f"Received message: {text[:100]}")
    
    # Check if message contains a URL
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    
    if not urls:
        await update.message.reply_text(
            "❌ Non ho trovato alcun link nel messaggio.\n\n"
            "Invia un link Amazon e riceverai il link di affiliazione accorciato!"
        )
        return
    
    # Process each URL found
    for url in urls:
        logger.info(f"Processing URL: {url}")
        
        if not is_amazon_link(url):
            await update.message.reply_text(
                f"❌ Questo non sembra un link Amazon:\n`{url}`",
                parse_mode='Markdown'
            )
            continue
        
        # Show processing message
        processing_msg = await update.message.reply_text("⏳ Sto elaborando il link...")
        
        try:
            # Add affiliate tag
            affiliate_url = add_affiliate_tag_to_url(url, AFFILIATE_TAG)
            logger.info(f"Affiliate URL: {affiliate_url}")
            
            # Shorten with YOURLS
            short_url = shorten_with_yourls(affiliate_url)
            
            if short_url:
                # Format response as Markdown link
                response = f"✅ Link di affiliazione creato:\n\n[{short_url}]({short_url})"
                await processing_msg.edit_text(response, parse_mode='Markdown')
                logger.info(f"Successfully shortened to: {short_url}")
            else:
                await processing_msg.edit_text(
                    "⚠️ Errore nella creazione del link accorciato.\n"
                    "Verifica che YOURLS sia configurato correttamente.\n"
                    "Prova di nuovo tra qualche secondo."
                )
                logger.error("Failed to shorten URL with YOURLS")
        
        except Exception as e:
            logger.error(f"Error processing URL: {e}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ Errore durante l'elaborazione:\n`{str(e)}`",
                parse_mode='Markdown'
            )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}", exc_info=True)


def main():
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not set in environment variables")
        sys.exit(1)
    
    if not YOURLS_SIGNATURE:
        logger.error("YOURLS_SIGNATURE not set in environment variables")
        sys.exit(1)
    
    logger.info("=" * 50)
    logger.info("Starting Amazon Affiliate Bot")
    logger.info(f"YOURLS URL: {YOURLS_URL}")
    logger.info(f"Affiliate Tag: {AFFILIATE_TAG}")
    logger.info("=" * 50)
    
    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot is running and listening for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
