# handlers/reminder_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import datetime
import pytz
import re
from database.sqlite_client import create_reminder, get_user_pending_reminders, complete_reminder, get_due_reminders
from utils.translations import get_text
from handlers.menu_handler import get_user_language

# Wyrażenia regularne do rozpoznawania wzorców czasowych
TIME_PATTERNS = [
    (r'(?:za|po|w ciągu|)\s*(\d+)\s*(?:min(?:ut(?:a|y|))|m)', lambda m: datetime.timedelta(minutes=int(m.group(1)))),
    (r'(?:za|po|w ciągu|)\s*(\d+)\s*(?:godzin(?:a|y|)|h)', lambda m: datetime.timedelta(hours=int(m.group(1)))),
    (r'(?:za|po|w ciągu|)\s*(\d+)\s*(?:dz(?:ień|ni|)|d)', lambda m: datetime.timedelta(days=int(m.group(1)))),
    (r'(?:o|o godzinie)\s*(\d{1,2})[:\.]?(\d{2})', 
     lambda m: datetime.datetime.combine(
         datetime.date.today() if datetime.time(int(m.group(1)), int(m.group(2))) > datetime.datetime.now().time() 
         else datetime.date.today() + datetime.timedelta(days=1), 
         datetime.time(int(m.group(1)), int(m.group(2)))
     ) - datetime.datetime.now())
]

