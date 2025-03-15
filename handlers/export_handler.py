# handlers/export_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction
from database.sqlite_client import get_active_conversation, get_conversation_history, get_or_create_user
from utils.pdf_generator import generate_conversation_pdf
from config import BOT_NAME
from utils.translations import get_text
from handlers.menu_handler import get_user_language
import io

async def export_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Eksportuje aktualną konwersację użytkownika do PDF
    Użycie: /export
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Informuj użytkownika o rozpoczęciu procesu
    status_message = await update.message.reply_text(
        "⏳ Generowanie pliku PDF z historią konwersacji..."
    )
    
    # Pokazuj animację "bot pisze"
    await update.message.chat.send_action(action=ChatAction.UPLOAD_DOCUMENT)
    
    # Pobierz aktywną konwersację
    conversation = get_active_conversation(user_id)
    
    if not conversation:
        await status_message.edit_text("Nie znaleziono aktywnej konwersacji.")
        return
    
    # Pobierz historię konwersacji
    history = get_conversation_history(conversation['id'])
    
    if not history:
        await status_message.edit_text("Historia konwersacji jest pusta.")
        return
    
    # Pobierz dane użytkownika
    user_info = get_or_create_user(user_id)
    
    # Generuj PDF
    try:
        pdf_buffer = generate_conversation_pdf(history, user_info, BOT_NAME)
        
        # Przygotuj nazwę pliku
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_name = f"Konwersacja_{BOT_NAME}_{current_date}.pdf"
        
        # Wyślij plik PDF
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=pdf_buffer,
            filename=file_name,
            caption="📄 Historia konwersacji w formacie PDF"
        )
        
        # Usuń wiadomość o statusie
        await status_message.delete()
        
    except Exception as e:
        print(f"Błąd podczas generowania PDF: {e}")
        await status_message.edit_text(
            "Wystąpił błąd podczas generowania pliku PDF. Spróbuj ponownie później."
        )