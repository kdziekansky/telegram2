from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import CHAT_MODES, AVAILABLE_LANGUAGES, AVAILABLE_MODELS, CREDIT_COSTS
from utils.translations import get_text
from database.credits_client import get_user_credits

# Funkcje pomocnicze

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

def get_user_current_mode(context, user_id):
    """Pobiera aktualny tryb czatu użytkownika"""
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data']:
        user_data = context.chat_data['user_data'][user_id]
        if 'current_mode' in user_data and user_data['current_mode'] in CHAT_MODES:
            return user_data['current_mode']
    return "no_mode"

def get_user_current_model(context, user_id):
    """Pobiera aktualny model AI użytkownika"""
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data']:
        user_data = context.chat_data['user_data'][user_id]
        if 'current_model' in user_data and user_data['current_model'] in AVAILABLE_MODELS:
            return user_data['current_model']
    return "gpt-3.5-turbo"  # Domyślny model

def store_menu_state(context, user_id, state, message_id=None):
    """
    Zapisuje stan menu dla użytkownika
    
    Args:
        context: Kontekst bota
        user_id: ID użytkownika
        state: Stan menu (np. 'main', 'settings', 'chat_modes')
        message_id: ID wiadomości menu (opcjonalnie)
    """
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    
    if user_id not in context.chat_data['user_data']:
        context.chat_data['user_data'][user_id] = {}
    
    context.chat_data['user_data'][user_id]['menu_state'] = state
    
    if message_id:
        context.chat_data['user_data'][user_id]['menu_message_id'] = message_id

def get_menu_state(context, user_id):
    """
    Pobiera stan menu dla użytkownika
    
    Args:
        context: Kontekst bota
        user_id: ID użytkownika
        
    Returns:
        str: Stan menu lub 'main' jeśli brak
    """
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data'] and 'menu_state' in context.chat_data['user_data'][user_id]:
        return context.chat_data['user_data'][user_id]['menu_state']
    return 'main'

def get_menu_message_id(context, user_id):
    """
    Pobiera ID wiadomości menu dla użytkownika
    
    Args:
        context: Kontekst bota
        user_id: ID użytkownika
        
    Returns:
        int: ID wiadomości lub None jeśli brak
    """
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data'] and 'menu_message_id' in context.chat_data['user_data'][user_id]:
        return context.chat_data['user_data'][user_id]['menu_message_id']
    return None

# Funkcje generujące menu

