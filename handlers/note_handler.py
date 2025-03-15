# handlers/note_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import datetime
from database.sqlite_client import create_note, get_user_notes, get_note_by_id, delete_note
from utils.translations import get_text
from handlers.menu_handler import get_user_language

async def note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Tworzy nową notatkę lub wyświetla listę istniejących notatek
    Użycie: /note lub /note [tytuł] [treść]
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Jeśli podano argumenty, utwórz nową notatkę
    if context.args and len(context.args) >= 2:
        # Pierwszy argument to tytuł, reszta to treść
        title = context.args[0]
        content = ' '.join(context.args[1:])
        
        await create_new_note(update, context, title, content)
        return
    
    # W przeciwnym razie wyświetl listę notatek
    await show_notes_list(update, context)

async def create_new_note(update: Update, context: ContextTypes.DEFAULT_TYPE, title, content):
    """
    Tworzy nową notatkę
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Ograniczenie długości tytułu
    if len(title) > 50:
        title = title[:47] + "..."
    
    # Utwórz nową notatkę
    note = create_note(user_id, title, content)
    
    if not note:
        await update.message.reply_text(
            "Wystąpił błąd podczas tworzenia notatki. Spróbuj ponownie później.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await update.message.reply_text(
        f"📝 *Notatka utworzona*\n\n"
        f"Tytuł: *{title}*\n\n"
        f"{content}\n\n"
        f"Aby zobaczyć wszystkie notatki, użyj komendy /notes.",
        parse_mode=ParseMode.MARKDOWN
    )

async def notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla listę notatek użytkownika
    Użycie: /notes
    """
    await show_notes_list(update, context)

async def show_notes_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla listę notatek użytkownika
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Pobierz listę notatek użytkownika
    notes = get_user_notes(user_id)
    
    if not notes:
        await update.message.reply_text(
            "Nie masz jeszcze żadnych notatek. "
            "Aby utworzyć nową notatkę, użyj komendy /note [tytuł] [treść].",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Utwórz przyciski dla każdej notatki
    keyboard = []
    message_text = "📝 *Twoje notatki*\n\n"
    
    for i, note in enumerate(notes):
        title = note['title'] or f"Notatka #{note['id']}"
        message_text += f"{i+1}. {title}\n"
        
        keyboard.append([
            InlineKeyboardButton(
                f"📄 {title}", 
                callback_data=f"note_view_{note['id']}"
            )
        ])
    
    # Dodaj przycisk do tworzenia nowej notatki
    keyboard.append([
        InlineKeyboardButton("➕ Utwórz nową notatkę", callback_data="new_note")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def handle_note_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługuje przyciski związane z notatkami
    """
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    await query.answer()
    
    # Obsługa przycisku tworzenia nowej notatki
    if query.data == "new_note":
        await query.edit_message_text(
            "Aby utworzyć nową notatkę, użyj komendy /note [tytuł] [treść]\n\n"
            "Na przykład: /note Zakupy Mleko, chleb, masło",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Obsługa przycisku wyświetlania notatki
    if query.data.startswith("note_view_"):
        note_id = int(query.data.split("_")[2])
        note = get_note_by_id(note_id)
        
        if not note or note['user_id'] != user_id:
            await query.edit_message_text(
                "Wystąpił błąd podczas wyświetlania notatki. Spróbuj ponownie później.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Utwórz przyciski akcji dla notatki
        keyboard = [
            [
                InlineKeyboardButton("🗑️ Usuń notatkę", callback_data=f"note_delete_{note['id']}"),
                InlineKeyboardButton("🔙 Powrót", callback_data="note_list")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Formatuj datę utworzenia
        created_at = datetime.datetime.fromisoformat(note['created_at'].replace('Z', '+00:00'))
        formatted_date = created_at.astimezone(datetime.timezone.utc).strftime("%d.%m.%Y %H:%M")
        
        await query.edit_message_text(
            f"📝 *{note['title']}*\n\n"
            f"{note['content']}\n\n"
            f"_Utworzono: {formatted_date}_",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        return
    
    # Obsługa przycisku usuwania notatki
    if query.data.startswith("note_delete_"):
        note_id = int(query.data.split("_")[2])
        note = get_note_by_id(note_id)
        
        if not note or note['user_id'] != user_id:
            await query.edit_message_text(
                "Wystąpił błąd podczas usuwania notatki. Spróbuj ponownie później.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Utwórz przyciski potwierdzenia usunięcia
        keyboard = [
            [
                InlineKeyboardButton("✅ Tak, usuń", callback_data=f"note_confirm_delete_{note['id']}"),
                InlineKeyboardButton("❌ Nie, anuluj", callback_data=f"note_view_{note['id']}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Czy na pewno chcesz usunąć notatkę *{note['title']}*?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        return
    
    # Obsługa przycisku potwierdzenia usunięcia notatki
    if query.data.startswith("note_confirm_delete_"):
        note_id = int(query.data.split("_")[3])
        
        # Usuń notatkę
        success = delete_note(note_id)
        
        if success:
            await query.edit_message_text(
                "✅ Notatka została usunięta!",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                "Wystąpił błąd podczas usuwania notatki. Spróbuj ponownie później.",
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    # Obsługa przycisku powrotu do listy notatek
    if query.data == "note_list":
        await show_notes_list_inline(update, context)
        return

async def show_notes_list_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla listę notatek użytkownika inline (dla przycisków)
    """
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Pobierz listę notatek użytkownika
    notes = get_user_notes(user_id)
    
    if not notes:
        await query.edit_message_text(
            "Nie masz jeszcze żadnych notatek. "
            "Aby utworzyć nową notatkę, użyj komendy /note [tytuł] [treść].",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Utwórz przyciski dla każdej notatki
    keyboard = []
    message_text = "📝 *Twoje notatki*\n\n"
    
    for i, note in enumerate(notes):
        title = note['title'] or f"Notatka #{note['id']}"
        message_text += f"{i+1}. {title}\n"
        
        keyboard.append([
            InlineKeyboardButton(
                f"📄 {title}", 
                callback_data=f"note_view_{note['id']}"
            )
        ])
    
    # Dodaj przycisk do tworzenia nowej notatki
    keyboard.append([
        InlineKeyboardButton("➕ Utwórz nową notatkę", callback_data="new_note")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )