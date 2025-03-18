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

async def analyze_document(file_content, file_name, mode="analyze", target_language="en"):
    """
    Analizuj lub tłumacz dokument za pomocą OpenAI API
    
    Args:
        file_content (bytes): Zawartość pliku
        file_name (str): Nazwa pliku
        mode (str): Tryb analizy: "analyze" (domyślnie) lub "translate"
        target_language (str): Docelowy język tłumaczenia (dwuliterowy kod)
        
    Returns:
        str: Analiza dokumentu, tłumaczenie lub informacja o błędzie
    """
    try:
        # Określamy typ zawartości na podstawie rozszerzenia pliku
        file_extension = os.path.splitext(file_name)[1].lower()
        
        # Przygotuj odpowiednie instrukcje w zależności od trybu
        if mode == "translate":
            language_names = {
                "en": "angielski",
                "pl": "polski",
                "ru": "rosyjski",
                "fr": "francuski",
                "de": "niemiecki",
                "es": "hiszpański",
                "it": "włoski",
                "zh": "chiński"
            }
            target_lang_name = language_names.get(target_language, target_language)
            
            system_instruction = f"Jesteś profesjonalnym tłumaczem. Twoim zadaniem jest przetłumaczenie tekstu z dokumentu na język {target_lang_name}. Zachowaj oryginalny format tekstu."
            user_instruction = f"Przetłumacz tekst z pliku {file_name} na język {target_lang_name}. Zachowaj strukturę i formatowanie oryginału."
        else:  # tryb analyze
            system_instruction = "Jesteś pomocnym asystentem, który analizuje dokumenty i pliki."
            user_instruction = f"Przeanalizuj plik {file_name} i opisz jego zawartość. Podaj kluczowe informacje i wnioski."
        
        messages = [
            {
                "role": "system", 
                "content": system_instruction
            },
            {
                "role": "user",
                "content": user_instruction
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
            model="gpt-4o",  # Użyjemy GPT-4o dla lepszej jakości
            messages=messages,
            max_tokens=1500  # Zwiększamy limit tokenów dla dłuższych tekstów
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Błąd analizy dokumentu: {e}")
        return f"Przepraszam, wystąpił błąd podczas analizy dokumentu: {str(e)}"

async def analyze_document(file_content, file_name, mode="analyze"):
    """
    Analizuj lub tłumacz dokument za pomocą OpenAI API
    
    Args:
        file_content (bytes): Zawartość pliku
        file_name (str): Nazwa pliku
        mode (str): Tryb analizy: "analyze" (domyślnie) lub "translate"
    
    Returns:
        str: Analiza dokumentu, tłumaczenie lub informacja o błędzie
    """
    try:
        # Określamy typ zawartości na podstawie rozszerzenia pliku
        file_extension = os.path.splitext(file_name)[1].lower()
        
        # Przygotuj odpowiednie instrukcje w zależności od trybu
        if mode == "translate":
            system_instruction = "Jesteś profesjonalnym tłumaczem. Twoim zadaniem jest przetłumaczenie tekstu z dokumentu na język polski. Zachowaj oryginalny format tekstu."
            user_instruction = f"Przetłumacz tekst z pliku {file_name} na język polski. Zachowaj strukturę i formatowanie oryginału."
        else:  # tryb analyze
            system_instruction = "Jesteś pomocnym asystentem, który analizuje dokumenty i pliki."
            user_instruction = f"Przeanalizuj plik {file_name} i opisz jego zawartość. Podaj kluczowe informacje i wnioski."
        
        messages = [
            {
                "role": "system", 
                "content": system_instruction
            },
            {
                "role": "user",
                "content": user_instruction
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
            model="gpt-4o",  # Użyjemy GPT-4o dla lepszej jakości
            messages=messages,
            max_tokens=1500  # Zwiększamy limit tokenów dla dłuższych tekstów
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Błąd analizy dokumentu: {e}")
        return f"Przepraszam, wystąpił błąd podczas analizy dokumentu: {str(e)}"

async def analyze_image(image_content, image_name, mode="analyze", target_language="en"):
    """
    Analizuj obraz za pomocą OpenAI API
    
    Args:
        image_content (bytes): Zawartość obrazu
        image_name (str): Nazwa obrazu
        mode (str): Tryb analizy: "analyze" (domyślnie) lub "translate"
        target_language (str): Docelowy język tłumaczenia (dwuliterowy kod)
        
    Returns:
        str: Analiza obrazu lub tłumaczenie tekstu
    """
    try:
        # Kodowanie obrazu do Base64
        base64_image = base64.b64encode(image_content).decode('utf-8')
        
        # Przygotuj odpowiednie instrukcje bazując na trybie
        if mode == "translate":
            language_names = {
                "en": "angielski",
                "pl": "polski",
                "ru": "rosyjski",
                "fr": "francuski",
                "de": "niemiecki",
                "es": "hiszpański",
                "it": "włoski",
                "zh": "chiński"
            }
            target_lang_name = language_names.get(target_language, target_language)
            
            system_instruction = f"Jesteś pomocnym asystentem, który tłumaczy tekst z obrazów na język {target_lang_name}. Skup się tylko na odczytaniu i przetłumaczeniu tekstu widocznego na obrazie."
            user_instruction = f"Odczytaj cały tekst widoczny na obrazie i przetłumacz go na język {target_lang_name}. Podaj tylko tłumaczenie, bez dodatkowych wyjaśnień."
        else:  # tryb analyze
            system_instruction = "Jesteś pomocnym asystentem, który analizuje obrazy. Twoje odpowiedzi powinny być szczegółowe, ale zwięzłe."
            user_instruction = "Opisz ten obraz. Co widzisz? Podaj szczegółową, ale zwięzłą analizę zawartości obrazu."
        
        messages = [
            {
                "role": "system", 
                "content": system_instruction
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_instruction
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
            model="gpt-4o",  # Używamy GPT-4o zamiast zdeprecjonowanego gpt-4-vision-preview
            messages=messages,
            max_tokens=800  # Zwiększona liczba tokenów dla dłuższych tekstów
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Błąd analizy obrazu: {e}")
        return f"Przepraszam, wystąpił błąd podczas analizy obrazu: {str(e)}"