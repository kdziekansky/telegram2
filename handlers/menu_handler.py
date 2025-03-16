from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

def create_chat_modes_menu_markup(language):
    """Klawiatura dla sekcji trybów czatu"""
    keyboard = []
    
    # Dodaj przyciski dla każdego trybu czatu
    row = []
    for i, (mode_id, mode_info) in enumerate(CHAT_MODES.items()):
        if i % 2 == 0 and i > 0:
            keyboard.append(row)
            row = []
        row.append(
            InlineKeyboardButton(
                f"{mode_info['name']} ({mode_info['credit_cost']})", 
                callback_data=f"menu_mode_{mode_id}"
            )
        )
    
    if row:
        keyboard.append(row)
    
    # Dodaj przycisk powrotu
    keyboard.append([InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_main")])
    
    return InlineKeyboardMarkup(keyboard)

def create_credits_menu_markup(language):
    """Klawiatura dla sekcji kredytów"""
    keyboard = [
        [
            InlineKeyboardButton("💰 " + get_text("check_balance", language, default="Stan konta"), callback_data="menu_credits_check")
        ],
        [
            InlineKeyboardButton("🛒 " + get_text("buy_credits_btn", language, default="Kup kredyty"), callback_data="menu_credits_buy")
        ],
        [
            InlineKeyboardButton("📈 " + get_text("credit_stats", language, default="Statystyki"), callback_data="menu_credits_stats")
        ],
        [
            InlineKeyboardButton("🎁 " + get_text("promo_code", language, default="Kod promocyjny"), callback_data="menu_credits_promo")
        ],
        [
            InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_main")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def create_history_menu_markup(language):
    """Klawiatura dla sekcji historii"""
    keyboard = [
        [
            InlineKeyboardButton("📝 " + get_text("view_history", language, default="Zobacz historię"), callback_data="menu_history_view")
        ],
        [
            InlineKeyboardButton("🔄 " + get_text("new_chat", language, default="Nowa rozmowa"), callback_data="menu_history_new")
        ],
        [
            InlineKeyboardButton("📤 " + get_text("export_conversation", language, default="Eksportuj rozmowę"), callback_data="menu_history_export")
        ],
        [
            InlineKeyboardButton("🗑️ " + get_text("delete_history", language, default="Usuń historię"), callback_data="menu_history_delete")
        ],
        [
            InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_main")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def create_settings_menu_markup(language):
    """Klawiatura dla sekcji ustawień"""
    keyboard = [
        [
            InlineKeyboardButton("🤖 " + get_text("settings_model", language), callback_data="menu_settings_model")
        ],
        [
            InlineKeyboardButton("🌐 " + get_text("settings_language", language), callback_data="menu_settings_language")
        ],
        [
            InlineKeyboardButton("👤 " + get_text("settings_name", language), callback_data="menu_settings_name")
        ],
        [
            InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_main")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def create_models_menu_markup(language):
    """Klawiatura dla wyboru modelu AI"""
    keyboard = []
    
    # Dodaj przyciski dla każdego modelu
    for model_id, model_name in AVAILABLE_MODELS.items():
        # Dodaj informację o koszcie kredytów
        credit_cost = CREDIT_COSTS["message"].get(model_id, CREDIT_COSTS["message"]["default"])
        
        keyboard.append([
            InlineKeyboardButton(
                f"{model_name} ({credit_cost} kredyt(ów))", 
                callback_data=f"menu_model_{model_id}"
            )
        ])
    
    # Dodaj przycisk powrotu
    keyboard.append([InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_settings")])
    
    return InlineKeyboardMarkup(keyboard)

def create_language_menu_markup():
    """Klawiatura dla wyboru języka"""
    keyboard = []
    
    # Dodaj przyciski dla każdego języka
    for lang_code, lang_name in AVAILABLE_LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"menu_lang_{lang_code}")])
    
    # Dodaj przycisk powrotu
    keyboard.append([InlineKeyboardButton("🔙 Back / Powrót / Назад", callback_data="menu_back_settings")])
    
    return InlineKeyboardMarkup(keyboard)

def create_credits_packages_markup(language, packages):
    """Klawiatura dla pakietów kredytów"""
    keyboard = []
    
    # Dodaj przyciski dla każdego pakietu
    for pkg in packages:
        keyboard.append([
            InlineKeyboardButton(
                f"{pkg['name']} - {pkg['credits']} kredytów ({pkg['price']} PLN)", 
                callback_data=f"buy_package_{pkg['id']}"
            )
        ])
    
    # Dodaj przycisk powrotu
    keyboard.append([InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_credits")])
    
    return InlineKeyboardMarkup(keyboard)

# Funkcje obsługujące menu

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla główne menu bota z przyciskami inline
    """
    user_id = update.effective_user.id
    
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
    
    elif menu_state == 'chat_modes':
        menu_title = get_text("menu_chat_mode", language)
        menu_text = f"""💬 *{menu_title}*

{get_text("current_mode", language, default="Aktualny tryb")}: *{mode_name}*
{get_text("select_chat_mode", language, default="Wybierz tryb czatu:")}
"""
        if not markup:
            markup = create_chat_modes_menu_markup(language)
    
    elif menu_state == 'credits':
        menu_title = get_text("menu_credits", language, default="Kredyty")
        menu_text = f"""📊 *{menu_title}*

{get_text("current_credits", language, default="Aktualny stan kredytów")}: *{credits}*
{get_text("credit_options", language, default="Wybierz opcję:")}
"""
        if not markup:
            markup = create_credits_menu_markup(language)
    
    elif menu_state == 'history':
        menu_title = get_text("menu_dialog_history", language)
        menu_text = f"""📂 *{menu_title}*

{get_text("history_options", language, default="Wybierz opcję dla historii rozmów:")}
"""
        if not markup:
            markup = create_history_menu_markup(language)
    
    elif menu_state == 'settings':
        menu_title = get_text("menu_settings", language)
        menu_text = f"""⚙️ *{menu_title}*

{get_text("current_model", language, default="Model")}: *{model_name}*
{get_text("current_language", language, default="Język")}: *{AVAILABLE_LANGUAGES.get(language, language)}*

{get_text("settings_options", language, default="Wybierz opcję:")}
"""
        if not markup:
            markup = create_settings_menu_markup(language)
    
    elif menu_state == 'models':
        menu_title = get_text("settings_model", language)
        menu_text = f"""🤖 *{menu_title}*

{get_text("current_model", language, default="Aktualny model")}: *{model_name}*
{get_text("select_model", language, default="Wybierz model AI:")}
"""
        if not markup:
            markup = create_models_menu_markup(language)
    
    elif menu_state == 'languages':
        menu_title = get_text("settings_language", language)
        menu_text = f"""🌐 *{menu_title}*

{get_text("current_language", language, default="Aktualny język")}: *{AVAILABLE_LANGUAGES.get(language, language)}*
{get_text("select_language", language, default="Wybierz język:")}
"""
        if not markup:
            markup = create_language_menu_markup()
    
    elif menu_state == 'buy_credits':
        from database.credits_client import get_credit_packages
        packages = get_credit_packages()
        
        menu_title = get_text("buy_credits_btn", language, default="Kup kredyty")
        menu_text = f"""🛒 *{menu_title}*

{get_text("current_credits", language, default="Aktualny stan kredytów")}: *{credits}*
{get_text("select_package", language, default="Wybierz pakiet kredytów:")}
"""
        if not markup:
            markup = create_credits_packages_markup(language, packages)
    
    else:
        # Domyślnie wróć do głównego menu
        menu_state = 'main'
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
    
    elif query.data == "menu_back_settings":
        await query.answer()
        await update_menu(update, context, 'settings')
        return True
    
    elif query.data == "menu_back_credits":
        await query.answer()
        await update_menu(update, context, 'credits')
        return True
    
    # Obsługa sekcji menu
    elif query.data == "menu_section_chat_modes":
        await query.answer()
        await update_menu(update, context, 'chat_modes')
        return True
    
    elif query.data == "menu_section_credits":
        await query.answer()
        await update_menu(update, context, 'credits')
        return True
    
    elif query.data == "menu_section_history":
        await query.answer()
        await update_menu(update, context, 'history')
        return True
    
    elif query.data == "menu_section_settings":
        await query.answer()
        await update_menu(update, context, 'settings')
        return True
    
    # Obsługa akcji w sekcji ustawień
    elif query.data == "menu_settings_model":
        await query.answer()
        await update_menu(update, context, 'models')
        return True
    
    elif query.data == "menu_settings_language":
        await query.answer()
        await update_menu(update, context, 'languages')
        return True
    
    elif query.data == "menu_settings_name":
        await query.answer()
        await query.edit_message_text(
            get_text("settings_change_name", language),
            parse_mode=ParseMode.MARKDOWN
        )
        return True
    
    # Obsługa wyboru modelu
    elif query.data.startswith("menu_model_"):
        model_id = query.data[11:]  # Usuń prefix "menu_model_"
        await handle_model_selection(update, context, model_id)
        return True
    
    # Obsługa wyboru języka
    elif query.data.startswith("menu_lang_"):
        lang_code = query.data[10:]  # Usuń prefix "menu_lang_"
        await handle_language_selection(update, context, lang_code)
        return True
    
    # Obsługa wyboru trybu czatu
    elif query.data.startswith("menu_mode_"):
        mode_id = query.data[10:]  # Usuń prefix "menu_mode_"
        await handle_mode_selection(update, context, mode_id)
        return True
    
    # Obsługa akcji w sekcji kredytów
    elif query.data == "menu_credits_check":
        await handle_credits_check(update, context)
        return True
    
    elif query.data == "menu_credits_buy":
        await query.answer()
        await update_menu(update, context, 'buy_credits')
        return True
    
    elif query.data == "menu_credits_stats":
        await handle_credits_stats(update, context)
        return True
    
    elif query.data == "menu_credits_promo":
        await query.answer()
        await query.edit_message_text(
            get_text("activation_code_usage", language),
            parse_mode=ParseMode.MARKDOWN
        )
        return True
    
    # Obsługa zakupu pakietu kredytów
    elif query.data.startswith("buy_package_"):
        package_id = int(query.data.split("_")[2])
        await handle_package_purchase(update, context, package_id)
        return True
    
    # Obsługa akcji w sekcji historii
    elif query.data == "menu_history_view":
        await handle_history_view(update, context)
        return True
    
    elif query.data == "menu_history_new":
        await handle_history_new(update, context)
        return True
    
    elif query.data == "menu_history_export":
        await handle_history_export(update, context)
        return True
    
    elif query.data == "menu_history_delete":
        await handle_history_delete(update, context)
        return True
    
    # Obsługa akcji generowania obrazu
    elif query.data == "menu_image_generate":
        await query.answer()
        await query.edit_message_text(
            get_text("image_usage", language),
            parse_mode=ParseMode.MARKDOWN
        )
        return True
    
    # Obsługa akcji pomocy
    elif query.data == "menu_help":
        await query.answer()
        help_text = get_text("help_text", language)
        
        # Dodaj przycisk powrotu
        keyboard = [[InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_main")]]
        
        await query.edit_message_text(
            help_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return True
    
    return False

# Funkcje obsługujące akcje menu

async def handle_model_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, model_id):
    """Obsługa wyboru modelu AI"""
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Sprawdź, czy model istnieje
    if model_id not in AVAILABLE_MODELS:
        await query.answer(get_text("model_not_available", language))
        return
    
    # Zapisz wybrany model w kontekście użytkownika
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    
    if user_id not in context.chat_data['user_data']:
        context.chat_data['user_data'][user_id] = {}
    
    context.chat_data['user_data'][user_id]['current_model'] = model_id
    
    # Pobierz koszt kredytów dla wybranego modelu
    credit_cost = CREDIT_COSTS["message"].get(model_id, CREDIT_COSTS["message"]["default"])
    
    model_name = AVAILABLE_MODELS[model_id]
    
    # Powiadom użytkownika
    await query.answer(get_text("model_selected_short", language, default="Model został zmieniony", model=model_name))
    
    # Wyświetl potwierdzenie
    message = get_text("model_selected", language, model=model_name, credits=credit_cost)
    
    # Dodaj przycisk powrotu
    keyboard = [[InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_settings")]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_lang):
    """Obsługa wyboru języka"""
    query = update.callback_query
    user_id = query.from_user.id
    
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
    
    # Dodaj sugestię restartu bota
    full_message = f"{confirmation_message}\n\n{restart_suggestion}"
    
    # Przyciski akcji
    keyboard = [
        [InlineKeyboardButton(get_text("restart_button", selected_lang), callback_data="restart_bot")],
        [InlineKeyboardButton("🔙 " + get_text("back", language_name, default="Powrót"), callback_data="menu_back_settings")]
    ]
    
    await query.answer(get_text("language_selected_short", selected_lang, default="Język został zmieniony"))
    
    await query.edit_message_text(
        full_message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_mode_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, mode_id):
    """Obsługa wyboru trybu czatu"""
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Sprawdź, czy tryb istnieje
    if mode_id not in CHAT_MODES:
        await query.answer(get_text("model_not_available", language))
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
    
    # Powiadom użytkownika
    await query.answer(get_text("mode_selected", language, default="Tryb został zmieniony", mode=mode_name))
    
    # Wyświetl potwierdzenie
    message = f"✅ {get_text('mode_changed', language, default='Zmieniono tryb na')}: *{mode_name}*\n"
    message += f"{get_text('cost', language)}: *{credit_cost}* {get_text('credits', language)} {get_text('per_message', language, default='za wiadomość')}\n\n"
    message += f"_{short_description}_\n\n"
    message += f"{get_text('mode_usage', language, default='Możesz teraz zadać pytanie w wybranym trybie.')}"
    
    # Utwórz nową konwersację dla wybranego trybu
    from database.sqlite_client import create_new_conversation
    create_new_conversation(user_id)
    
    # Dodaj przycisk powrotu
    keyboard = [[InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_main")]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_credits_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa sprawdzania stanu kredytów"""
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Pobierz stan kredytów
    credits = get_user_credits(user_id)
    
    # Przygotuj informacje o kredytach
    message = get_text("credits_info", language, bot_name="AI Bot", credits=credits)
    
    # Dodaj przycisk zakupu kredytów
    keyboard = [
        [InlineKeyboardButton("🛒 " + get_text("buy_credits_btn", language, default="Kup kredyty"), callback_data="menu_credits_buy")],
        [InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_credits")]
    ]
    
    await query.answer()
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_credits_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa statystyk kredytów"""
    query = update.callback_query
    
    # Przekazanie do właściwej funkcji
    from handlers.credit_handler import credit_stats_command
    
    # Symulujemy update dla funkcji credit_stats_command
    class FakeUpdate:
        class FakeMessage:
            def __init__(self, chat_id, from_user):
                self.chat_id = chat_id
                self.from_user = from_user
                
            async def reply_text(self, text, **kwargs):
                return await query.message.reply_text(text, **kwargs)
        
        def __init__(self, message, effective_user):
            self.message = message
            self.effective_user = effective_user
    
    fake_message = FakeUpdate.FakeMessage(query.message.chat_id, query.from_user)
    fake_update = FakeUpdate(fake_message, query.from_user)
    
    await query.answer()
    await query.edit_message_text("Generuję statystyki kredytów...")
    
    # Wywołujemy właściwą funkcję
    await credit_stats_command(fake_update, context)

async def handle_package_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, package_id):
    """Obsługa zakupu pakietu kredytów"""
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Symulacja zakupu kredytów
    from database.credits_client import purchase_credits
    success, package = purchase_credits(user_id, package_id)
    
    if success and package:
        current_credits = get_user_credits(user_id)
        message = get_text("credit_purchase_success", language,
            package_name=package['name'],
            credits=package['credits'],
            price=package['price'],
            total_credits=current_credits
        )
        
        # Dodaj przycisk powrotu
        keyboard = [[InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_credits")]]
        
        await query.answer(get_text("purchase_complete", language, default="Zakup zakończony pomyślnie!"))
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        error_message = get_text("purchase_error", language, default="Wystąpił błąd podczas zakupu kredytów. Spróbuj ponownie lub wybierz inny pakiet.")
        
        # Dodaj przycisk powrotu
        keyboard = [[InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_credits")]]
        
        await query.answer(get_text("purchase_error_short", language, default="Błąd zakupu"))
        
        await query.edit_message_text(
            error_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_history_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa podglądu historii rozmów"""
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Pobierz aktywną konwersację
    from database.sqlite_client import get_active_conversation, get_conversation_history
    conversation = get_active_conversation(user_id)
    
    if not conversation:
        await query.answer(get_text("history_no_conversation", language))
        await query.edit_message_text(
            get_text("history_no_conversation", language),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_history")
            ]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Pobierz historię konwersacji
    history = get_conversation_history(conversation['id'])
    
    if not history:
        await query.answer(get_text("history_empty", language))
        await query.edit_message_text(
            get_text("history_empty", language),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_history")
            ]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Przygotuj wiadomość z historią
    history_text = f"{get_text('history_title', language)}\n\n"
    
    # Ogranicz do ostatnich 5 wiadomości, aby nie przekroczyć limitu
    for msg in history[-5:]:
        sender = get_text("history_user", language) if msg['is_from_user'] else get_text("history_bot", language)
        content = msg['content']
        
        # Skróć wiadomości, jeśli są za długie
        if len(content) > 100:
            content = content[:97] + "..."
        
        history_text += f"*{sender}*: {content}\n\n"
    
    # Dodaj przyciski
    keyboard = [
        [InlineKeyboardButton("🔄 " + get_text("refresh", language, default="Odśwież"), callback_data="menu_history_view")],
        [InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_history")]
    ]
    
    await query.answer()
    
    await query.edit_message_text(
        history_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_history_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa tworzenia nowej rozmowy"""
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Utwórz nową konwersację
    from database.sqlite_client import create_new_conversation
    conversation = create_new_conversation(user_id)
    
    if conversation:
        await query.answer(get_text("new_chat_created", language, default="Utworzono nową rozmowę"))
        
        message = get_text("new_chat_success", language, default="✅ Utworzono nową rozmowę. Możesz teraz zadać pytanie.")
        
        keyboard = [[InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_history")]]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await query.answer(get_text("error", language, default="Wystąpił błąd"))
        
        message = get_text("new_chat_error", language, default="Wystąpił błąd podczas tworzenia nowej rozmowy.")
        
        keyboard = [[InlineKeyboardButton("🔙 " + get_text("back", language, default="Powrót"), callback_data="menu_back_history")]]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_history_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa eksportu historii rozmów"""
    query = update.callback_query
    
    # Przekazanie do właściwej funkcji
    from handlers.export_handler import export_conversation
    
    # Symulujemy update dla funkcji export_conversation
    class FakeUpdate:
        class FakeMessage:
            class FakeChat:
                def __init__(self, chat_id):
                    self.id = chat_id
                
                async def send_action(self, action):
                    pass
            
            def __init__(self, chat_id, from_user):
                self.chat_id = chat_id
                self.from_user = from_user
                self.chat = self.FakeChat(chat_id)
                
            async def reply_text(self, text, **kwargs):
                return await query.message.reply_text(text, **kwargs)
        
        def __init__(self, message, effective_user, effective_chat):
            self.message = message
            self.effective_user = effective_user
            self.effective_chat = effective_chat
    
    fake_message = FakeUpdate.FakeMessage(query.message.chat_id, query.from_user)
    fake_update = FakeUpdate(fake_message, query.from_user, query.message.chat)
    
    await query.answer()
    await query.edit_message_text("Przygotowuję eksport rozmowy...")
    
    # Wywołujemy właściwą funkcję
    await export_conversation(fake_update, context)

async def handle_history_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa usuwania historii rozmów"""
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Potwierdź usunięcie historii
    keyboard = [
        [
            InlineKeyboardButton("✅ " + get_text("yes", language, default="Tak"), callback_data="history_confirm_delete"),
            InlineKeyboardButton("❌ " + get_text("no", language, default="Nie"), callback_data="menu_back_history")
        ]
    ]
    
    await query.answer()
    
    await query.edit_message_text(
        get_text("history_delete_confirm", language, default="Czy na pewno chcesz usunąć historię rozmów?"),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

# Funkcje pomocnicze menu kontekstowego

def create_contextual_menu_markup(context, user_id, message_text):
    """
    Tworzy menu kontekstowe na podstawie treści wiadomości
    
    Args:
        context: Kontekst bota
        user_id: ID użytkownika
        message_text: Treść wiadomości
        
    Returns:
        InlineKeyboardMarkup: Klawiatura z przyciskami kontekstowymi lub None
    """
    language = get_user_language(context, user_id)
    
    # Wykrywanie kontekstu na podstawie słów kluczowych
    keywords = {
        'image': ['obraz', 'zdjęcie', 'obrazek', 'picture', 'image', 'foto', 'narysuj'],
        'code': ['kod', 'program', 'funkcja', 'code', 'algorithm', 'function', 'class'],
        'explain': ['wyjaśnij', 'wytłumacz', 'explain', 'what is', 'how to', 'jak', 'co to'],
        'translate': ['przetłumacz', 'translate', 'tłumaczenie', 'tłumacz'],
        'write': ['napisz', 'utwórz', 'write', 'create', 'compose', 'draft'],
        'search': ['znajdź', 'wyszukaj', 'search', 'find', 'look for']
    }
    
    detected_contexts = []
    for context_type, words in keywords.items():
        if any(word.lower() in message_text.lower() for word in words):
            detected_contexts.append(context_type)
    
    # Jeśli nie wykryto kontekstu, nie pokazuj menu
    if not detected_contexts:
        return None
    
    # Przygotuj przyciski kontekstowe
    keyboard = []
    
    if 'image' in detected_contexts:
        keyboard.append([
            InlineKeyboardButton("🖼️ " + get_text("generate_image", language, default="Wygeneruj obraz"), 
                                callback_data="context_image_generate")
        ])
    
    if 'code' in detected_contexts:
        keyboard.append([
            InlineKeyboardButton("👨‍💻 " + get_text("switch_to_code_mode", language, default="Przełącz na tryb programisty"), 
                                callback_data="context_mode_code_developer")
        ])
    
    if 'explain' in detected_contexts:
        keyboard.append([
            InlineKeyboardButton("🧠 " + get_text("detailed_explanation", language, default="Szczegółowe wyjaśnienie"), 
                                callback_data="context_detailed_explanation")
        ])
    
    if 'translate' in detected_contexts:
        keyboard.append([
            InlineKeyboardButton("🌐 " + get_text("translate", language, default="Przetłumacz"), 
                                callback_data="context_translate")
        ])
    
    # Jeśli mamy więcej niż jeden przycisk, dodaj przycisk "Nie pokazuj"
    if len(keyboard) > 0:
        keyboard.append([
            InlineKeyboardButton("❌ " + get_text("dont_show", language, default="Nie pokazuj"), 
                                callback_data="context_dismiss")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    return None

async def handle_contextual_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługuje callbacki związane z menu kontekstowym
    
    Returns:
        bool: True jeśli callback został obsłużony, False w przeciwnym razie
    """
    query = update.callback_query
    
    # Sprawdź, czy to callback związany z menu kontekstowym
    if not query.data.startswith("context_"):
        return False
    
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Obsługa ukrycia menu kontekstowego
    if query.data == "context_dismiss":
        await query.answer(get_text("menu_hidden", language, default="Menu zostało ukryte"))
        await query.delete_message()
        return True
    
    # Obsługa akcji generowania obrazu
    elif query.data == "context_image_generate":
        await query.answer()
        await query.edit_message_text(
            get_text("image_usage", language),
            parse_mode=ParseMode.MARKDOWN
        )
        return True
    
    # Obsługa przełączania trybu na programistę
    elif query.data == "context_mode_code_developer":
        if 'user_data' not in context.chat_data:
            context.chat_data['user_data'] = {}
        
        if user_id not in context.chat_data['user_data']:
            context.chat_data['user_data'][user_id] = {}
        
        context.chat_data['user_data'][user_id]['current_mode'] = "code_developer"
        
        # Jeśli tryb ma określony model, ustaw go również
        if "model" in CHAT_MODES["code_developer"]:
            context.chat_data['user_data'][user_id]['current_model'] = CHAT_MODES["code_developer"]["model"]
        
        # Utwórz nową konwersację
        from database.sqlite_client import create_new_conversation
        create_new_conversation(user_id)
        
        await query.answer(get_text("mode_changed", language, default="Tryb został zmieniony"))
        await query.edit_message_text(
            f"✅ {get_text('switched_to_mode', language, default='Przełączono na tryb')}: *{CHAT_MODES['code_developer']['name']}*\n\n"
            f"{get_text('ask_coding_question', language, default='Możesz teraz zadać pytanie związane z programowaniem.')}",
            parse_mode=ParseMode.MARKDOWN
        )
        return True
    
    # Obsługa żądania szczegółowego wyjaśnienia
    elif query.data == "context_detailed_explanation":
        # Pobierz oryginalną wiadomość
        original_message = query.message.reply_to_message.text if query.message.reply_to_message else ""
        
        if original_message:
            # Utwórz nową konwersację
            from database.sqlite_client import get_active_conversation, save_message
            
            conversation = get_active_conversation(user_id)
            save_message(conversation['id'], user_id, f"Potrzebuję szczegółowego wyjaśnienia na temat: {original_message}", is_from_user=True)
            
            await query.answer()
            await query.edit_message_text(
                f"{get_text('detailed_explanation_requested', language, default='Poproszono o szczegółowe wyjaśnienie')}:\n\n"
                f"_{original_message}_",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.answer(get_text("error", language, default="Wystąpił błąd"))
            await query.delete_message()
        
        return True
    
    # Obsługa żądania tłumaczenia
    elif query.data == "context_translate":
        # Pobierz oryginalną wiadomość
        original_message = query.message.reply_to_message.text if query.message.reply_to_message else ""
        
        if original_message:
            # Utwórz nową konwersację
            from database.sqlite_client import get_active_conversation, save_message
            
            conversation = get_active_conversation(user_id)
            save_message(conversation['id'], user_id, f"Przetłumacz na język polski i angielski: {original_message}", is_from_user=True)
            
            await query.answer()
            await query.edit_message_text(
                f"{get_text('translation_requested', language, default='Poproszono o tłumaczenie')}:\n\n"
                f"_{original_message}_",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.answer(get_text("error", language, default="Wystąpił błąd"))
            await query.delete_message()
        
        return True
    
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