async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Tworzy nowe przypomnienie
    Użycie: /remind [czas] [treść]
    Przykłady:
    /remind 30m Zadzwoń do klienta
    /remind 2h Spotkanie z zespołem
    /remind 18:00 Trening
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Sprawdź, czy podano argumenty
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Użycie: /remind [czas] [treść]\n\n"
            "Przykłady:\n"
            "/remind 30m Zadzwoń do klienta\n"
            "/remind 2h Spotkanie z zespołem\n"
            "/remind 18:00 Trening",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Połącz wszystkie argumenty w jedną wiadomość
    message = ' '.join(context.args)
    
    # Spróbuj rozpoznać wzorzec czasowy
    remind_delta = None
    content = message
    
    for pattern, time_func in TIME_PATTERNS:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            remind_delta = time_func(match)
            # Usuń dopasowany wzorzec z treści
            content = re.sub(pattern, '', message, 1, re.IGNORECASE).strip()
            break
    
    # Jeśli nie rozpoznano czasu, spróbuj rozpoznać go jako pierwszy argument
    if not remind_delta and len(context.args) >= 2:
        time_arg = context.args[0].lower()
        
        # Sprawdź różne formaty czasu
        if re.match(r'^\d+m$', time_arg):
            minutes = int(time_arg[:-1])
            remind_delta = datetime.timedelta(minutes=minutes)
            content = ' '.join(context.args[1:])
        elif re.match(r'^\d+h$', time_arg):
            hours = int(time_arg[:-1])
            remind_delta = datetime.timedelta(hours=hours)
            content = ' '.join(context.args[1:])
        elif re.match(r'^\d+d$', time_arg):
            days = int(time_arg[:-1])
            remind_delta = datetime.timedelta(days=days)
            content = ' '.join(context.args[1:])
        elif re.match(r'^\d{1,2}:\d{2}$', time_arg):
            hour, minute = map(int, time_arg.split(':'))
            now = datetime.datetime.now()
            remind_time = datetime.datetime.combine(
                datetime.date.today() if datetime.time(hour, minute) > now.time() 
                else datetime.date.today() + datetime.timedelta(days=1), 
                datetime.time(hour, minute)
            )
            remind_delta = remind_time - now
            content = ' '.join(context.args[1:])
    
    if not remind_delta:
        await update.message.reply_text(
            "Nie udało się rozpoznać czasu przypomnienia. "
            "Podaj czas w formacie jak w przykładach:\n\n"
            "/remind 30m Zadzwoń do klienta\n"
            "/remind 2h Spotkanie z zespołem\n"
            "/remind 18:00 Trening",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Oblicz rzeczywisty czas przypomnienia
    now = datetime.datetime.now(pytz.UTC)
    remind_at = now + remind_delta
    
    # Utwórz przypomnienie
    reminder = create_reminder(user_id, content, remind_at)
    
    if not reminder:
        await update.message.reply_text(
            "Wystąpił błąd podczas tworzenia przypomnienia. Spróbuj ponownie później.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Zaplanuj przypomnienie w kontekście bota
    context.job_queue.run_once(
        send_reminder,
        remind_delta.total_seconds(),
        data={'user_id': user_id, 'reminder_id': reminder['id'], 'content': content}
    )
    
    # Formatuj czas przypomnienia
    formatted_time = remind_at.astimezone(pytz.timezone('Europe/Warsaw')).strftime("%d.%m.%Y %H:%M")
    
    await update.message.reply_text(
        f"⏰ *Przypomnienie ustawione*\n\n"
        f"Treść: {content}\n"
        f"Czas: {formatted_time}\n\n"
        f"Powiadomię Cię o wyznaczonym czasie!",
        parse_mode=ParseMode.MARKDOWN
    )

async def reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla listę przypomnień użytkownika
    Użycie: /reminders
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Pobierz listę przypomnień użytkownika
    reminders = get_user_pending_reminders(user_id)
    
    if not reminders:
        await update.message.reply_text(
            "Nie masz żadnych aktywnych przypomnień. "
            "Aby utworzyć nowe przypomnienie, użyj komendy /remind.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Utwórz przyciski dla każdego przypomnienia
    keyboard = []
    message_text = "⏰ *Twoje przypomnienia*\n\n"
    
    for i, reminder in enumerate(reminders):
        try:
            remind_at = datetime.datetime.fromisoformat(reminder['remind_at'].replace('Z', '+00:00'))
            formatted_time = remind_at.astimezone(pytz.timezone('Europe/Warsaw')).strftime("%d.%m.%Y %H:%M")
            
            message_text += f"{i+1}. {formatted_time} - {reminder['content']}\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"✅ Oznacz #{i+1} jako wykonane", 
                    callback_data=f"reminder_complete_{reminder['id']}"
                )
            ])
        except Exception as e:
            print(f"Błąd przy formatowaniu przypomnienia: {e}")
    
    # Dodaj przycisk do tworzenia nowego przypomnienia
    keyboard.append([
        InlineKeyboardButton("➕ Utwórz nowe przypomnienie", callback_data="new_reminder")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """
    Wysyła przypomnienie do użytkownika
    """
    job = context.job
    user_id = job.data['user_id']
    reminder_id = job.data['reminder_id']
    content = job.data['content']
    
    # Oznacz przypomnienie jako zakończone
    complete_reminder(reminder_id)
    
    # Wyślij przypomnienie
    await context.bot.send_message(
        chat_id=user_id,
        text=f"⏰ *PRZYPOMNIENIE*\n\n{content}",
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_reminder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługuje przyciski związane z przypomnieniami
    """
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    await query.answer()
    
    # Obsługa przycisku tworzenia nowego przypomnienia
    if query.data == "new_reminder":
        await query.edit_message_text(
            "Aby utworzyć nowe przypomnienie, użyj komendy /remind [czas] [treść]\n\n"
            "Przykłady:\n"
            "/remind 30m Zadzwoń do klienta\n"
            "/remind 2h Spotkanie z zespołem\n"
            "/remind 18:00 Trening",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Obsługa przycisku oznaczania przypomnienia jako wykonane
    if query.data.startswith("reminder_complete_"):
        reminder_id = int(query.data.split("_")[2])
        
        # Oznacz przypomnienie jako zakończone
        success = complete_reminder(reminder_id)
        
        if success:
            await query.edit_message_text(
                "✅ Przypomnienie zostało oznaczone jako wykonane!",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                "Wystąpił błąd podczas oznaczania przypomnienia jako wykonane. Spróbuj ponownie później.",
                parse_mode=ParseMode.MARKDOWN
            )
        return

async def check_due_reminders(context: ContextTypes.DEFAULT_TYPE):
    """
    Sprawdza przypomnienia, dla których nadszedł czas i wysyła je do użytkowników
    """
    # Pobierz przypomnienia, dla których nadszedł czas
    reminders = get_due_reminders()
    
    for reminder in reminders:
        # Oznacz przypomnienie jako zakończone
        complete_reminder(reminder['id'])
        
        # Wyślij przypomnienie
        await context.bot.send_message(
            chat_id=reminder['user_id'],
            text=f"⏰ *PRZYPOMNIENIE*\n\n{reminder['content']}",
            parse_mode=ParseMode.MARKDOWN
        )