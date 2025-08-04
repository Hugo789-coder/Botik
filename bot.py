import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, Filters
from config import BOT_TOKEN
from handlers import (start_command, button_callback, handle_user_message,
                      cancel_conversation, help_command, dialogs_command,
                      handle_owner_reply, handle_direct_message,
                      WAITING_FOR_MESSAGE)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramBot:

    def __init__(self):
        """Initialize the Telegram bot."""
        self.updater = Updater(token=BOT_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.setup_handlers()

    def setup_handlers(self):
        """Set up all bot handlers."""

        # Conversation handler for collecting user messages
        conversation_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(button_callback)],
            states={
                WAITING_FOR_MESSAGE: [
                    MessageHandler(Filters.text & ~Filters.command,
                                   handle_user_message),
                    CallbackQueryHandler(button_callback)
                ]
            },
            fallbacks=[
                CommandHandler("cancel", cancel_conversation),
                CallbackQueryHandler(button_callback)
            ],
            per_message=False)

        # Add handlers to dispatcher
        self.dispatcher.add_handler(CommandHandler("start", start_command))
        self.dispatcher.add_handler(CommandHandler("help", help_command))
        self.dispatcher.add_handler(CommandHandler("dialogs", dialogs_command))
        self.dispatcher.add_handler(conversation_handler)

        # Handle owner replies to users
        self.dispatcher.add_handler(
            MessageHandler(Filters.reply & Filters.text & ~Filters.command,
                           handle_owner_reply))

        # Handle direct messages and group messages (AI works only in groups)
        self.dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command,
                           handle_direct_message))

        # Handle callback queries that are not part of conversation
        self.dispatcher.add_handler(CallbackQueryHandler(button_callback))

        logger.info("Bot handlers set up successfully")

    def run(self):
        """Run the bot using polling."""
        logger.info("Starting bot...")

        try:
            # Start polling
            self.updater.start_polling()
            logger.info("Bot started successfully")

            # Keep the bot running
            self.updater.idle()

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            raise

    def run_sync(self):
        """Run the bot in sync mode (for backwards compatibility)."""
        self.run()


def create_bot():
    """Factory function to create a bot instance."""
    return TelegramBot()
