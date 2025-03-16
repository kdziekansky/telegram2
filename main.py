import logging
import os
import re
import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ParseMode, ChatAction
from config import (
    TELEGRAM_TOKEN, DEFAULT_MODEL, AVAILABLE_MODELS, 
    MAX_CONTEXT_MESSAGES, CHAT_MODES, BOT_NAME, CREDIT_COSTS,
    AVAILABLE_LANGUAGES
)

# Import funkcji z modułu tłumaczeń
from utils.translations import get_text

# Import funkcji z modułu sqlite_client
from database.sqlite_client import (
    get_or_create_user, create_new_conversation, 
    get_active_conversation, save_message, 
    get_conversation_history, get_message_status
)

# Import funkcji obsługi kredytów
from database.credits_client import (
    get_user_credits, add_user_credits, deduct_user_credits, 
    check_user_credits
)

# Import handlerów kredytów
from handlers.credit_handler import (
    credits_command, buy_command, handle_credit_callback,
    credit_stats_command, credit_analytics_command
)

# Import handlerów kodu aktywacyjnego
from handlers.code_handler import (
    code_command, admin_generate_code
)

# Import handlerów menu
from handlers.menu_handler import (
    show_main_menu, handle_menu_callback,
    set_user_name, get_user_language
)

# Import handlera start
from handlers.start_handler import (
    start_command, handle_language_selection
)

# Import handlera obrazów
from handlers.image_handler import generate_image

from utils.openai_client import (
    chat_completion_stream, prepare_messages_from_history,
    generate_image_dall_e, analyze_document, analyze_image
)

# Import handlera eksportu
from handlers.export_handler import export_conversation
from handlers.theme_handler import theme_command, notheme_command, handle_theme_callback
from utils.credit_analytics import generate_credit_usage_chart, generate_usage_breakdown_chart


# Konfiguracja loggera
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Lista ID administratorów bota - tutaj należy dodać swoje ID
ADMIN_USER_IDS = [1743680448, 787188598]  # Zastąp swoim ID użytkownika Telegram

# Handlers dla podstawowych komend

from telegram import ReplyKeyboardRemove

