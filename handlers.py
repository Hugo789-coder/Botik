import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from config import CATEGORIES, CATEGORY_INSTRUCTIONS, OWNER_IDS
# AI module removed - all messages go to admins

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_MESSAGE = 1
IN_DIALOG = 2

# Global storage for active dialogs
# Format: {user_id: {'admin_id': admin_id, 'category': category}}
active_dialogs = {}

def start_command(update: Update, context: CallbackContext) -> None:
    """Handle the /start command and show the main menu."""
    keyboard = []
    
    # Create inline keyboard with category buttons
    for key, value in CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(value, callback_data=key)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🤖 Добро пожаловать!\n\n"
        "Выберите категорию вашего обращения из меню ниже:"
    )
    
    if update.message:
        update.message.reply_text(welcome_text, reply_markup=reply_markup)

def button_callback(update: Update, context: CallbackContext) -> int:
    """Handle button callbacks from the inline keyboard."""
    query = update.callback_query
    if query:
        query.answer()
        
        category = query.data
        
        if category in CATEGORIES:
            # Store the selected category in user context
            context.user_data['selected_category'] = category
            
            # Get instruction for the selected category
            instruction = CATEGORY_INSTRUCTIONS.get(category, "Напишите ваше сообщение.")
            
            # Create back button
            keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            response_text = (
                f"📝 Категория: {CATEGORIES[category]}\n\n"
                f"{instruction}\n\n"
                "Отправьте ваше сообщение:"
            )
            
            query.edit_message_text(response_text, reply_markup=reply_markup)
            return WAITING_FOR_MESSAGE
        
        elif category == "back_to_menu":
            # End any active dialog and return to main menu
            user = update.effective_user
            if user and user.id in active_dialogs:
                del active_dialogs[user.id]
            
            keyboard = []
            for key, value in CATEGORIES.items():
                keyboard.append([InlineKeyboardButton(value, callback_data=key)])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_text = (
                "🤖 Главное меню\n\n"
                "Выберите категорию вашего обращения:"
            )
            
            query.edit_message_text(welcome_text, reply_markup=reply_markup)
            return ConversationHandler.END
        
        elif category == "end_dialog":
            # End active dialog
            user = update.effective_user
            if user and user.id in active_dialogs:
                admin_id = active_dialogs[user.id]['admin_id']
                del active_dialogs[user.id]
                
                # Notify admin about dialog end
                try:
                    context.bot.send_message(
                        chat_id=admin_id,
                        text=f"💬 Пользователь {user.first_name} ({user.id}) завершил диалог."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id} about dialog end: {e}")
                
                # Notify other admins that dialog is ended and user is available
                for other_admin_id in OWNER_IDS:
                    if other_admin_id != admin_id:
                        try:
                            context.bot.send_message(
                                chat_id=other_admin_id,
                                text=f"✅ Диалог с пользователем {user.first_name} ({user.id}) завершен. Пользователь снова доступен для новых обращений."
                            )
                        except Exception as e:
                            logger.error(f"Failed to notify admin {other_admin_id} about dialog end: {e}")
                
                query.edit_message_text(
                    "✅ Диалог завершен.\n\n"
                    "Спасибо за обращение! При необходимости используйте /start для нового обращения."
                )
            else:
                query.edit_message_text("❌ Активный диалог не найден.")
            return ConversationHandler.END
    
    return ConversationHandler.END

