#!/usr/bin/env python3
import logging
import sys
from bot import create_bot
from config import BOT_TOKEN, OWNER_ID
from keep_alive import keep_alive
keep_alive()


# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def validate_config():
    """Validate bot configuration."""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN is not set! Please set the BOT_TOKEN environment variable.")
        return False
    
    if not OWNER_ID or OWNER_ID == 123456789:
        logger.error("OWNER_ID is not set! Please set the OWNER_ID environment variable.")
        return False
    
    return True

def main():
    """Main function to run the bot."""
    logger.info("Starting Telegram Feedback Bot...")
    
    # Start keep-alive web server first
    keep_alive()
    
    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed. Exiting...")
        sys.exit(1)
    
    # Create and run bot
    bot = create_bot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)
