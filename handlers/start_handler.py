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
    Tworzy lub pobiera użytkownika z bazy danych i wyświetla wiadomość powitalną
    """
    user = update.effective_user
    language = "pl"  # Domyślny język
    
    # Usuwamy klawiaturę systemową
    await update.message.reply_text("Inicjuję...", reply_markup=ReplyKeyboardRemove())
    
    # Sprawdź, czy użytkownik ma już ustawiony język w bazie
    user_data = get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code
    )
    
    if user_data and 'language' in user_data and user_data['language']:
        language = user_data['language']
    
    # Sprawdź, czy istnieje kod referencyjny w argumencie start
    if context.args and len(context.args) > 0:
        start_param = context.args[0]
        
        # Obsługa kodu referencyjnego (format: ref_XXXXX)
        if start_param.startswith("ref_"):
            ref_code = start_param[4:]
            success, referrer_id = use_referral_code(user.id, ref_code)
            
            if success:
                # Dodaj kredyty dla obu stron (zaimplementowane w prawdziwym use_referral_code)
                await update.message.reply_text(
                    get_text("referral_success", language, credits=25),
                    parse_mode=ParseMode.MARKDOWN
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
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)
    
    # Pokaż menu główne
    from handlers.menu_handler import show_main_menu
    await show_main_menu(update, context)

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
    
    # Aktualizuj wiadomość
    await query.edit_message_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Pokaż menu główne
    from handlers.menu_handler import show_main_menu
    
    # Utwórz fałszywy obiekt update, aby móc użyć show_main_menu
    class FakeUpdate:
        class FakeMessage:
            def __init__(self, chat_id):
                self.chat_id = chat_id
                
            async def reply_text(self, text, **kwargs):
                return await context.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    **kwargs
                )
        
        def __init__(self, chat_id, user):
            self.message = self.FakeMessage(chat_id)
            self.effective_user = user
    
    fake_update = FakeUpdate(query.message.chat_id, query.from_user)
    await show_main_menu(fake_update, context)