from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import BOT_NAME, AVAILABLE_LANGUAGES
from utils.translations import get_text
from database.sqlite_client import get_or_create_user, get_message_status
from database.credits_client import get_user_credits

# Zabezpieczony import z awaryjnym fallbackiem
try:
    from utils.referral import use_referral_code
except ImportError:
    # Fallback jeśli import nie zadziała
    def use_referral_code(user_id, code):
        """
        Prosta implementacja awaryjnego fallbacku dla use_referral_code
        """
        # Jeśli kod ma format REF123, wyodrębnij ID polecającego
        if code.startswith("REF") and code[3:].isdigit():
            referrer_id = int(code[3:])
            # Sprawdź, czy użytkownik nie używa własnego kodu
            if referrer_id == user_id:
                return False, None
            # Dodanie kredytów zostałoby implementowane tutaj w prawdziwym przypadku
            return True, referrer_id
        return False, None

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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługa komendy /start
    Tworzy lub pobiera użytkownika z bazy danych i wyświetla wiadomość powitalną z menu
    """
    user = update.effective_user
    
    # Usuwamy klawiaturę systemową bez komunikatu
    await update.message.reply_text("", reply_markup=ReplyKeyboardRemove())
    await update.message.delete()
    
    # Sprawdź, czy użytkownik istnieje w bazie
    user_data = get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code
    )
    
    # Ustaw domyślny język
    language = "pl"
    if user_data and 'language' in user_data and user_data['language']:
        language = user_data['language']
    
    # Zapisz język w kontekście
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    
    if user.id not in context.chat_data['user_data']:
        context.chat_data['user_data'][user.id] = {}
    
    context.chat_data['user_data'][user.id]['language'] = language
    
    # Pobierz stan kredytów
    credits = get_user_credits(user.id)
    
    # Utwórz wiadomość powitalną
    welcome_text = f"""Witaj w {BOT_NAME}! 🤖✨

Jestem zaawansowanym botem AI, który pomoże Ci w wielu zadaniach - od odpowiadania na pytania po generowanie obrazów.

Dostępne komendy:
/start - Pokaż tę wiadomość
/credits - Sprawdź saldo kredytów
/buy - Kup pakiet kredytów
/status - Sprawdź stan konta
/newchat - Rozpocznij nową konwersację
/mode - Wybierz tryb czatu
/image [opis] - Wygeneruj obraz
/menu - Pokaż menu główne

Używanie bota:
1. Po prostu wpisz wiadomość, aby otrzymać odpowiedź
2. Użyj przycisków menu, aby uzyskać dostęp do funkcji
3. Możesz przesyłać zdjęcia i dokumenty do analizy

Wsparcie:
Jeśli potrzebujesz pomocy, skontaktuj się z nami: @twojkontaktwsparcia

Twój aktualny stan kredytów: {credits} kredytów

