from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import CHAT_MODES
from utils.translations import get_text
from database.credits_client import get_user_credits
from handlers.menu_handler import get_user_language

async def show_modes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pokazuje dostępne tryby czatu"""
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Sprawdź, czy użytkownik ma kredyty
    credits = get_user_credits(user_id)
    if credits <= 0:
        await update.message.reply_text(get_text("subscription_expired", language))
        return
    
    # Utwórz przyciski dla dostępnych trybów
    keyboard = []
    for mode_id, mode_info in CHAT_MODES.items():
        # Użyj tłumaczeń z translations.py zamiast hardkodowanych tekstów
        mode_name = get_text(f"chat_mode_{mode_id}", language, default=mode_info['name'])
        keyboard.append([
            InlineKeyboardButton(
                text=f"{mode_name} ({mode_info['credit_cost']} {get_text('credit', language)})", 
                callback_data=f"mode_{mode_id}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text("select_chat_mode", language),
        reply_markup=reply_markup
    )


async def handle_mode_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa wyboru trybu czatu"""
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    await query.answer()  # Odpowiedz na callback_query, aby usunąć "zegar oczekiwania"
    
    # Sprawdź, czy callback zaczyna się od "mode_"
    if query.data.startswith("mode_"):
        mode_id = query.data[5:]  # Pobierz ID trybu (usuń prefix "mode_")
        
        # Sprawdź, czy tryb istnieje
        if mode_id not in CHAT_MODES:
            await query.edit_message_text(get_text("model_not_available", language))
            return
        
        # Zapisz wybrany tryb w kontekście użytkownika
        if 'user_data' not in context.chat_data:
            context.chat_data['user_data'] = {}
        
        if user_id not in context.chat_data['user_data']:
            context.chat_data['user_data'][user_id] = {}
        
        context.chat_data['user_data'][user_id]['current_mode'] = mode_id
        
        # Jeśli tryb ma określony model, ustaw go również
        if "model" in CHAT_MODES[mode_id]:
            context.chat_data['user_data'][user_id]['current_model'] = CHAT_MODES[mode_id]["model"]
        
        mode_name = CHAT_MODES[mode_id]["name"]
        mode_description = CHAT_MODES[mode_id]["prompt"]
        credit_cost = CHAT_MODES[mode_id]["credit_cost"]
        
        # Skróć opis, jeśli jest zbyt długi
        if len(mode_description) > 100:
            short_description = mode_description[:97] + "..."
        else:
            short_description = mode_description
        
        await query.edit_message_text(
            f"Wybrany tryb: *{mode_name}*\n"
            f"Koszt: *{credit_cost}* kredyt(ów) za wiadomość\n\n"
            f"Opis: _{short_description}_\n\n"
            f"Możesz teraz zadać pytanie w wybranym trybie.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Utwórz nową konwersację dla wybranego trybu
        from database.sqlite_client import create_new_conversation
        create_new_conversation(user_id)