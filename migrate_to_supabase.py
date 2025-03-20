import sqlite3
import datetime
import pytz
import logging
import os
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

# Konfiguracja loggera, aby wyświetlał wszystkie komunikaty na konsoli
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()  # Dodajemy handler dla konsoli
    ]
)
logger = logging.getLogger(__name__)

# Ścieżka do pliku bazy danych SQLite
DB_PATH = "bot_database.sqlite"

# Inicjalizacja klienta Supabase
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Pomyślnie zainicjalizowano klienta Supabase")
except Exception as e:
    logger.error(f"Błąd inicjalizacji klienta Supabase: {e}")
    supabase = None

def check_sqlite_database():
    """Sprawdza zawartość bazy danych SQLite"""
    try:
        # Połączenie z bazą SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pobierz listę tabel
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        logger.info(f"Znalezione tabele w bazie SQLite: {[table[0] for table in tables]}")
        
        # Sprawdź zawartość kilku kluczowych tabel
        for table_name in ['users', 'conversations', 'messages', 'user_credits']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                logger.info(f"Tabela {table_name} zawiera {count} rekordów")
            except Exception as e:
                logger.warning(f"Nie można sprawdzić zawartości tabeli {table_name}: {e}")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Błąd podczas sprawdzania bazy SQLite: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def migrate_users():
    """Migruje użytkowników z SQLite do Supabase"""
    try:
        logger.info("Rozpoczynam migrację użytkowników...")
        
        # Połączenie z bazą SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pobierz wszystkich użytkowników
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        # Pobierz nazwy kolumn
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        logger.info(f"Znaleziono {len(users)} użytkowników do migracji")
        logger.info(f"Kolumny tabeli users: {columns}")
        
        migrated_count = 0
        for user in users:
            # Utwórz słownik z danymi użytkownika
            user_data = {columns[i]: user[i] for i in range(len(columns)) if i < len(user)}
            
            if 'id' not in user_data or user_data['id'] is None:
                logger.warning(f"Pomijam użytkownika bez ID: {user_data}")
                continue
                
            logger.info(f"Próba migracji użytkownika: {user_data['id']}")
            
            # Przekształć wartości logiczne
            if 'is_active' in user_data:
                user_data['is_active'] = bool(user_data['is_active'])
            
            # Upewnij się, że mamy właściwy format daty
            if 'created_at' in user_data and user_data['created_at']:
                try:
                    dt = datetime.datetime.fromisoformat(user_data['created_at'].replace('Z', '+00:00'))
                    user_data['created_at'] = dt.isoformat()
                except Exception as e:
                    logger.warning(f"Błąd konwersji daty created_at dla użytkownika {user_data['id']}: {e}")
                    user_data['created_at'] = datetime.datetime.now(pytz.UTC).isoformat()
            else:
                user_data['created_at'] = datetime.datetime.now(pytz.UTC).isoformat()
            
            if 'subscription_end_date' in user_data and user_data['subscription_end_date']:
                try:
                    dt = datetime.datetime.fromisoformat(user_data['subscription_end_date'].replace('Z', '+00:00'))
                    user_data['subscription_end_date'] = dt.isoformat()
                except Exception as e:
                    logger.warning(f"Błąd konwersji daty subscription_end_date dla użytkownika {user_data['id']}: {e}")
                    user_data['subscription_end_date'] = None
            
            # Inicjalizuj pola, które mogą być wymagane przez Supabase
            if 'language' not in user_data or not user_data['language']:
                user_data['language'] = user_data.get('language_code', 'pl')
            
            if 'messages_used' not in user_data:
                user_data['messages_used'] = 0
                
            if 'messages_limit' not in user_data:
                user_data['messages_limit'] = 0
            
            # Dodaj użytkownika do Supabase
            try:
                # Sprawdź czy użytkownik już istnieje
                response = supabase.table('users').select('id').eq('id', user_data['id']).execute()
                
                if response.data:
                    # Aktualizuj istniejącego użytkownika
                    logger.info(f"Aktualizuję istniejącego użytkownika {user_data['id']}")
                    update_response = supabase.table('users').update(user_data).eq('id', user_data['id']).execute()
                    logger.info(f"Zaktualizowano użytkownika {user_data['id']}")
                else:
                    # Dodaj nowego użytkownika
                    logger.info(f"Dodaję nowego użytkownika {user_data['id']}")
                    insert_response = supabase.table('users').insert(user_data).execute()
                    logger.info(f"Dodano użytkownika {user_data['id']}")
                
                migrated_count += 1
            except Exception as e:
                logger.error(f"Błąd przy migracji użytkownika {user_data['id']}: {e}")
                logger.error(f"Dane użytkownika: {user_data}")
        
        conn.close()
        logger.info(f"Zmigrowano {migrated_count} użytkowników")
        return migrated_count
    except Exception as e:
        logger.error(f"Błąd podczas migracji użytkowników: {e}")
        if 'conn' in locals():
            conn.close()
        return 0

