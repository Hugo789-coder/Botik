from flask import Flask
from threading import Thread
import logging

# Set up logging
logger = logging.getLogger(__name__)

app = Flask('')

@app.route('/')
def home():
    """Simple health check endpoint."""
    return "Telegram Bot is alive and running! 🤖"

@app.route('/status')
def status():
    """Bot status endpoint."""
    return {
        "status": "running",
        "message": "Hostel Bot is online",
        "service": "telegram-feedback-bot"
    }

@app.route('/health')
def health():
    """Health check for monitoring services."""
    return "OK"

def run():
    """Run the Flask web server."""
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")

def keep_alive():
    """Start the keep-alive web server in a separate thread."""
    logger.info("Starting keep-alive web server...")
    t = Thread(target=run)
    t.daemon = True  # Dies when main thread dies
    t.start()
    logger.info("Keep-alive web server started on port 5000")