def handle_user_message(update: Update, context: CallbackContext) -> int:
    """Handle user messages and forward them to owners."""
    user = update.effective_user
    if not user or not update.message or not update.message.text:
        return ConversationHandler.END
        
    message_text = update.message.text
    user_name = f"{user.first_name}{' ' + user.last_name if user.last_name else ''}"
    
    # In private chats (conversation flow), all messages go to admins
    # AI only works in groups, not in private conversation flow
    selected_category = 'other'
    if context.user_data:
        selected_category = context.user_data.get('selected_category', 'other')
    category_name = CATEGORIES.get(selected_category, 'Прочее')
    
    # Create message to forward to owners with unique ID for replies
    message_id = f"msg_{user.id}_{update.message.message_id}"
    forward_message = (
        f"📨 Новое обращение #{message_id}\n\n"
        f"👤 От: {user.first_name}"
        f"{' ' + user.last_name if user.last_name else ''}\n"
        f"🆔 ID: {user.id}\n"
        f"👤 Username: @{user.username if user.username else 'не указан'}\n"
        f"📂 Категория: {category_name}\n\n"
        f"💬 Сообщение:\n{message_text}\n\n"
        f"📋 Для ответа пользователю ответьте на это сообщение"
    )
    
    try:
        # Forward message to all owners
        for owner_id in OWNER_IDS:
            try:
                sent_message = context.bot.send_message(
                    chat_id=owner_id,
                    text=forward_message
                )
                # Store mapping for replies
                context.bot_data[f"reply_{sent_message.message_id}"] = {
                    'user_id': user.id,
                    'original_message_id': message_id
                }
            except Exception as e:
                logger.error(f"Failed to send message to owner {owner_id}: {e}")
        
        # Send confirmation to user
        confirmation_text = (
            "✅ Спасибо за обращение!\n\n"
            "Ваше сообщение было отправлено администраторам. "
            "Ожидайте ответа!"
        )
        
        update.message.reply_text(confirmation_text)
        
        logger.info(f"Message from user {user.id} ({user.username}) forwarded to owners")
        
    except Exception as e:
        logger.error(f"Failed to forward message to owners: {e}")
        
        error_text = (
            "❌ Произошла ошибка при отправке сообщения.\n"
            "Пожалуйста, попробуйте позже."
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            update.message.reply_text(error_text, reply_markup=reply_markup)
    
    # Clear the selected category
    context.user_data.clear()
    return ConversationHandler.END

def cancel_conversation(update: Update, context: CallbackContext) -> int:
    """Cancel the current conversation."""
    if update.message:
        update.message.reply_text("❌ Операция отменена.")
    context.user_data.clear()
    return ConversationHandler.END

def help_command(update: Update, context: CallbackContext) -> None:
    """Handle the /help command."""
    user = update.effective_user
    
    if user and user.id in OWNER_IDS:
        # Admin help
        help_text = (
            "🤖 Помощь для администраторов\n\n"
            "Команды:\n"
            "/start - Показать главное меню\n"
            "/help - Показать эту справку\n"
            "/dialogs - Показать активные диалоги\n\n"
            "Как работать с диалогами:\n"
            "1. Пользователь отправляет обращение\n"
            "2. Отвечайте на сообщение (reply) для начала диалога\n"
            "3. Только первый ответивший админ ведет диалог\n"
            "4. Остальные админы получают уведомления\n"
            "5. Пользователь может закончить диалог кнопкой"
        )
    else:
        # User help
        help_text = (
            "🤖 Помощь по использованию бота\n\n"
            "Команды:\n"
            "/start - Показать главное меню\n"
            "/help - Показать эту справку\n\n"
            "Как использовать:\n"
            "1. Выберите категорию обращения\n"
            "2. Напишите ваше сообщение\n"
            "3. Сообщение будет отправлено администраторам\n\n"
            "Доступные категории:\n"
            "• Вступление во флуд\n"
            "• Интересующие вопросы\n"
            "• Критика\n"
            "• Предложения\n"
            "• Союзы\n"
            "• Рест\n"
            "• Жалобы\n"
            "• Прочее"
        )
    
    if update.message:
        update.message.reply_text(help_text)

def dialogs_command(update: Update, context: CallbackContext) -> None:
    """Show active dialogs to admin."""
    user = update.effective_user
    if not user or user.id not in OWNER_IDS:
        return
    
    if not active_dialogs:
        update.message.reply_text("📭 Активных диалогов нет.")
        return
    
    dialog_list = "💬 Активные диалоги:\n\n"
    for user_id, dialog_info in active_dialogs.items():
        admin_id = dialog_info['admin_id']
        category = dialog_info.get('category', 'other')
        category_name = CATEGORIES.get(category, 'Прочее')
        
        dialog_list += (
            f"👤 Пользователь: {user_id}\n"
            f"👨‍💼 Администратор: {admin_id}\n"
            f"📂 Категория: {category_name}\n"
            f"{'🟢 Ваш диалог' if admin_id == user.id else '🔴 Диалог коллеги'}\n\n"
        )
    
    update.message.reply_text(dialog_list)

def handle_owner_reply(update: Update, context: CallbackContext) -> None:
    """Handle replies from owners to user messages."""
    user = update.effective_user
    if not user or user.id not in OWNER_IDS:
        return
    
    if not update.message or not update.message.reply_to_message:
        return
    
    reply_to_message_id = update.message.reply_to_message.message_id
    reply_data = context.bot_data.get(f"reply_{reply_to_message_id}")
    
    if not reply_data:
        update.message.reply_text("❌ Не удалось найти исходное сообщение пользователя.")
        return
    
    user_id = reply_data['user_id']
    message_id = reply_data['original_message_id']
    reply_text = update.message.text
    
    # Check if user already has active dialog with another admin
    if user_id in active_dialogs and active_dialogs[user_id]['admin_id'] != user.id:
        existing_admin_id = active_dialogs[user_id]['admin_id']
        update.message.reply_text(
            f"⚠️ Пользователь уже ведет диалог с администратором {existing_admin_id}.\n"
            f"Дождитесь завершения диалога или свяжитесь с коллегой."
        )
        return
    
    try:
        # Start or continue dialog session
        active_dialogs[user_id] = {
            'admin_id': user.id,
            'category': reply_data.get('category', 'other')
        }
        
        # Send reply to user with dialog controls
        response_message = (
            f"📬 Ответ от администратора:\n\n"
            f"{reply_text}\n\n"
            f"💬 Диалог начат! Можете продолжить общение."
        )
        
        # Create dialog control buttons
        keyboard = [
            [InlineKeyboardButton("✅ Завершить диалог", callback_data="end_dialog")],
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_message(
            chat_id=user_id,
            text=response_message,
            reply_markup=reply_markup
        )
        
        # Notify other admins about started dialog
        for admin_id in OWNER_IDS:
            if admin_id != user.id:
                try:
                    context.bot.send_message(
                        chat_id=admin_id,
                        text=f"💬 Администратор {user.first_name} ({user.id}) начал диалог с пользователем {user_id}."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id} about dialog start: {e}")
        
        # Confirm to owner
        update.message.reply_text("✅ Ответ отправлен пользователю! Диалог начат. Другие админы уведомлены.")
        
        logger.info(f"Owner {user.id} started dialog with user {user_id} for message {message_id}")
        
    except Exception as e:
        logger.error(f"Failed to send reply to user {user_id}: {e}")
        update.message.reply_text("❌ Ошибка при отправке ответа пользователю.")

def handle_dialog_message(update: Update, context: CallbackContext) -> None:
    """Handle messages in active dialog."""
    user = update.effective_user
    if not user or not update.message or not update.message.text:
        return
    
    # Check if user is in active dialog
    if user.id not in active_dialogs:
        return
    
    dialog_info = active_dialogs[user.id]
    admin_id = dialog_info['admin_id']
    message_text = update.message.text
    
    try:
        # Forward message to admin
        forward_message = (
            f"💬 Продолжение диалога\n\n"
            f"👤 От: {user.first_name}"
            f"{' ' + user.last_name if user.last_name else ''}\n"
            f"🆔 ID: {user.id}\n"
            f"👤 Username: @{user.username if user.username else 'не указан'}\n\n"
            f"💬 Сообщение:\n{message_text}\n\n"
            f"📋 Ответьте на это сообщение для продолжения диалога"
        )
        
        sent_message = context.bot.send_message(
            chat_id=admin_id,
            text=forward_message
        )
        
        # Store mapping for admin replies
        context.bot_data[f"reply_{sent_message.message_id}"] = {
            'user_id': user.id,
            'original_message_id': f"dialog_{user.id}_{update.message.message_id}",
            'category': dialog_info['category']
        }
        
        # Confirm to user
        confirmation_text = "✅ Сообщение отправлено администратору!"
        
        # Add dialog control buttons
        keyboard = [
            [InlineKeyboardButton("✅ Завершить диалог", callback_data="end_dialog")],
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(confirmation_text, reply_markup=reply_markup)
        
        logger.info(f"Dialog message from user {user.id} forwarded to admin {admin_id}")
        
    except Exception as e:
        logger.error(f"Failed to forward dialog message: {e}")
        update.message.reply_text("❌ Ошибка при отправке сообщения администратору.")

def handle_direct_message(update: Update, context: CallbackContext) -> None:
    """Handle direct messages outside of conversation."""
    user = update.effective_user
    if not user or not update.message or not update.message.text:
        return
    
    chat = update.effective_chat
    
    # Check if user is in active dialog
    if user.id in active_dialogs:
        handle_dialog_message(update, context)
        return
    
    # For private chats, redirect to menu
    if chat and chat.type == 'private':
        update.message.reply_text("Привет! Для обращения к администратору используйте /start")
    
    # For group chats, bot doesn't respond automatically (no AI)
    # Users in groups should use /start to contact admins