def migrate_user_credits():
    """Migruje kredyty użytkowników z SQLite do Supabase"""
    try:
        # Połączenie z bazą SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pobierz kredyty wszystkich użytkowników
        cursor.execute("SELECT * FROM user_credits")
        credits = cursor.fetchall()
        
        # Pobierz nazwy kolumn
        cursor.execute("PRAGMA table_info(user_credits)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrated_count = 0
        for credit in credits:
            # Utwórz słownik z danymi kredytów
            credit_data = {columns[i]: credit[i] for i in range(len(columns))}
            
            # Upewnij się, że mamy właściwy format daty
            if 'last_purchase_date' in credit_data and credit_data['last_purchase_date']:
                try:
                    dt = datetime.datetime.fromisoformat(credit_data['last_purchase_date'].replace('Z', '+00:00'))
                    credit_data['last_purchase_date'] = dt.isoformat()
                except:
                    credit_data['last_purchase_date'] = None
            
            # Dodaj kredyty do Supabase
            try:
                # Sprawdź czy rekord już istnieje
                response = supabase.table('user_credits').select('user_id').eq('user_id', credit_data['user_id']).execute()
                
                if response.data:
                    # Aktualizuj istniejący rekord
                    supabase.table('user_credits').update(credit_data).eq('user_id', credit_data['user_id']).execute()
                else:
                    # Dodaj nowy rekord
                    supabase.table('user_credits').insert(credit_data).execute()
                
                migrated_count += 1
            except Exception as e:
                logger.error(f"Błąd przy migracji kredytów użytkownika {credit_data['user_id']}: {e}")
        
        conn.close()
        logger.info(f"Zmigrowano kredyty dla {migrated_count} użytkowników")
        return migrated_count
    except Exception as e:
        logger.error(f"Błąd podczas migracji kredytów użytkowników: {e}")
        if 'conn' in locals():
            conn.close()
        return 0

def migrate_credit_transactions():
    """Migruje transakcje kredytowe z SQLite do Supabase"""
    try:
        # Połączenie z bazą SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pobierz wszystkie transakcje
        cursor.execute("SELECT * FROM credit_transactions")
        transactions = cursor.fetchall()
        
        # Pobierz nazwy kolumn
        cursor.execute("PRAGMA table_info(credit_transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrated_count = 0
        for transaction in transactions:
            # Utwórz słownik z danymi transakcji
            transaction_data = {columns[i]: transaction[i] for i in range(len(columns))}
            
            # Usuń pole id, aby Supabase mógł wygenerować własne
            if 'id' in transaction_data:
                del transaction_data['id']
            
            # Upewnij się, że mamy właściwy format daty
            if 'created_at' in transaction_data and transaction_data['created_at']:
                try:
                    dt = datetime.datetime.fromisoformat(transaction_data['created_at'].replace('Z', '+00:00'))
                    transaction_data['created_at'] = dt.isoformat()
                except:
                    transaction_data['created_at'] = datetime.datetime.now(pytz.UTC).isoformat()
            
            # Dodaj transakcję do Supabase
            try:
                supabase.table('credit_transactions').insert(transaction_data).execute()
                migrated_count += 1
            except Exception as e:
                logger.error(f"Błąd przy migracji transakcji użytkownika {transaction_data['user_id']}: {e}")
        
        conn.close()
        logger.info(f"Zmigrowano {migrated_count} transakcji kredytowych")
        return migrated_count
    except Exception as e:
        logger.error(f"Błąd podczas migracji transakcji kredytowych: {e}")
        if 'conn' in locals():
            conn.close()
        return 0

def migrate_credit_packages():
    """Migruje pakiety kredytów z SQLite do Supabase"""
    try:
        # Połączenie z bazą SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pobierz wszystkie pakiety
        cursor.execute("SELECT * FROM credit_packages")
        packages = cursor.fetchall()
        
        # Pobierz nazwy kolumn
        cursor.execute("PRAGMA table_info(credit_packages)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrated_count = 0
        for package in packages:
            # Utwórz słownik z danymi pakietu
            package_data = {columns[i]: package[i] for i in range(len(columns))}
            
            # Usuń pole id, aby Supabase mógł wygenerować własne
            if 'id' in package_data:
                del package_data['id']
            
            # Przekształć wartości logiczne
            if 'is_active' in package_data:
                package_data['is_active'] = bool(package_data['is_active'])
            
            # Upewnij się, że mamy właściwy format daty
            if 'created_at' in package_data and package_data['created_at']:
                try:
                    dt = datetime.datetime.fromisoformat(package_data['created_at'].replace('Z', '+00:00'))
                    package_data['created_at'] = dt.isoformat()
                except:
                    package_data['created_at'] = datetime.datetime.now(pytz.UTC).isoformat()
            
            # Dodaj pakiet do Supabase
            try:
                supabase.table('credit_packages').insert(package_data).execute()
                migrated_count += 1
            except Exception as e:
                logger.error(f"Błąd przy migracji pakietu kredytów {package_data['name']}: {e}")
        
        conn.close()
        logger.info(f"Zmigrowano {migrated_count} pakietów kredytów")
        return migrated_count
    except Exception as e:
        logger.error(f"Błąd podczas migracji pakietów kredytów: {e}")
        if 'conn' in locals():
            conn.close()
        return 0

def migrate_conversations():
    """Migruje konwersacje z SQLite do Supabase"""
    try:
        # Połączenie z bazą SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pobierz wszystkie konwersacje
        cursor.execute("SELECT * FROM conversations")
        conversations = cursor.fetchall()
        
        # Pobierz nazwy kolumn
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrated_count = 0
        for conversation in conversations:
            # Utwórz słownik z danymi konwersacji
            conversation_data = {columns[i]: conversation[i] for i in range(len(columns))}
            
            # Usuń pole id, aby Supabase mógł wygenerować własne
            old_id = conversation_data['id']
            del conversation_data['id']
            
            # Upewnij się, że mamy właściwy format daty
            for date_field in ['created_at', 'last_message_at']:
                if date_field in conversation_data and conversation_data[date_field]:
                    try:
                        dt = datetime.datetime.fromisoformat(conversation_data[date_field].replace('Z', '+00:00'))
                        conversation_data[date_field] = dt.isoformat()
                    except:
                        conversation_data[date_field] = datetime.datetime.now(pytz.UTC).isoformat()
            
            # Dodaj konwersację do Supabase
            try:
                response = supabase.table('conversations').insert(conversation_data).execute()
                
                if response.data:
                    new_id = response.data[0]['id']
                    
                    # Teraz migrujemy wiadomości dla tej konwersacji
                    migrate_messages_for_conversation(old_id, new_id)
                
                migrated_count += 1
            except Exception as e:
                logger.error(f"Błąd przy migracji konwersacji {old_id}: {e}")
        
        conn.close()
        logger.info(f"Zmigrowano {migrated_count} konwersacji")
        return migrated_count
    except Exception as e:
        logger.error(f"Błąd podczas migracji konwersacji: {e}")
        if 'conn' in locals():
            conn.close()
        return 0

def migrate_messages_for_conversation(old_conversation_id, new_conversation_id):
    """Migruje wiadomości dla określonej konwersacji"""
    try:
        # Połączenie z bazą SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pobierz wiadomości dla konwersacji
        cursor.execute("SELECT * FROM messages WHERE conversation_id = ?", (old_conversation_id,))
        messages = cursor.fetchall()
        
        # Pobierz nazwy kolumn
        cursor.execute("PRAGMA table_info(messages)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrated_count = 0
        for message in messages:
            # Utwórz słownik z danymi wiadomości
            message_data = {columns[i]: message[i] for i in range(len(columns))}
            
            # Usuń pole id, aby Supabase mógł wygenerować własne
            del message_data['id']
            
            # Zaktualizuj ID konwersacji
            message_data['conversation_id'] = new_conversation_id
            
            # Przekształć wartości logiczne
            if 'is_from_user' in message_data:
                message_data['is_from_user'] = bool(message_data['is_from_user'])
            
            # Upewnij się, że mamy właściwy format daty
            if 'created_at' in message_data and message_data['created_at']:
                try:
                    dt = datetime.datetime.fromisoformat(message_data['created_at'].replace('Z', '+00:00'))
                    message_data['created_at'] = dt.isoformat()
                except:
                    message_data['created_at'] = datetime.datetime.now(pytz.UTC).isoformat()
            
            # Dodaj wiadomość do Supabase
            try:
                supabase.table('messages').insert(message_data).execute()
                migrated_count += 1
            except Exception as e:
                logger.error(f"Błąd przy migracji wiadomości dla konwersacji {old_conversation_id}: {e}")
        
        conn.close()
        logger.info(f"Zmigrowano {migrated_count} wiadomości dla konwersacji {old_conversation_id}")
        return migrated_count
    except Exception as e:
        logger.error(f"Błąd podczas migracji wiadomości dla konwersacji {old_conversation_id}: {e}")
        if 'conn' in locals():
            conn.close()
        return 0

def migrate_conversation_themes():
    """Migruje tematy konwersacji z SQLite do Supabase"""
    try:
        # Połączenie z bazą SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pobierz wszystkie tematy
        cursor.execute("SELECT * FROM conversation_themes")
        themes = cursor.fetchall()
        
        # Pobierz nazwy kolumn
        cursor.execute("PRAGMA table_info(conversation_themes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrated_count = 0
        for theme in themes:
            # Utwórz słownik z danymi tematu
            theme_data = {columns[i]: theme[i] for i in range(len(columns))}
            
            # Usuń pole id, aby Supabase mógł wygenerować własne
            del theme_data['id']
            
            # Przekształć wartości logiczne
            if 'is_active' in theme_data:
                theme_data['is_active'] = bool(theme_data['is_active'])
            
            # Upewnij się, że mamy właściwy format daty
            for date_field in ['created_at', 'last_used_at']:
                if date_field in theme_data and theme_data[date_field]:
                    try:
                        dt = datetime.datetime.fromisoformat(theme_data[date_field].replace('Z', '+00:00'))
                        theme_data[date_field] = dt.isoformat()
                    except:
                        theme_data[date_field] = datetime.datetime.now(pytz.UTC).isoformat()
            
            # Dodaj temat do Supabase
            try:
                supabase.table('conversation_themes').insert(theme_data).execute()
                migrated_count += 1
            except Exception as e:
                logger.error(f"Błąd przy migracji tematu konwersacji {theme_data['theme_name']}: {e}")
        
        conn.close()
        logger.info(f"Zmigrowano {migrated_count} tematów konwersacji")
        return migrated_count
    except Exception as e:
        logger.error(f"Błąd podczas migracji tematów konwersacji: {e}")
        if 'conn' in locals():
            conn.close()
        return 0

def migrate_prompt_templates():
    """Migruje szablony promptów z SQLite do Supabase"""
    try:
        # Połączenie z bazą SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pobierz wszystkie szablony
        cursor.execute("SELECT * FROM prompt_templates")
        templates = cursor.fetchall()
        
        # Pobierz nazwy kolumn
        cursor.execute("PRAGMA table_info(prompt_templates)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrated_count = 0
        for template in templates:
            # Utwórz słownik z danymi szablonu
            template_data = {columns[i]: template[i] for i in range(len(columns))}
            
            # Usuń pole id, aby Supabase mógł wygenerować własne
            del template_data['id']
            
            # Przekształć wartości logiczne
            if 'is_active' in template_data:
                template_data['is_active'] = bool(template_data['is_active'])
            
            # Upewnij się, że mamy właściwy format daty
            if 'created_at' in template_data and template_data['created_at']:
                try:
                    dt = datetime.datetime.fromisoformat(template_data['created_at'].replace('Z', '+00:00'))
                    template_data['created_at'] = dt.isoformat()
                except:
                    template_data['created_at'] = datetime.datetime.now(pytz.UTC).isoformat()
            
            # Dodaj szablon do Supabase
            try:
                supabase.table('prompt_templates').insert(template_data).execute()
                migrated_count += 1
            except Exception as e:
                logger.error(f"Błąd przy migracji szablonu prompta {template_data['name']}: {e}")
        
        conn.close()
        logger.info(f"Zmigrowano {migrated_count} szablonów promptów")
        return migrated_count
    except Exception as e:
        logger.error(f"Błąd podczas migracji szablonów promptów: {e}")
        if 'conn' in locals():
            conn.close()
        return 0

def migrate_licenses():
    """Migruje licencje z SQLite do Supabase"""
    try:
        # Połączenie z bazą SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pobierz wszystkie licencje
        cursor.execute("SELECT * FROM licenses")
        licenses = cursor.fetchall()
        
        # Pobierz nazwy kolumn
        cursor.execute("PRAGMA table_info(licenses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrated_count = 0
        for license in licenses:
            # Utwórz słownik z danymi licencji
            license_data = {columns[i]: license[i] for i in range(len(columns))}
            
            # Usuń pole id, aby Supabase mógł wygenerować własne
            del license_data['id']
            
            # Przekształć wartości logiczne
            if 'is_used' in license_data:
                license_data['is_used'] = bool(license_data['is_used'])
            
            # Upewnij się, że mamy właściwy format daty
            for date_field in ['created_at', 'used_at']:
                if date_field in license_data and license_data[date_field]:
                    try:
                        dt = datetime.datetime.fromisoformat(license_data[date_field].replace('Z', '+00:00'))
                        license_data[date_field] = dt.isoformat()
                    except:
                        if date_field == 'created_at':
                            license_data[date_field] = datetime.datetime.now(pytz.UTC).isoformat()
                        else:
                            license_data[date_field] = None
            
            # Dodaj licencję do Supabase
            try:
                supabase.table('licenses').insert(license_data).execute()
                migrated_count += 1
            except Exception as e:
                logger.error(f"Błąd przy migracji licencji {license_data['license_key']}: {e}")
        
        conn.close()
        logger.info(f"Zmigrowano {migrated_count} licencji")
        return migrated_count
    except Exception as e:
        logger.error(f"Błąd podczas migracji licencji: {e}")
        if 'conn' in locals():
            conn.close()
        return 0

def run_migration():
    """Uruchamia pełną migrację danych z SQLite do Supabase"""
    if not supabase:
        logger.error("Nie można przeprowadzić migracji - brak połączenia z Supabase")
        return False
    
    logger.info("Rozpoczynam migrację danych z SQLite do Supabase...")
    
    # Sprawdź, czy plik bazy SQLite istnieje
    if not os.path.exists(DB_PATH):
        logger.error(f"Plik bazy danych SQLite ({DB_PATH}) nie istnieje")
        return False
    
    # Sprawdź zawartość bazy SQLite
    check_sqlite_database()
    
    # Migracja danych (w odpowiedniej kolejności)
    users_count = migrate_users()
    
    if users_count == 0:
        logger.error("Migracja użytkowników nie powiodła się. Przerywam migrację, ponieważ inne tabele zależą od użytkowników.")
        return False
    
    # Reszta migracji...
    logger.info("Migracja użytkowników zakończona. Kontynuowanie migracji innych danych...")
    
    credits_count = migrate_user_credits()
    transactions_count = migrate_credit_transactions()
    packages_count = migrate_credit_packages()
    templates_count = migrate_prompt_templates()
    themes_count = migrate_conversation_themes()
    conversations_count = migrate_conversations()
    licenses_count = migrate_licenses()
    
    logger.info("Migracja zakończona!")
    logger.info(f"Zmigrowano: {users_count} użytkowników, {credits_count} rekordów kredytów, "
                f"{transactions_count} transakcji, {packages_count} pakietów, "
                f"{templates_count} szablonów promptów, {themes_count} tematów, "
                f"{conversations_count} konwersacji, {licenses_count} licencji")
    
    return True

if __name__ == "__main__":
    logger.info("Uruchamiam skrypt migracji do Supabase")
    success = run_migration()
    if success:
        logger.info("Migracja zakończona sukcesem!")
    else:
        logger.error("Migracja zakończona niepowodzeniem!")