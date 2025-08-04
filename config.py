import os

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN",
                      "8366607921:AAGfoLBzDW4x7UBZp6lbOt3SiUima0UTrGY")


# Support for multiple owners - add both owner IDs
OWNER_IDS = [
    int(os.getenv("OWNER_ID", "7017555176")),  # First owner
    int(os.getenv("OWNER_ID_2","6118037678")),  # Second owner (replace with actual ID)
    int(os.getenv("OWNER_ID_3","869751612")),  # Second owner (replace with actual ID)
    int(os.getenv("OWNER_ID_4","7489475288"))  # Second owner (replace with actual ID)
]

# Backward compatibility
OWNER_ID = OWNER_IDS[0]

# Categories for the menu
CATEGORIES = {
    "joining": "Вступление во флуд",
    "questions": "Интересующие вопросы",
    "criticism": "Критика",
    "suggestions": "Предложения",
    "unions": "Союзы",
    "rest": "Рест",
    "complaints": "Жалобы",
    "other": "Прочее"
}

# Instructions for each category
CATEGORY_INSTRUCTIONS = {
    "joining":
    "Ознакомьтесь в инфо @HOSTELFM с правилами и напишите роль,которую желаете занять ",
    "questions": "Напишите ваш вопрос, и мы постараемся на него ответить.",
    "criticism":
    "Поделитесь вашей критикой или замечаниями. Мы ценим обратную связь.",
    "suggestions":
    "Расскажите о ваших предложениях по улучшению нашей работы.",
    "unions": "Ознакомьтесь с информацией о союзах в в инфо @HOSTELFM и скиньте инфо/информацию для обратной связи.",
    "rest": "Напишите вашу роль, срок реста и причину.",
    "complaints": "Опишите вашу жалобу. Мы обязательно рассмотрим ее.",
    "other": "Напишите ваше сообщение по любому другому вопросу."
}
