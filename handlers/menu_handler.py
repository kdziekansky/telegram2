from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import CHAT_MODES, AVAILABLE_LANGUAGES
from utils.translations import get_text

# Import z lokalnego referral.py lub definiuj bazowe elementy jeśli import nie działa
try:
    from utils.referral import get_referral_stats, REFERRAL_CREDITS
except ImportError:
    # Fallback, jeśli import się nie powiedzie
    REFERRAL_CREDITS = 50
    
    def get_referral_stats(user_id):
        return {
            'code': f"REF{user_id}",
            'used_count': 0,
            'earned_credits': 0,
            'referred_users': []
        }

def get_user_language(context, user_id):
    """
    Pobiera język użytkownika z kontekstu lub bazy danych
    
    Args:
        context: Kontekst bota
        user_id: ID użytkownika
        
    Returns:
        str: Kod języka (pl, en, ru)
    """
    # Sprawdź, czy język jest zapisany w kontekście
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data'] and 'language' in context.chat_data['user_data'][user_id]:
        return context.chat_data['user_data'][user_id]['language']
    
    # Jeśli nie, pobierz z bazy danych
    try:
        from database.sqlite_client import sqlite3, DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT language FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            # Zapisz w kontekście na przyszłość
            if 'user_data' not in context.chat_data:
                context.chat_data['user_data'] = {}
            
            if user_id not in context.chat_data['user_data']:
                context.chat_data['user_data'][user_id] = {}
            
            context.chat_data['user_data'][user_id]['language'] = result[0]
            return result[0]
    except Exception as e:
        print(f"Błąd pobierania języka z bazy: {e}")
    
    # Domyślny język, jeśli nie znaleziono w bazie
    return "pl"

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla główne menu bota z przyciskami
    """
    user_id = update.effective_user.id
    
    # Pobierz język użytkownika
    language = get_user_language(context, user_id)
    
    # Przygotuj klawiaturę z przyciskami menu
    keyboard = [
        [KeyboardButton(get_text("menu_chat_mode", language))],
        [KeyboardButton(get_text("menu_dialog_history", language))],
        [KeyboardButton(get_text("menu_get_tokens", language))],
        [KeyboardButton(get_text("menu_balance", language)), KeyboardButton(get_text("menu_settings", language))],
        [KeyboardButton(get_text("menu_help", language))]
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await update.message.reply_text(
        get_text("main_menu", language),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługuje wybór opcji z menu
    """
    message_text = update.message.text
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Sprawdź dla wszystkich obsługiwanych języków
    for lang in AVAILABLE_LANGUAGES.keys():
        # Opcja: Tryb czatu
        if message_text == get_text("menu_chat_mode", lang):
            await show_chat_modes(update, context)
            return True
            
        # Opcja: Historia rozmów
        elif message_text == get_text("menu_dialog_history", lang):
            await show_dialog_history(update, context)
            return True
            
        # Opcja: Darmowe tokeny
        elif message_text == get_text("menu_get_tokens", lang):
            await show_referral_program(update, context)
            return True
            
        # Opcja: Saldo (Kredyty)
        elif message_text == get_text("menu_balance", lang):
            # Importuj funkcję dopiero tutaj, aby uniknąć cyklicznych importów
            from handlers.credit_handler import credits_command
            await credits_command(update, context)
            return True
            
        # Opcja: Ustawienia
        elif message_text == get_text("menu_settings", lang):
            await show_settings(update, context)
            return True
            
        # Opcja: Pomoc
        elif message_text == get_text("menu_help", lang):
            await show_help(update, context)
            return True
    
    # Jeśli nie rozpoznano opcji, przekaż obsługę dalej
    return False

async def show_chat_modes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla dostępne tryby czatu jako przyciski
    """
    # Sprawdzenie, czy użytkownik ma uprawnienia
    from database.credits_client import get_user_credits
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    credits = get_user_credits(user_id)
    if credits <= 0:
        await update.message.reply_text(get_text("subscription_expired", language))
        return
    
    # Utwórz przyciski dla dostępnych trybów
    keyboard = []
    for mode_id, mode_info in CHAT_MODES.items():
        keyboard.append([
            InlineKeyboardButton(text=mode_info["name"], callback_data=f"mode_{mode_id}")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text("settings_choose_model", language),
        reply_markup=reply_markup
    )

async def show_dialog_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla historię dialogu lub opcje jej zarządzania
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Pobierz aktywną konwersację
    from database.sqlite_client import get_active_conversation, get_conversation_history
    conversation = get_active_conversation(user_id)
    
    if not conversation:
        await update.message.reply_text(get_text("history_no_conversation", language))
        return
    
    # Pobierz historię konwersacji
    history = get_conversation_history(conversation['id'])
    
    if not history:
        # Brak historii
        keyboard = [[InlineKeyboardButton(get_text("history_delete_button", language), callback_data="history_delete")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            get_text("history_empty", language),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Przygotuj wiadomość z historią
    history_text = f"{get_text('history_title', language)}\n\n"
    
    # Ogranicz do ostatnich 10 wiadomości, aby nie przekroczyć limitu
    for msg in history[-10:]:
        sender = get_text("history_user", language) if msg['is_from_user'] else get_text("history_bot", language)
        content = msg['content']
        
        # Skróć wiadomości, jeśli są za długie
        if len(content) > 100:
            content = content[:97] + "..."
        
        history_text += f"*{sender}*: {content}\n\n"
    
    # Przycisk do usunięcia historii
    keyboard = [[InlineKeyboardButton(get_text("history_delete_button", language), callback_data="history_delete")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        history_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def show_referral_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla informacje o programie referencyjnym
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Pobierz statystyki referencyjne użytkownika
    referral_stats = get_referral_stats(user_id)
    
    # Przygotuj wiadomość
    message = f"{get_text('referral_title', language)}\n\n"
    message += f"{get_text('referral_description', language, credits=REFERRAL_CREDITS)}\n\n"
    message += f"*{get_text('referral_your_code', language)}* `{referral_stats['code']}`\n"
    
    # Możemy dodać link referencyjny, jeśli bot ma nazwę użytkownika
    bot_username = context.bot.username
    if bot_username:
        ref_link = f"https://t.me/{bot_username}?start=ref_{referral_stats['code']}"
        message += f"*{get_text('referral_your_link', language)}* [Link]({ref_link})\n\n"
    else:
        message += "\n"
    
    # Statystyki
    message += f"*{get_text('referral_invited', language)}* {referral_stats['used_count']} {get_text('referral_users', language)}\n"
    message += f"*{get_text('referral_earned', language)}* {referral_stats['earned_credits']} {get_text('referral_credits', language)}\n\n"
    
    # Jak to działa
    message += f"*{get_text('referral_how_to_use', language)}*\n"
    message += f"1. {get_text('referral_step1', language)}\n"
    message += f"2. {get_text('referral_step2', language)}\n"
    message += f"3. {get_text('referral_step3', language, credits=REFERRAL_CREDITS)}\n\n"
    
    # Ostatnio zaproszeni użytkownicy
    if referral_stats['referred_users']:
        message += f"*{get_text('referral_recent_users', language)}*\n"
        for user in referral_stats['referred_users']:
            date = user['date'].split('T')[0] if 'T' in user['date'] else user['date']
            message += f"- {user['name']} ({date})\n"
    
    # Przycisk do udostępniania kodu
    share_text = f"Wypróbuj bota {context.bot.username} i otrzymaj darmowe kredyty! Użyj mojego kodu referencyjnego: {referral_stats['code']}"
    keyboard = [[InlineKeyboardButton(
        get_text("referral_share_button", language), 
        switch_inline_query=share_text
    )]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla ustawienia bota
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    keyboard = [
        [InlineKeyboardButton(get_text("settings_model", language), callback_data="settings_model")],
        [InlineKeyboardButton(get_text("settings_language", language), callback_data="settings_language")],
        [InlineKeyboardButton(get_text("settings_name", language), callback_data="settings_name")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text("settings_title", language),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla pomoc i informacje o bocie
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    help_text = get_text("help_text", language)
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN
    )

# Handler dodatkowych przycisków (ustawienia, historia itp.)
async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługuje callbacki związane z ustawieniami
    """
    query = update.callback_query
    await query.answer()  # Odpowiedz na callback_query, aby usunąć "zegar oczekiwania"
    
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    if query.data == "settings_model":
        # Przekieruj do wyboru modelu
        await show_models_selection(update, context)
        
    elif query.data == "settings_language":
        # Pokazywanie wyboru języka
        await show_language_selection(update, context)
        
    elif query.data.startswith("lang_"):
        # Wybór języka
        selected_lang = query.data[5:]  # Pobierz kod języka (usuń prefix "lang_")
        await change_language(update, context, selected_lang)
        
    elif query.data == "settings_name":
        await query.edit_message_text(
            get_text("settings_change_name", language),
            parse_mode=ParseMode.MARKDOWN
        )
        
    elif query.data.startswith("history_"):
        action = query.data[8:]  # Pobierz akcję (usuń prefix "history_")
        
        if action == "delete":
            # Implementacja usuwania historii
            user_id = query.from_user.id
            # Twórz nową konwersację (efektywnie "usuwając" historię)
            from database.sqlite_client import create_new_conversation
            conversation = create_new_conversation(user_id)
            
            if conversation:
                await query.edit_message_text(
                    get_text("history_deleted", language),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.edit_message_text(
                    "Wystąpił błąd podczas czyszczenia historii.",
                    parse_mode=ParseMode.MARKDOWN
                )

async def show_models_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla wybór modeli AI
    """
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Przekieruj do funkcji show_models z main.py
    # Zaimportuj show_models z głównego pliku dopiero w momencie wywołania
    # żeby uniknąć cyklicznych importów
    try:
        from main import show_models
        
        # Symulujemy update dla funkcji show_models
        class FakeUpdate:
            class FakeMessage:
                def __init__(self, chat_id):
                    self.chat_id = chat_id
                    
                async def reply_text(self, text, **kwargs):
                    await query.edit_message_text(text, **kwargs)
            
            def __init__(self, chat_id):
                self.message = self.FakeMessage(chat_id)
        
        fake_update = FakeUpdate(query.message.chat_id)
        
        # Wymuszamy użycie query.edit_message_text zamiast update.message.reply_text
        await show_models(fake_update, context, edit_message=True, callback_query=query)
    except Exception as e:
        print(f"Błąd podczas pokazywania wyboru modeli: {e}")
        await query.edit_message_text(
            f"Wystąpił błąd podczas ładowania modeli. Spróbuj ponownie.",
            parse_mode=ParseMode.MARKDOWN
        )

async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla wybór języka
    """
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Utwórz przyciski dla każdego języka
    keyboard = []
    for lang_code, lang_name in AVAILABLE_LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        get_text("settings_choose_language", language),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_lang=None):
    """
    Zmienia język dla użytkownika
    """
    query = update.callback_query
    user_id = query.from_user.id
    
    if not selected_lang:
        selected_lang = query.data[5:]  # Pobierz kod języka (usuń prefix "lang_")
    
    # Zapisz język w kontekście użytkownika
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    
    if user_id not in context.chat_data['user_data']:
        context.chat_data['user_data'][user_id] = {}
    
    # Zapisz stary język (do porównania czy się zmienił)
    old_language = context.chat_data['user_data'][user_id].get('language', 'pl')
    
    # Aktualizuj na nowy język
    context.chat_data['user_data'][user_id]['language'] = selected_lang
    
    # Zapisz język do bazy danych
    try:
        from database.sqlite_client import sqlite3, DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET language = ? WHERE id = ?", (selected_lang, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Błąd zapisywania języka: {e}")
    
    # Pobierz przetłumaczoną nazwę języka
    language_name = AVAILABLE_LANGUAGES.get(selected_lang, selected_lang)
    
    # Użyj nowego języka do tłumaczenia komunikatu
    confirmation_message = get_text("language_selected", selected_lang, language_display=language_name)
    restart_suggestion = get_text("restart_suggestion", selected_lang)
    
    # Dodaj sugestię użycia komendy restart
    full_message = f"{confirmation_message}\n\n{restart_suggestion}"
    
    # Tworzę przyciski z prawidłowym callbackiem
    keyboard = [[InlineKeyboardButton(
        get_text("restart_button", selected_lang), 
        callback_data="restart_bot"
    )]]
    
    # Wyświetl komunikat z przyciskiem restartu
    await query.edit_message_text(
        full_message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def set_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ustawia niestandardową nazwę użytkownika
    Użycie: /setname [nazwa]
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Sprawdź, czy podano nazwę
    if not context.args or len(' '.join(context.args)) < 1:
        await update.message.reply_text(get_text("settings_change_name", language))
        return
    
    name = ' '.join(context.args)
    
    # Zapisz nazwę w kontekście użytkownika
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    
    if user_id not in context.chat_data['user_data']:
        context.chat_data['user_data'][user_id] = {}
    
    context.chat_data['user_data'][user_id]['custom_name'] = name
    
    await update.message.reply_text(
        f"Twoja nazwa została zmieniona na: *{name}*",
        parse_mode=ParseMode.MARKDOWN
    )