def create_main_menu_markup(language):
    """
    Tworzy klawiaturę dla głównego menu
    
    Args:
        language: Kod języka
        
    Returns:
        InlineKeyboardMarkup: Klawiatura z przyciskami
    """
    keyboard = [
        [
            InlineKeyboardButton("💬 " + get_text("menu_chat_mode", language), callback_data="menu_section_chat_modes"),
            InlineKeyboardButton("🖼️ " + get_text("image_generate", language, default="Generuj obraz"), callback_data="menu_image_generate")
        ],
        [
            InlineKeyboardButton("📊 " + get_text("menu_credits", language, default="Kredyty"), callback_data="menu_section_credits"),
            InlineKeyboardButton("📂 " + get_text("menu_dialog_history", language), callback_data="menu_section_history")
        ],
        [
            InlineKeyboardButton("⚙️ " + get_text("menu_settings", language), callback_data="menu_section_settings"),
            InlineKeyboardButton("❓ " + get_text("menu_help", language), callback_data="menu_help")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

# ... [pozostałe funkcje create_*_menu_markup]

# Funkcje obsługujące menu

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla główne menu bota z przyciskami inline
    """
    user_id = update.effective_user.id
    
    # Upewnij się, że klawiatura systemowa jest usunięta
    await update.message.reply_text("Usuwam klawiaturę...", reply_markup=ReplyKeyboardRemove())
    
    # Pobierz język użytkownika
    language = get_user_language(context, user_id)
    
    # Pobierz informacje o statusie użytkownika
    credits = get_user_credits(user_id)
    current_mode = get_user_current_mode(context, user_id)
    current_model = get_user_current_model(context, user_id)
    
    # Przygotuj informacje o aktualnym trybie i modelu
    mode_name = CHAT_MODES[current_mode]["name"] if current_mode in CHAT_MODES else "Standard"
    model_name = AVAILABLE_MODELS[current_model] if current_model in AVAILABLE_MODELS else "GPT-3.5"
    
    # Przygotuj tekst statusu
    status_text = f"""📋 *{get_text("main_menu", language)}*

*{get_text("status", language, default="Status")}:*
💰 {get_text("credits", language)}: *{credits}*
💬 {get_text("current_mode", language, default="Aktualny tryb")}: *{mode_name}*
🤖 {get_text("current_model", language, default="Model")}: *{model_name}*

{get_text("select_option", language, default="Wybierz opcję z menu poniżej:")}
"""
    
    # Utwórz klawiaturę menu
    reply_markup = create_main_menu_markup(language)
    
    # Wyślij menu
    message = await update.message.reply_text(
        status_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Zapisz ID wiadomości menu i stan menu
    store_menu_state(context, user_id, 'main', message.message_id)

async def update_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, menu_state, markup=None):
    """
    Aktualizuje istniejące menu
    
    Args:
        update: Obiekt Update
        context: Kontekst bota
        menu_state: Nowy stan menu
        markup: Klawiatura menu (opcjonalnie)
    """
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Pobierz informacje o statusie użytkownika
    credits = get_user_credits(user_id)
    current_mode = get_user_current_mode(context, user_id)
    current_model = get_user_current_model(context, user_id)
    
    # Przygotuj informacje o aktualnym trybie i modelu
    mode_name = CHAT_MODES[current_mode]["name"] if current_mode in CHAT_MODES else "Standard"
    model_name = AVAILABLE_MODELS[current_model] if current_model in AVAILABLE_MODELS else "GPT-3.5"
    
    # Utwórz tekst menu na podstawie stanu
    if menu_state == 'main':
        menu_title = get_text("main_menu", language)
        menu_text = f"""📋 *{menu_title}*

*{get_text("status", language, default="Status")}:*
💰 {get_text("credits", language)}: *{credits}*
💬 {get_text("current_mode", language, default="Aktualny tryb")}: *{mode_name}*
🤖 {get_text("current_model", language, default="Model")}: *{model_name}*

{get_text("select_option", language, default="Wybierz opcję z menu poniżej:")}
"""
        if not markup:
            markup = create_main_menu_markup(language)
    
    # ... [pozostałe stany menu - zachowaj istniejącą implementację]
    
    # Aktualizuj wiadomość menu
    await query.edit_message_text(
        text=menu_text,
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Zapisz nowy stan menu
    store_menu_state(context, user_id, menu_state)

async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługuje wszystkie callbacki związane z menu
    
    Returns:
        bool: True jeśli callback został obsłużony, False w przeciwnym razie
    """
    query = update.callback_query
    
    # Sprawdź, czy to callback związany z menu
    if not query.data.startswith("menu_") and not query.data.startswith("buy_package_"):
        return False
    
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Obsługa nawigacji menu
    if query.data == "menu_back_main":
        await query.answer()
        await update_menu(update, context, 'main')
        return True
    
    # ... [pozostałe obsługi menu - zachowaj istniejącą implementację]
    
    return False

# ... [pozostałe funkcje obsługujące akcje menu]

# Funkcja do wyświetlania menu kontekstowego po wiadomości użytkownika
async def show_contextual_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_message):
    """
    Wyświetla menu kontekstowe na podstawie treści wiadomości użytkownika
    
    Args:
        update: Obiekt Update
        context: Kontekst bota
        user_message: Treść wiadomości użytkownika
        
    Returns:
        bool: True jeśli menu zostało wyświetlone, False w przeciwnym razie
    """
    user_id = update.effective_user.id
    
    # Sprawdź, czy użytkownik ma włączone menu kontekstowe
    # (można dodać opcję wyłączenia w ustawieniach)
    context_enabled = True
    
    if not context_enabled:
        return False
    
    # Wygeneruj menu kontekstowe
    markup = create_contextual_menu_markup(context, user_id, user_message)
    
    if markup:
        # Wyślij menu kontekstowe jako odpowiedź na wiadomość użytkownika
        language = get_user_language(context, user_id)
        
        await update.message.reply_text(
            get_text("contextual_options", language, default="Opcje kontekstowe:"),
            reply_markup=markup,
            reply_to_message_id=update.message.message_id
        )
        return True
    
    return False

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
    
    # Wyślij potwierdzenie z przyciskiem menu
    keyboard = [[InlineKeyboardButton("📋 " + get_text("menu", language, default="Menu"), callback_data="menu_back_main")]]
    
    await update.message.reply_text(
        f"{get_text('name_changed', language, default='Twoja nazwa została zmieniona na')}: *{name}*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )