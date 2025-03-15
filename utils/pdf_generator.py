# utils/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import cm
import io
import os
import datetime

def generate_conversation_pdf(conversation, user_info, bot_name="AI Bot"):
    """
    Generuje plik PDF z historią konwersacji
    
    Args:
        conversation (list): Lista wiadomości z konwersacji
        user_info (dict): Informacje o użytkowniku
        bot_name (str): Nazwa bota
        
    Returns:
        BytesIO: Bufor zawierający wygenerowany plik PDF
    """
    buffer = io.BytesIO()
    
    # Konfiguracja dokumentu
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Style
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='UserMessage',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='BotMessage',
        parent=styles['Normal'],
        fontName='Helvetica',
        leftIndent=20,
        spaceAfter=12
    ))
    
    # Elementy dokumentu
    elements = []
    
    # Nagłówek
    title = f"Konwersacja z {bot_name}"
    elements.append(Paragraph(title, styles['Title']))
    
    # Metadane
    current_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    metadata_text = f"Eksportowano: {current_time}"
    if user_info.get('username'):
        metadata_text += f"<br/>Użytkownik: {user_info.get('username')}"
    elements.append(Paragraph(metadata_text, styles['Italic']))
    elements.append(Spacer(1, 0.5*cm))
    
    # Treść konwersacji
    for msg in conversation:
        if msg['is_from_user']:
            icon = "👤 "  # Ikona użytkownika
            style = styles['UserMessage']
            content = f"{icon}Ty: {msg['content']}"
        else:
            icon = "🤖 "  # Ikona bota
            style = styles['BotMessage']
            content = f"{icon}{bot_name}: {msg['content']}"
        
        # Dodaj datę i godzinę wiadomości, jeśli są dostępne
        if 'created_at' in msg and msg['created_at']:
            try:
                # Konwersja formatu daty
                if isinstance(msg['created_at'], str) and 'T' in msg['created_at']:
                    dt = datetime.datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00'))
                    time_str = dt.strftime("%d-%m-%Y %H:%M")
                    content += f"<br/><font size=8 color=gray>{time_str}</font>"
            except Exception as e:
                # Ignoruj błędy konwersji daty
                pass
                
        elements.append(Paragraph(content, style))
    
    # Stopka
    elements.append(Spacer(1, 1*cm))
    footer_text = f"Wygenerowano przez {bot_name} • {current_time}"
    elements.append(Paragraph(footer_text, styles['Italic']))
    
    # Wygeneruj dokument
    doc.build(elements)
    
    # Zresetuj pozycję w buforze i zwróć go
    buffer.seek(0)
    return buffer