async def remove_keyboard(update, context):
    """Usuwa klawiaturę systemową bota i zastępuje ją pustą"""
    await update.message.reply_text(
        "Klawiatura została usunięta. Używam teraz tylko menu inline.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Pokaż menu główne
    from handlers.menu_handler import show_main_menu
    await show_main_menu(update, context)

async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługa komendy /restart
    Resetuje kontekst bota, pokazuje informacje o bocie i aktualnych ustawieniach użytkownika
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Usuń klawiaturę systemową
    await update.message.reply_text("Usuwam klawiaturę...", reply_markup=ReplyKeyboardRemove())
    
    # Resetowanie konwersacji - tworzymy nową konwersację i czyścimy kontekst
    conversation = create_new_conversation(user_id)
    
    # Zachowujemy wybrane ustawienia użytkownika (język, model)
    user_data = {}
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data']:
        # Pobieramy tylko podstawowe ustawienia, reszta jest resetowana
        old_user_data = context.chat_data['user_data'][user_id]
        if 'language' in old_user_data:
            user_data['language'] = old_user_data['language']
        if 'current_model' in old_user_data:
            user_data['current_model'] = old_user_data['current_model']
        if 'current_mode' in old_user_data:
            user_data['current_mode'] = old_user_data['current_mode']
    
    # Resetujemy dane użytkownika w kontekście i ustawiamy tylko zachowane ustawienia
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    context.chat_data['user_data'][user_id] = user_data
    
    # Sprawdzanie statusu kredytów
    credits = get_user_credits(user_id)
    
    # Pobranie aktualnego trybu czatu
    current_mode = "brak" 
    current_mode_cost = 1
    if 'current_mode' in user_data and user_data['current_mode'] in CHAT_MODES:
        current_mode = CHAT_MODES[user_data['current_mode']]["name"]
        current_mode_cost = CHAT_MODES[user_data['current_mode']]["credit_cost"]
    
    # Pobranie aktualnego modelu
    current_model = DEFAULT_MODEL
    if 'current_model' in user_data and user_data['current_model'] in AVAILABLE_MODELS:
        current_model = AVAILABLE_MODELS[user_data['current_model']]
    
    # Pobierz nazwę aktualnego języka
    language_name = AVAILABLE_LANGUAGES.get(language, language)
    
    # Przygotowanie wiadomości
    restart_text = f"""
🔄 *{BOT_NAME} został zrestartowany*

{get_text("help_text", language)}
"""
    
    # Dodaj informacje o aktualnych ustawieniach
    restart_text += f"\n*{get_text('settings_title', language)}*"
    restart_text += f"\n{get_text('menu_chat_mode', language)}: {current_mode} ({get_text('credits', language)}: {current_mode_cost})"
    restart_text += f"\n{get_text('settings_model', language)}: {current_model}"
    restart_text += f"\n{get_text('settings_language', language)}: {language_name}"
    restart_text += f"\n{get_text('menu_balance', language)}: *{credits}* {get_text('credits', language)}"
    
    # Dodaj informację o restarcie bota
    restart_text += f"\n\n{get_text('language_restart_complete', language, language_display=language_name)}"
    
    await update.message.reply_text(restart_text, parse_mode=ParseMode.MARKDOWN)
    
    # Pokaż menu główne
    await show_main_menu(update, context)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługa komendy /menu
    Wyświetla menu główne bota
    """
    await show_main_menu(update, context)

async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sprawdza status konta użytkownika
    Użycie: /status
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Pobierz status kredytów
    credits = get_user_credits(user_id)
    
    # Pobranie aktualnego trybu czatu
    current_mode = "brak" 
    current_mode_cost = 1
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data']:
        user_data = context.chat_data['user_data'][user_id]
        if 'current_mode' in user_data and user_data['current_mode'] in CHAT_MODES:
            current_mode = CHAT_MODES[user_data['current_mode']]["name"]
            current_mode_cost = CHAT_MODES[user_data['current_mode']]["credit_cost"]
    
    # Stwórz wiadomość o statusie
    message = f"""
*Status twojego konta w {BOT_NAME}:*

Dostępne kredyty: *{credits}*
Aktualny tryb: *{current_mode}* (koszt: {current_mode_cost} kredyt(ów) za wiadomość)

Koszty operacji:
• Standardowa wiadomość (GPT-3.5): 1 kredyt
• Wiadomość Premium (GPT-4o): 3 kredyty
• Wiadomość Ekspercka (GPT-4): 5 kredytów
• Obraz DALL-E: 10-15 kredytów
• Analiza dokumentu: 5 kredytów
• Analiza zdjęcia: 8 kredytów

Aby dokupić więcej kredytów, użyj komendy /buy.
"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rozpoczyna nową konwersację"""
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Utwórz nową konwersację
    conversation = create_new_conversation(user_id)
    
    if conversation:
        await update.message.reply_text(
            "Rozpoczęto nową konwersację. Możesz teraz zadać pytanie.",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            "Wystąpił błąd podczas tworzenia nowej konwersacji.",
            parse_mode=ParseMode.MARKDOWN
        )

async def show_models(update: Update, context: ContextTypes.DEFAULT_TYPE, edit_message=False, callback_query=None):
    """Pokazuje dostępne modele AI"""
    user_id = update.effective_user.id if hasattr(update, 'effective_user') else callback_query.from_user.id
    language = get_user_language(context, user_id)
    
    # Utwórz przyciski dla dostępnych modeli
    keyboard = []
    for model_id, model_name in AVAILABLE_MODELS.items():
        # Dodaj informację o koszcie kredytów
        credit_cost = CREDIT_COSTS["message"].get(model_id, CREDIT_COSTS["message"]["default"])
        keyboard.append([
            InlineKeyboardButton(
                text=f"{model_name} ({credit_cost} kredyt(ów))", 
                callback_data=f"model_{model_id}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if edit_message and callback_query:
        await callback_query.edit_message_text(
            get_text("settings_choose_model", language),
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            get_text("settings_choose_model", language),
            reply_markup=reply_markup
        )

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
        keyboard.append([
            InlineKeyboardButton(
                text=f"{mode_info['name']} ({mode_info['credit_cost']} kredyt(ów))", 
                callback_data=f"mode_{mode_id}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text("settings_choose_model", language),
        reply_markup=reply_markup
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa wiadomości tekstowych od użytkownika ze strumieniowaniem odpowiedzi"""
    user_id = update.effective_user.id
    user_message = update.message.text
    language = get_user_language(context, user_id)
    
    # Określ tryb i koszt kredytów
    current_mode = "no_mode"
    credit_cost = 1
    
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data']:
        user_data = context.chat_data['user_data'][user_id]
        if 'current_mode' in user_data and user_data['current_mode'] in CHAT_MODES:
            current_mode = user_data['current_mode']
            credit_cost = CHAT_MODES[current_mode]["credit_cost"]
    
    # Sprawdź, czy użytkownik ma wystarczającą liczbę kredytów
    if not check_user_credits(user_id, credit_cost):
        await update.message.reply_text(get_text("subscription_expired", language))
        return
    
    # Pobierz lub utwórz aktywną konwersację
    conversation = get_active_conversation(user_id)
    conversation_id = conversation['id']
    
    # Zapisz wiadomość użytkownika do bazy danych
    save_message(conversation_id, user_id, user_message, is_from_user=True)
    
    # Wyświetl menu kontekstowe jeśli odpowiednie
    from handlers.menu_handler import show_contextual_menu
    await show_contextual_menu(update, context, user_message)
    
    # Wyślij informację, że bot pisze
    await update.message.chat.send_action(action=ChatAction.TYPING)
    
    # Pobierz historię konwersacji
    history = get_conversation_history(conversation_id, limit=MAX_CONTEXT_MESSAGES)
    
    # Określ model do użycia - domyślny lub z trybu czatu
    model_to_use = CHAT_MODES[current_mode].get("model", DEFAULT_MODEL)
    
    # Jeśli użytkownik wybrał konkretny model, użyj go
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data']:
        user_data = context.chat_data['user_data'][user_id]
        if 'current_model' in user_data:
            model_to_use = user_data['current_model']
            # Aktualizuj koszt kredytów na podstawie modelu
            credit_cost = CREDIT_COSTS["message"].get(model_to_use, CREDIT_COSTS["message"]["default"])
    
    # Przygotuj system prompt z wybranego trybu
    system_prompt = CHAT_MODES[current_mode]["prompt"]
    
    # Przygotuj wiadomości dla API OpenAI
    messages = prepare_messages_from_history(history, user_message, system_prompt)
    
    # Wyślij początkową pustą wiadomość, którą będziemy aktualizować
    response_message = await update.message.reply_text(get_text("generating_response", language))
    
    # Zainicjuj pełną odpowiedź
    full_response = ""
    buffer = ""
    last_update = datetime.datetime.now().timestamp()
    
    # Generuj odpowiedź strumieniowo
    async for chunk in chat_completion_stream(messages, model=model_to_use):
        full_response += chunk
        buffer += chunk
        
        # Aktualizuj wiadomość co 1 sekundę lub gdy bufor jest wystarczająco duży
        current_time = datetime.datetime.now().timestamp()
        if current_time - last_update >= 1.0 or len(buffer) > 100:
            try:
                # Dodaj migający kursor na końcu wiadomości
                await response_message.edit_text(full_response + "▌", parse_mode=ParseMode.MARKDOWN)
                buffer = ""
                last_update = current_time
            except Exception as e:
                # Jeśli wystąpi błąd (np. wiadomość nie została zmieniona), kontynuuj
                pass
                
    # Aktualizuj wiadomość z pełną odpowiedzią bez kursora
    try:
        await response_message.edit_text(full_response, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        # Jeśli wystąpi błąd formatowania Markdown, wyślij bez formatowania
        await response_message.edit_text(full_response)
    
    # Zapisz odpowiedź do bazy danych
    save_message(conversation_id, user_id, full_response, is_from_user=False, model_used=model_to_use)
    
    # Odejmij kredyty
    deduct_user_credits(user_id, credit_cost, f"Wiadomość ({model_to_use})")
    
    # Sprawdź aktualny stan kredytów
    credits = get_user_credits(user_id)
    if credits < 5:
        # Dodaj przycisk doładowania kredytów
        keyboard = [[InlineKeyboardButton("🛒 " + get_text("buy_credits_btn", language, default="Kup kredyty"), callback_data="menu_credits_buy")]]
        
        await update.message.reply_text(
            f"*{get_text('low_credits_warning', language)}* {get_text('low_credits_message', language, credits=credits)}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa przesłanych dokumentów"""
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Sprawdź, czy użytkownik ma wystarczającą liczbę kredytów
    credit_cost = CREDIT_COSTS["document"]
    if not check_user_credits(user_id, credit_cost):
        await update.message.reply_text(get_text("subscription_expired", language))
        return
    
    document = update.message.document
    file_name = document.file_name
    
    # Sprawdź rozmiar pliku (limit 25MB)
    if document.file_size > 25 * 1024 * 1024:
        await update.message.reply_text("Plik jest zbyt duży. Maksymalny rozmiar to 25MB.")
        return
    
    # Pobierz plik
    message = await update.message.reply_text(get_text("analyzing_document", language))
    
    # Wyślij informację o aktywności bota
    await update.message.chat.send_action(action=ChatAction.TYPING)
    
    file = await context.bot.get_file(document.file_id)
    file_bytes = await file.download_as_bytearray()
    
    # Analizuj plik
    analysis = await analyze_document(file_bytes, file_name)
    
    # Odejmij kredyty
    deduct_user_credits(user_id, credit_cost, f"Analiza dokumentu: {file_name}")
    
    # Wyślij analizę do użytkownika
    await message.edit_text(
        f"*Analiza pliku:* {file_name}\n\n{analysis}",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Sprawdź aktualny stan kredytów
    credits = get_user_credits(user_id)
    if credits < 5:
        await update.message.reply_text(
            f"*Uwaga:* Pozostało Ci tylko *{credits}* kredytów. "
            f"Kup więcej za pomocą komendy /buy.",
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa przesłanych zdjęć"""
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Sprawdź, czy użytkownik ma wystarczającą liczbę kredytów
    credit_cost = CREDIT_COSTS["photo"]
    if not check_user_credits(user_id, credit_cost):
        await update.message.reply_text(get_text("subscription_expired", language))
        return
    
    # Wybierz zdjęcie o najwyższej rozdzielczości
    photo = update.message.photo[-1]
    
    # Pobierz zdjęcie
    message = await update.message.reply_text(get_text("analyzing_photo", language))
    
    # Wyślij informację o aktywności bota
    await update.message.chat.send_action(action=ChatAction.TYPING)
    
    file = await context.bot.get_file(photo.file_id)
    file_bytes = await file.download_as_bytearray()
    
    # Analizuj zdjęcie
    analysis = await analyze_image(file_bytes, f"photo_{photo.file_unique_id}.jpg")
    
    # Odejmij kredyty
    deduct_user_credits(user_id, credit_cost, "Analiza zdjęcia")
    
    # Wyślij analizę do użytkownika
    await message.edit_text(
        f"*Analiza zdjęcia:*\n\n{analysis}",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Sprawdź aktualny stan kredytów
    credits = get_user_credits(user_id)
    if credits < 5:
        await update.message.reply_text(
            f"*Uwaga:* Pozostało Ci tylko *{credits}* kredytów. "
            f"Kup więcej za pomocą komendy /buy.",
            parse_mode=ParseMode.MARKDOWN
        )

# Handlers dla przycisków i callbacków

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obsługa zapytań zwrotnych (z przycisków)"""
    query = update.callback_query
    
    # Najpierw sprawdzamy, czy to callback związany z menu
    from handlers.menu_handler import handle_menu_callback, handle_contextual_menu_callback
    
    # Obsługa menu głównego i kontekstowego
    menu_handled = await handle_menu_callback(update, context)
    if menu_handled:
        return
        
    context_handled = await handle_contextual_menu_callback(update, context)
    if context_handled:
        return
    
    # Poniżej znajduje się obsługa pozostałych callbacków
    await query.answer()  # Odpowiedz na callback_query, aby usunąć "zegar oczekiwania"
    
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Obsługa przycisku restartu bota
    if query.data == "restart_bot":
        restart_message = get_text("restarting_bot", language)
        await query.edit_message_text(restart_message)
        
        # Resetowanie konwersacji - tworzymy nową konwersację i czyścimy kontekst
        conversation = create_new_conversation(user_id)
        
        # Zachowujemy wybrane ustawienia użytkownika (język, model)
        user_data = {}
        if 'user_data' in context.chat_data and user_id in context.chat_data['user_data']:
            # Pobieramy tylko podstawowe ustawienia, reszta jest resetowana
            old_user_data = context.chat_data['user_data'][user_id]
            if 'language' in old_user_data:
                user_data['language'] = old_user_data['language']
            if 'current_model' in old_user_data:
                user_data['current_model'] = old_user_data['current_model']
            if 'current_mode' in old_user_data:
                user_data['current_mode'] = old_user_data['current_mode']
        
        # Resetujemy dane użytkownika w kontekście i ustawiamy tylko zachowane ustawienia
        if 'user_data' not in context.chat_data:
            context.chat_data['user_data'] = {}
        context.chat_data['user_data'][user_id] = user_data
        
        # Wykonaj podobne operacje jak w komendzie /restart
        language_name = AVAILABLE_LANGUAGES.get(language, language)
        restart_complete = get_text("language_restart_complete", language, language_display=language_name)
        
        # Wyślij nową wiadomość z potwierdzeniem restartu
        await query.message.reply_text(restart_complete, parse_mode=ParseMode.MARKDOWN)
        
        # Pokaż menu główne
        from handlers.menu_handler import show_main_menu
        
        # Utwórz sztuczny obiekt update do wyświetlenia menu
        class FakeUpdate:
            class FakeMessage:
                def __init__(self, chat_id, message_id):
                    self.chat_id = chat_id
                    self.message_id = message_id
                    
                async def reply_text(self, text, **kwargs):
                    return await context.bot.send_message(
                        chat_id=self.chat_id,
                        text=text,
                        **kwargs
                    )
            
            def __init__(self, message, user):
                self.message = message
                self.effective_user = user
        
        fake_message = FakeUpdate.FakeMessage(query.message.chat_id, query.message.message_id)
        fake_update = FakeUpdate(fake_message, query.from_user)
        await show_main_menu(fake_update, context)
        return
    
    # Obsługa historii rozmów
    elif query.data == "history_confirm_delete":
        user_id = query.from_user.id
        # Twórz nową konwersację (efektywnie "usuwając" historię)
        conversation = create_new_conversation(user_id)
        
        if conversation:
            from handlers.menu_handler import update_menu
            await update_menu(update, context, 'history')
        else:
            await query.edit_message_text(
                "Wystąpił błąd podczas czyszczenia historii.",
                parse_mode=ParseMode.MARKDOWN
            )
        return

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługa komendy /menu
    Wyświetla menu główne bota
    """
    from handlers.menu_handler import show_main_menu
    await show_main_menu(update, context)


async def handle_model_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, model_id):
    """Obsługa wyboru modelu AI"""
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Sprawdź, czy model istnieje
    if model_id not in AVAILABLE_MODELS:
        await query.edit_message_text(get_text("model_not_available", language))
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
    await query.edit_message_text(
        get_text("model_selected", language, model=model_name, credits=credit_cost), 
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_mode_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, mode_id):
    """Obsługa wyboru trybu czatu"""
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
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

# Handlers dla komend administracyjnych

async def add_credits_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Dodaje kredyty użytkownikowi (tylko dla administratorów)
    Użycie: /addcredits [user_id] [ilość]
    """
    user_id = update.effective_user.id
    
    # Sprawdź, czy użytkownik jest administratorem
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("Nie masz uprawnień do tej komendy.")
        return
    
    # Sprawdź, czy podano argumenty
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Użycie: /addcredits [user_id] [ilość]")
        return
    
    try:
        target_user_id = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Błędne argumenty. Użycie: /addcredits [user_id] [ilość]")
        return
    
    # Sprawdź, czy ilość jest poprawna
    if amount <= 0 or amount > 10000:
        await update.message.reply_text("Ilość musi być liczbą dodatnią, nie większą niż 10000.")
        return
    
    # Dodaj kredyty
    success = add_user_credits(target_user_id, amount, "Dodano przez administratora")
    
    if success:
        # Pobierz aktualny stan kredytów
        credits = get_user_credits(target_user_id)
        await update.message.reply_text(
            f"Dodano *{amount}* kredytów użytkownikowi ID: *{target_user_id}*\n"
            f"Aktualny stan kredytów: *{credits}*",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text("Wystąpił błąd podczas dodawania kredytów.")

async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Pobiera informacje o użytkowniku (tylko dla administratorów)
    Użycie: /userinfo [user_id]
    """
    user_id = update.effective_user.id
    
    # Sprawdź, czy użytkownik jest administratorem
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("Nie masz uprawnień do tej komendy.")
        return
    
    # Sprawdź, czy podano ID użytkownika
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("Użycie: /userinfo [user_id]")
        return
    
    try:
        target_user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID użytkownika musi być liczbą.")
        return
    
    # Pobierz informacje o użytkowniku
    user = get_or_create_user(target_user_id)
    credits = get_user_credits(target_user_id)
    
    if not user:
        await update.message.reply_text("Użytkownik nie istnieje w bazie danych.")
        return
    
    # Formatuj dane
    subscription_end = user.get('subscription_end_date', 'Brak subskrypcji')
    if subscription_end and subscription_end != 'Brak subskrypcji':
        end_date = datetime.datetime.fromisoformat(subscription_end.replace('Z', '+00:00'))
        subscription_end = end_date.strftime('%d.%m.%Y %H:%M')
    
    info = f"""
*Informacje o użytkowniku:*
ID: `{user['id']}`
Nazwa użytkownika: {user.get('username', 'Brak')}
Imię: {user.get('first_name', 'Brak')}
Nazwisko: {user.get('last_name', 'Brak')}
Język: {user.get('language_code', 'Brak')}
Język interfejsu: {user.get('language', 'pl')}
Subskrypcja do: {subscription_end}
Aktywny: {'Tak' if user.get('is_active', False) else 'Nie'}
Data rejestracji: {user.get('created_at', 'Brak')}

*Status kredytów:*
Dostępne kredyty: *{credits}*
"""
    
    await update.message.reply_text(info, parse_mode=ParseMode.MARKDOWN)

# Główna funkcja uruchamiająca bota

def main():
    """Funkcja uruchamiająca bota"""
    # Inicjalizacja aplikacji
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("removekeyboard", remove_keyboard))

    # Dodanie handlerów komend
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", check_status))
    application.add_handler(CommandHandler("newchat", new_chat))
    application.add_handler(CommandHandler("models", show_models))
    application.add_handler(CommandHandler("mode", show_modes))
    application.add_handler(CommandHandler("image", generate_image))
    application.add_handler(CommandHandler("restart", restart_command))
    application.add_handler(CommandHandler("menu", menu_command))  # Nowa obsługa menu
    application.add_handler(CommandHandler("setname", set_user_name))
    
    # Dodanie handlerów kodów aktywacyjnych
    application.add_handler(CommandHandler("code", code_command))
    application.add_handler(CommandHandler("gencode", admin_generate_code))
    
    # Dodanie handlerów kredytów
    application.add_handler(CommandHandler("credits", credits_command))
    application.add_handler(CommandHandler("buy", buy_command))
    application.add_handler(CommandHandler("creditstats", credit_stats_command))
    
    # Dodanie handlerów komend administracyjnych
    application.add_handler(CommandHandler("addcredits", add_credits_admin))
    application.add_handler(CommandHandler("userinfo", get_user_info))
    
    # Dodanie handlerów dokumentów i zdjęć
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Handler eksportu
    application.add_handler(CommandHandler("export", export_conversation))
    
    # Handlery tematów konwersacji
    application.add_handler(CommandHandler("theme", theme_command))
    application.add_handler(CommandHandler("notheme", notheme_command))
    
    # Dodanie handlera zapytań zwrotnych (z przycisków)
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Dodanie handlera wiadomości tekstowych (musi być na końcu)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Uruchomienie bota
    application.run_polling()

if __name__ == '__main__':
    # Aktualizacja bazy danych przed uruchomieniem
    from update_database import run_all_updates
    run_all_updates()
    
    # Uruchomienie bota
    main()