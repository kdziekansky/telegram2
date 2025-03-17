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
    """
    keyboard = [
        [
            InlineKeyboardButton(get_text("menu_chat_mode", language), callback_data="menu_section_chat_modes"),
            InlineKeyboardButton(get_text("image_generate", language), callback_data="menu_image_generate")
        ],
        [
            InlineKeyboardButton(get_text("menu_credits", language), callback_data="menu_section_credits"),
            InlineKeyboardButton(get_text("menu_dialog_history", language), callback_data="menu_section_history")
        ],
        [
            InlineKeyboardButton(get_text("menu_settings", language), callback_data="menu_section_settings"),
            InlineKeyboardButton(get_text("menu_help", language), callback_data="menu_help")
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
    status_text = f"""*{get_text("main_menu", language)}*

*{get_text("status", language)}:*
{get_text("credits", language)}: *{credits}*
{get_text("current_mode", language)}: *{mode_name}*
{get_text("current_model", language)}: *{model_name}*

{get_text("select_option", language, default="Wybierz opcję z menu poniżej:")}"""
    
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

{get_text("select_option", language, default="Wybierz opcję z menu poniżej:")}"""
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

async def handle_contextual_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługuje callbacki związane z opcjami menu kontekstowego
    
    Returns:
        bool: True jeśli callback został obsłużony, False w przeciwnym razie
    """
    query = update.callback_query
    
    # Sprawdź, czy to callback menu kontekstowego
    if not query.data.startswith("context_"):
        return False
    
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    await query.answer()  # Odpowiedź, aby usunąć zegar oczekiwania
    
    # Obsługa różnych opcji menu kontekstowego
    if query.data == "context_generate_image":
        # Pobierz oryginalny tekst wiadomości jako prompt
        original_message = query.message.reply_to_message.text
        await query.edit_message_text(
            get_text("generating_image", language)
        )
        
        # Wywołaj funkcję generowania obrazu z oryginalną wiadomością jako promptem
        from handlers.image_handler import generate_image_dall_e
        image_url = await generate_image_dall_e(original_message)
        
        # Odejmij kredyty
        from database.credits_client import deduct_user_credits
        deduct_user_credits(user_id, 10, "Generowanie obrazu przez menu kontekstowe")
        
        if image_url:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=image_url,
                caption=f"*{get_text('generated_image', language)}*\n{original_message}",
                parse_mode=ParseMode.MARKDOWN
            )
            await query.message.delete()  # Usuń wiadomość menu
        else:
            await query.edit_message_text(
                get_text("image_generation_error", language)
            )
        return True
        
    elif query.data == "context_code_mode":
        # Przełącz na tryb programisty
        if 'user_data' not in context.chat_data:
            context.chat_data['user_data'] = {}
        
        if user_id not in context.chat_data['user_data']:
            context.chat_data['user_data'][user_id] = {}
        
        context.chat_data['user_data'][user_id]['current_mode'] = "code_developer"
        
        await query.edit_message_text(
            f"{get_text('switched_to_mode', language)} *{CHAT_MODES['code_developer']['name']}*\n\n"
            f"{get_text('ask_coding_question', language)}",
            parse_mode=ParseMode.MARKDOWN
        )
        return True
        
    elif query.data == "context_detailed":
        # Żądanie szczegółowego wyjaśnienia oryginalnej wiadomości
        original_message = query.message.reply_to_message.text
        
        await query.edit_message_text(
            get_text("detailed_explanation_requested", language)
        )
        
        # Przygotuj prompt z żądaniem szczegółowego wyjaśnienia
        prompt = f"Proszę o szczegółowe wyjaśnienie następującego zagadnienia: {original_message}"
        
        # Utwórz nową wiadomość z żądaniem szczegółowego wyjaśnienia
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=prompt
        )
        return True
        
    elif query.data == "context_hide":
        # Ukryj menu kontekstowe
        await query.message.delete()
        return True
    
    return False

# Zastąp funkcję handle_menu_callback w pliku handlers/menu_handler.py poniższym kodem

async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługuje wszystkie callbacki związane z menu
    
    Returns:
        bool: True jeśli callback został obsłużony, False w przeciwnym razie
    """
    query = update.callback_query
    
    # Debugowanie
    print(f"Menu handler otrzymał callback: {query.data}")
    
    # Sprawdź, czy to callback związany z menu
    if not query.data.startswith("menu_"):
        return False
    
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Obsługa przycisków menu
    if query.data == "menu_section_chat_modes":
        # Utworzenie menu trybów czatu
        keyboard = []
        for mode_id, mode_info in CHAT_MODES.items():
            keyboard.append([
                InlineKeyboardButton(
                    mode_info['name'], 
                    callback_data=f"mode_{mode_id}"
                )
            ])
        
        # Dodaj przycisk powrotu
        keyboard.append([
            InlineKeyboardButton("Powrót", callback_data="menu_back_main")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Wybierz tryb czatu:",
            reply_markup=reply_markup
        )
        return True
        
    elif query.data == "menu_section_credits":
        # Menu kredytów
        keyboard = [
            [InlineKeyboardButton("Sprawdź saldo", callback_data="credits_check")],
            [InlineKeyboardButton("Kup kredyty", callback_data="credits_buy")],
            [InlineKeyboardButton("Powrót", callback_data="menu_back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Kredyty: {get_user_credits(user_id)}\nWybierz opcję:",
            reply_markup=reply_markup
        )
        return True
        
    elif query.data == "menu_image_generate":
        # Menu generowania obrazów
        keyboard = [
            [InlineKeyboardButton("Powrót", callback_data="menu_back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Aby wygenerować obraz, użyj komendy:\n/image [opis obrazu]",
            reply_markup=reply_markup
        )
        return True
        
    elif query.data == "menu_section_history":
        # Menu historii
        keyboard = [
            [InlineKeyboardButton("Nowa konwersacja", callback_data="history_new")],
            [InlineKeyboardButton("Eksportuj", callback_data="history_export")],
            [InlineKeyboardButton("Powrót", callback_data="menu_back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Historia rozmów - wybierz opcję:",
            reply_markup=reply_markup
        )
        return True
        
    elif query.data == "menu_section_settings":
        # Menu ustawień
        keyboard = [
            [InlineKeyboardButton("Zmień model AI", callback_data="settings_model")],
            [InlineKeyboardButton("Zmień język", callback_data="settings_language")],
            [InlineKeyboardButton("Powrót", callback_data="menu_back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Ustawienia - wybierz opcję:",
            reply_markup=reply_markup
        )
        return True
        
    elif query.data == "menu_help":
        # Menu pomocy
        keyboard = [
            [InlineKeyboardButton("Powrót", callback_data="menu_back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Pomoc:\n\n/start - Start\n/credits - Sprawdź kredyty\n/buy - Kup kredyty\n/image - Generuj obraz",
            reply_markup=reply_markup
        )
        return True
        
    elif query.data == "menu_back_main":
        # Powrót do głównego menu
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
        
        await query.edit_message_text(
            f"Menu główne\n\nStatus:\nKredyty: {get_user_credits(user_id)}\nWybierz opcję z menu poniżej:",
            reply_markup=reply_markup
        )
        return True
    
    print(f"Nieobsłużony callback menu: {query.data}")
    return False

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