Wybierz opcję z menu poniżej:"""
    
    # Utwórz klawiaturę menu
    keyboard = [
        [
            InlineKeyboardButton("🔄 Tryb czatu", callback_data="menu_section_chat_modes"),
            InlineKeyboardButton("🖼️ Generuj obraz", callback_data="menu_image_generate")
        ],
        [
            InlineKeyboardButton("💰 Kredyty", callback_data="menu_section_credits"),
            InlineKeyboardButton("📂 Historia", callback_data="menu_section_history")
        ],
        [
            InlineKeyboardButton("⚙️ Ustawienia", callback_data="menu_section_settings"),
            InlineKeyboardButton("❓ Pomoc", callback_data="menu_help")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Wyślij wiadomość powitalną z menu
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )

    
    # Utwórz klawiaturę menu
    keyboard = [
        [
            InlineKeyboardButton("🔄 Tryb czatu", callback_data="menu_section_chat_modes"),
            InlineKeyboardButton("🖼️ Generuj obraz", callback_data="menu_image_generate")
        ],
        [
            InlineKeyboardButton("💰 Kredyty", callback_data="menu_section_credits"),
            InlineKeyboardButton("📂 Historia", callback_data="menu_section_history")
        ],
        [
            InlineKeyboardButton("⚙️ Ustawienia", callback_data="menu_section_settings"),
            InlineKeyboardButton("❓ Pomoc", callback_data="menu_help")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Wyślij wiadomość powitalną z menu
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )
    
    # Jeśli użytkownik nie ma jeszcze języka, zaproponuj wybór
    if not user_data or 'language' not in user_data or not user_data['language']:
        return await show_language_selection(update, context)
    
    # Zapisz język w kontekście
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    
    if user.id not in context.chat_data['user_data']:
        context.chat_data['user_data'][user.id] = {}
    
    context.chat_data['user_data'][user.id]['language'] = language
    
    # Pobierz stan kredytów
    credits = get_user_credits(user.id)
    message_status = get_message_status(user.id)
    
    # Przygotowanie wiadomości powitalnej
    welcome_text = get_text("welcome_message", language, bot_name=BOT_NAME)
    welcome_text += f"\n\n{get_text('credits_status', language, credits=credits)}"
    
    # Dodaj informację o pozostałych wiadomościach
    if message_status["messages_left"] > 0:
        welcome_text += f"\nPozostało wiadomości: {message_status['messages_left']}"
    
    # Pobierz dane potrzebne dla menu
    current_mode = get_user_current_mode(context, user.id)
    current_model = get_user_current_model(context, user.id)
    
    # Przygotuj informacje o aktualnym trybie i modelu
    from config import CHAT_MODES, AVAILABLE_MODELS
    mode_name = CHAT_MODES[current_mode]["name"] if current_mode in CHAT_MODES else "Standard"
    model_name = AVAILABLE_MODELS[current_model] if current_model in AVAILABLE_MODELS else "GPT-3.5"
    
    # Utwórz klawiaturę menu
    from handlers.menu_handler import create_main_menu_markup
    reply_markup = create_main_menu_markup(language)
    
    # Wyślij wiadomość powitalną z menu
    message = await update.message.reply_text(
        welcome_text, 
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    
    # Zapisz ID wiadomości menu i stan menu
    from handlers.menu_handler import store_menu_state
    store_menu_state(context, user.id, 'main', message.message_id)

async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla wybór języka przy pierwszym uruchomieniu
    """
    # Utwórz przyciski dla każdego języka
    keyboard = []
    for lang_code, lang_name in AVAILABLE_LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"start_lang_{lang_code}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Użyj neutralnego języka dla pierwszej wiadomości
    welcome_message = f"🌐 Wybierz język / Choose language / Выберите язык:"
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługuje wybór języka przez użytkownika
    """
    query = update.callback_query
    await query.answer()
    
    if not query.data.startswith("start_lang_"):
        return
    
    language = query.data[11:]  # Usuń prefix "start_lang_"
    user_id = query.from_user.id
    
    # Zapisz język w bazie danych
    try:
        from database.sqlite_client import sqlite3, DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET language = ? WHERE id = ?", (language, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Błąd zapisywania języka: {e}")
    
    # Zapisz język w kontekście
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    
    if user_id not in context.chat_data['user_data']:
        context.chat_data['user_data'][user_id] = {}
    
    context.chat_data['user_data'][user_id]['language'] = language
    
    # Pobierz stan kredytów
    credits = get_user_credits(user_id)
    message_status = get_message_status(user_id)
    
    # Przygotowanie wiadomości powitalnej
    welcome_text = get_text("welcome_message", language, bot_name=BOT_NAME)
    welcome_text += f"\n\n{get_text('credits_status', language, credits=credits)}"
    
    # Dodaj informację o pozostałych wiadomościach
    if message_status["messages_left"] > 0:
        welcome_text += f"\nPozostało wiadomości: {message_status['messages_left']}"
    
    # Pobierz dane potrzebne dla menu
    from handlers.menu_handler import get_user_current_mode, get_user_current_model
    current_mode = get_user_current_mode(context, user_id)
    current_model = get_user_current_model(context, user_id)
    
    # Przygotuj informacje o aktualnym trybie i modelu
    from config import CHAT_MODES, AVAILABLE_MODELS
    mode_name = CHAT_MODES[current_mode]["name"] if current_mode in CHAT_MODES else "Standard"
    model_name = AVAILABLE_MODELS[current_model] if current_model in AVAILABLE_MODELS else "GPT-3.5"
    
    # Utwórz klawiaturę menu
    from handlers.menu_handler import create_main_menu_markup
    reply_markup = create_main_menu_markup(language)
    
    # Aktualizuj wiadomość
    message = await query.edit_message_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    
    # Zapisz ID wiadomości menu i stan menu
    from handlers.menu_handler import store_menu_state
    store_menu_state(context, user_id, 'main', message.message_id)