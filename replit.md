# Telegram Feedback Bot

## Overview

This is a Telegram feedback bot built with Python that provides a structured way for users to submit feedback, questions, complaints, and suggestions through an interactive menu system. The bot categorizes user messages into different types and forwards them to designated owners/administrators. All messages are handled by administrators through a menu system - no AI functionality. It uses the python-telegram-bot library for Telegram API integration and implements a conversation-based flow for collecting user input.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Structure
- **Modular Design**: The application is split into separate modules for configuration (`config.py`), message handlers (`handlers.py`), bot initialization (`bot.py`), and main execution (`main.py`)
- **Conversation Handler Pattern**: Uses ConversationHandler from python-telegram-bot to manage multi-step user interactions and state management
- **Inline Keyboard Interface**: Implements an inline keyboard menu system for category selection and navigation

### Message Flow
- **All Chats**: Users select from 8 predefined categories through inline keyboard buttons, all messages are forwarded to two owners/admins
- **No AI**: All user interactions are handled by human administrators only
- **State Management**: The bot tracks conversation states for menu navigation
- **Admin-Only System**: All messages → administrators (no AI responses)

### Configuration Management
- **Environment Variables**: Bot token and owner ID are loaded from environment variables with fallback defaults
- **Centralized Config**: All bot settings, categories, and instructions are centralized in `config.py` for easy maintenance
- **Localization Ready**: Category names and instructions are stored in dictionaries, making localization straightforward

### Error Handling and Logging
- **Comprehensive Logging**: Structured logging throughout the application using Python's logging module
- **Configuration Validation**: Startup validation ensures required environment variables are properly set
- **Graceful Shutdown**: Proper handling of keyboard interrupts and unexpected errors

## External Dependencies

### Telegram Bot API
- **python-telegram-bot**: Primary library for Telegram Bot API integration
- **Webhook Support**: Architecture supports both polling and webhook modes for message handling

### Runtime Environment
- **Python 3.7+**: Requires modern Python with asyncio support
- **Environment Variables**: Depends on BOT_TOKEN and OWNER_ID environment variables for configuration
- **No Database**: Currently uses in-memory state management through the telegram bot framework's context system

### Deployment Requirements
- **Telegram Bot Token**: Requires a valid bot token from @BotFather
- **Owner Telegram ID**: Requires the Telegram user ID of the bot owner/administrator for message forwarding