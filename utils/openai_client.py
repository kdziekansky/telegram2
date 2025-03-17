import openai
from openai import AsyncOpenAI
import base64
import os
import asyncio
from config import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT, DALL_E_MODEL
print(f"API Key is {'set' if OPENAI_API_KEY else 'NOT SET'}")
print(f"API Key length: {len(OPENAI_API_KEY) if OPENAI_API_KEY else 0}")

# Inicjalizacja klienta OpenAI
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def chat_completion_stream(messages, model=DEFAULT_MODEL):
    """
    Wygeneruj odpowiedź strumieniową z OpenAI API
    
    Args:
        messages (list): Lista wiadomości w formacie OpenAI
        model (str, optional): Model do użycia. Domyślnie DEFAULT_MODEL.
    
    Returns:
        async generator: Generator zwracający fragmenty odpowiedzi
    """
    try:
        print(f"Wywołuję OpenAI API z modelem {model}")
        # Dodaj opóźnienie w przypadku gdy używamy GPT-4 (aby uniknąć rate limitów)
        if "gpt-4" in model:
            import asyncio
            await asyncio.sleep(0.5)
            
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        error_msg = f"Błąd API OpenAI (stream): {str(e)}"
        print(error_msg)
        yield error_msg


async def chat_completion(messages, model=DEFAULT_MODEL):
    """
    Wygeneruj całą odpowiedź z OpenAI API (niestrumieniowa)
    
    Args:
        messages (list): Lista wiadomości w formacie OpenAI
        model (str, optional): Model do użycia. Domyślnie DEFAULT_MODEL.
    
    Returns:
        str: Wygenerowana odpowiedź
    """
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Błąd API OpenAI: {e}")
        return f"Przepraszam, wystąpił błąd podczas generowania odpowiedzi: {str(e)}"

def prepare_messages_from_history(history, user_message, system_prompt=None):
    """
    Przygotuj listę wiadomości dla API OpenAI na podstawie historii konwersacji
    
    Args:
        history (list): Lista wiadomości z historii konwersacji
        user_message (str): Aktualna wiadomość użytkownika
        system_prompt (str, optional): Prompt systemowy. Jeśli None, użyty zostanie DEFAULT_SYSTEM_PROMPT.
    
    Returns:
        list: Lista wiadomości w formacie OpenAI
    """
    # Zabezpieczenie przed None - używamy domyślnego prompta, jeśli system_prompt jest None
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Dodaj wiadomości z historii
    for msg in history:
        role = "user" if msg["is_from_user"] else "assistant"
        # Upewniamy się, że content nie jest None
        content = msg["content"] if msg["content"] is not None else ""
        messages.append({
            "role": role,
            "content": content
        })
    
    # Dodaj aktualną wiadomość użytkownika
    messages.append({"role": "user", "content": user_message if user_message is not None else ""})
    
    return messages

async def generate_image_dall_e(prompt):
    """
    Wygeneruj obraz za pomocą DALL-E 3
    
    Args:
        prompt (str): Opis obrazu do wygenerowania
    
    Returns:
        str: URL wygenerowanego obrazu lub błąd
    """
    try:
        response = await client.images.generate(
            model=DALL_E_MODEL,
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        return response.data[0].url
    except Exception as e:
        print(f"Błąd generowania obrazu: {e}")
        return None

async def analyze_document(file_content, file_name):
    """
    Analizuj dokument za pomocą OpenAI API
    
    Args:
        file_content (bytes): Zawartość pliku
        file_name (str): Nazwa pliku
    
    Returns:
        str: Analiza dokumentu
    """
    try:
        # Określamy typ zawartości na podstawie rozszerzenia pliku
        file_extension = os.path.splitext(file_name)[1].lower()
        
        messages = [
            {
                "role": "system", 
                "content": "Jesteś pomocnym asystentem, który analizuje dokumenty i pliki."
            },
            {
                "role": "user",
                "content": f"Przeanalizuj plik {file_name} i opisz jego zawartość. Podaj kluczowe informacje i wnioski."
            }
        ]
        
        # Dla plików tekstowych możemy dodać zawartość bezpośrednio
        if file_extension in ['.txt', '.csv', '.md', '.json', '.xml', '.html', '.js', '.py', '.cpp', '.c', '.java']:
            try:
                # Próbuj odkodować jako UTF-8
                file_text = file_content.decode('utf-8')
                messages[1]["content"] += f"\n\nZawartość pliku:\n\n{file_text}"
            except UnicodeDecodeError:
                # Jeśli nie możemy odkodować, traktuj jako plik binarny
                messages[1]["content"] += "\n\nPlik zawiera dane binarne, które nie mogą być wyświetlone jako tekst."
        
        response = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Błąd analizy dokumentu: {e}")
        return f"Przepraszam, wystąpił błąd podczas analizy dokumentu: {str(e)}"

async def analyze_image(image_content, image_name):
    """
    Analizuj obraz za pomocą OpenAI API
    
    Args:
        image_content (bytes): Zawartość obrazu
        image_name (str): Nazwa obrazu
    
    Returns:
        str: Analiza obrazu
    """
    try:
        # Kodowanie obrazu do Base64
        base64_image = base64.b64encode(image_content).decode('utf-8')
        
        messages = [
            {
                "role": "system", 
                "content": "Jesteś pomocnym asystentem, który analizuje obrazy."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Opisz ten obraz. Co widzisz? Podaj szczegółową analizę."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        response = await client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Błąd analizy obrazu: {e}")
        return f"Przepraszam, wystąpił błąd podczas analizy obrazu: {str(e)}"