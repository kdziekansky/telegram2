# translations.py
# Moduł obsługujący tłumaczenia dla bota Telegram

# Słownik z tłumaczeniami dla każdego obsługiwanego języka
translations = {
    "pl": {
        # Ogólne błędy
        "error": "Wystąpił błąd",
        "restart_error": "Wystąpił błąd podczas restartu bota. Spróbuj ponownie później.",
        "initialization_error": "Wystąpił błąd podczas inicjalizacji bota. Spróbuj ponownie później.",
        "database_error": "Wystąpił błąd bazy danych. Spróbuj ponownie później.",
        "conversation_error": "Wystąpił błąd przy pobieraniu konwersacji. Spróbuj /newchat aby utworzyć nową.",
        "response_error": "Wystąpił błąd podczas generowania odpowiedzi: {error}",
        
        # Teksty do start i restart
        "language_selection_neutral": "🌐 Wybierz język / Choose language / Выберите язык:",
        "welcome_message": "Co może robić ten bot?\n❤️ ChatGPT, GPT-4o, DALLE-3 i więcej dla Ciebie\n\nWpisz /onboarding aby poznać wszystkie funkcje\n\nWsparcie: @mypremiumsupport_bot",
        "restart_suggestion": "Aby zastosować nowy język do wszystkich elementów bota, użyj przycisku poniżej.",
        "restart_button": "🔄 Zrestartuj bota",
        "restarting_bot": "Restartuję bota z nowym językiem...",
        "language_restart_complete": "✅ Bot został zrestartowany! Wszystkie elementy interfejsu są teraz w języku: *{language_display}*",
        
        # Status konta
        "your_account": "twojego konta w {bot_name}",
        "available_credits": "Dostępne kredyty",
        "operation_costs": "Koszty operacji",
        "standard_message": "Standardowa wiadomość",
        "premium_message": "Wiadomość Premium",
        "expert_message": "Wiadomość Ekspercka",
        "dalle_image": "Obraz DALL-E",
        "document_analysis": "Analiza dokumentu",
        "photo_analysis": "Analiza zdjęcia",
        "credit": "kredyt",
        "credits_per_message": "kredyt(ów) za wiadomość",
        "messages_info": "Informacje o wiadomościach",
        "messages_used": "Wykorzystane wiadomości",
        "messages_limit": "Limit wiadomości",
        "messages_left": "Pozostałe wiadomości",
        "buy_more_credits": "Aby dokupić więcej kredytów, użyj komendy",
        "no_mode": "brak",
        
        # Do funkcji credits
        "user_credits": "Twoje kredyty",
        "credit_packages": "Pakiety kredytów",
        "buy_package": "Kup pakiet",
        "purchase_success": "Zakup zakończony pomyślnie!",
        "purchase_error": "Wystąpił błąd podczas zakupu.",
        "credits": "kredyty",
        "credits_status": "Twój aktualny stan kredytów: *{credits}* kredytów",
        "credits_info": "💰 *Twoje kredyty w {bot_name}* 💰\n\nAktualny stan: *{credits}* kredytów\n\nKoszt operacji:\n• Standardowa wiadomość (GPT-3.5): 1 kredyt\n• Wiadomość Premium (GPT-4o): 3 kredyty\n• Wiadomość Ekspercka (GPT-4): 5 kredytów\n• Obraz DALL-E: 10-15 kredytów\n• Analiza dokumentu: 5 kredytów\n• Analiza zdjęcia: 8 kredytów\n\nUżyj komendy /buy aby kupić więcej kredytów.",
        "buy_credits": "🛒 *Kup kredyty* 🛒\n\nWybierz pakiet kredytów:\n\n{packages}\n\nAby kupić, użyj komendy:\n/buy [numer_pakietu]\n\nNa przykład, aby kupić pakiet Standard:\n/buy 2",
        "credit_purchase_success": "✅ *Zakup zakończony pomyślnie!*\n\nKupiłeś pakiet *{package_name}*\nDodano *{credits}* kredytów do Twojego konta\nKoszt: *{price} zł*\n\nObecny stan kredytów: *{total_credits}*\n\nDziękujemy za zakup! 🎉",
        
        # Do funkcji image
        "image_description": "Opis obrazu",
        "generating_image": "Generuję obraz, proszę czekać...",
        "image_generation_error": "Wystąpił błąd podczas generowania obrazu. Spróbuj ponownie z innym opisem.",
        "image_usage": "Użycie: /image [opis obrazu]",
        "generated_image": "Wygenerowany obraz:",
        "cost": "Koszt",
        
        # Do funkcji file i photo
        "file_too_large": "Plik jest zbyt duży. Maksymalny rozmiar to 25MB.",
        "analyzing_file": "Analizuję plik, proszę czekać...",
        "analyzing_photo": "Analizuję zdjęcie, proszę czekać...",
        "file_analysis": "Analiza pliku",
        "photo_analysis": "Analiza zdjęcia",
        
        # Do funkcji menu i nawigacja
        "menu": "Menu",
        "back": "Powrót",
        "status": "Status",
        "current_mode": "Aktualny tryb",
        "current_model": "Model",
        "current_language": "Język",
        "select_option": "Wybierz opcję z menu poniżej:",
        "menu_credits": "Kredyty",
        "image_generate": "Generuj obraz",
        "menu_chat_mode": "🔄 Wybierz tryb czatu",
        "menu_dialog_history": "📂 Historia rozmów",
        "menu_get_tokens": "👥 Darmowe tokeny",
        "menu_balance": "💰 Saldo (Kredyty)",
        "menu_settings": "⚙️ Ustawienia",
        "menu_help": "❓ Pomoc",
        "main_menu": "📋 *Menu główne*\n\nWybierz opcję z listy lub wprowadź wiadomość, aby porozmawiać z botem.",
        
        # Do ustawień i personalizacji
        "check_balance": "Stan konta",
        "buy_credits_btn": "Kup kredyty",
        "credit_stats": "Statystyki",
        "promo_code": "Kod promocyjny",
        "view_history": "Zobacz historię",
        "new_chat": "Nowa rozmowa",
        "export_conversation": "Eksportuj rozmowę",
        "delete_history": "Usuń historię",
        "select_chat_mode": "Wybierz tryb czatu:",
        "current_credits": "Aktualny stan kredytów",
        "credit_options": "Wybierz opcję:",
        "history_options": "Wybierz opcję dla historii rozmów:",
        "settings_options": "Wybierz opcję:",
        "select_model": "Wybierz model AI:",
        "select_language": "Wybierz język:",
        "select_package": "Wybierz pakiet kredytów:",
        "model_selected_short": "Model został zmieniony",
        "language_selected_short": "Język został zmieniony",
        "purchase_complete": "Zakup zakończony pomyślnie!",
        "purchase_error_short": "Błąd zakupu",
        "refresh": "Odśwież",
        "settings_title": "*Ustawienia*\n\nWybierz co chcesz zmienić:",
        "settings_model": "🤖 Model AI",
        "settings_language": "🌐 Język",
        "settings_name": "👤 Twoja nazwa",
        "settings_choose_model": "Wybierz model AI, którego chcesz używać:",
        "settings_choose_language": "*Wybór języka*\n\nWybierz język interfejsu:",
        "settings_change_name": "*Zmiana nazwy*\n\nWpisz komendę /setname [twoja_nazwa] aby zmienić swoją nazwę w bocie.",
        
        # Do rozpoczynania i zarządzania czatem
        "new_chat_created": "Utworzono nową rozmowę",
        "new_chat_success": "✅ Utworzono nową rozmowę. Możesz teraz zadać pytanie.",
        "new_chat_error": "Wystąpił błąd podczas tworzenia nowej rozmowy.",
        "yes": "Tak",
        "no": "Nie",
        "history_delete_confirm": "Czy na pewno chcesz usunąć historię rozmów?",
        "mode_selected": "Tryb został zmieniony",
        "mode_changed": "Zmieniono tryb na",
        "per_message": "za wiadomość",
        "switched_to_mode": "Przełączono na tryb",
        "ask_coding_question": "Możesz teraz zadać pytanie związane z programowaniem.",
        "name_changed": "Twoja nazwa została zmieniona na",
        "contextual_options": "Opcje kontekstowe:",
        "generate_image": "Wygeneruj obraz",
        "switch_to_code_mode": "Przełącz na tryb programisty",
        "detailed_explanation": "Szczegółowe wyjaśnienie",
        "translate": "Przetłumacz",
        "dont_show": "Nie pokazuj",
        "menu_hidden": "Menu zostało ukryte",
        "detailed_explanation_requested": "Poproszono o szczegółowe wyjaśnienie",
        "translation_requested": "Poproszono o tłumaczenie",
        "history_title": "*Historia rozmów*",
        "history_user": "Ty",
        "history_bot": "Bot",
        "history_no_conversation": "Nie masz żadnej aktywnej rozmowy.",
        "history_empty": "Historia rozmów jest pusta.",
        "history_delete_button": "🗑️ Usuń historię",
        "history_deleted": "*Historia została wyczyszczona*\n\nRozpocznęto nową konwersację.",
        "generating_response": "⏳ Generowanie odpowiedzi...",
        
        # Do modeli i trybów
        "model_not_available": "Wybrany model nie jest dostępny.",
        "model_selected": "Wybrany model: *{model}*\nKoszt: *{credits}* kredyt(ów) za wiadomość\n\nMożesz teraz zadać pytanie.",
        "language_selected": "Język został zmieniony na: *{language_display}*",
        "choose_language": "Wybierz język interfejsu:",
        
        # Do kodów aktywacyjnych
        "activation_code_usage": "Użycie: /code [kod_aktywacyjny]\n\nNa przykład: /code ABC123",
        "activation_code_invalid": "❌ *Błąd!* ❌\n\nPodany kod aktywacyjny jest nieprawidłowy lub został już wykorzystany.",
        "activation_code_success": "✅ *Kod Aktywowany!* ✅\n\nKod *{code}* został pomyślnie aktywowany.\nDodano *{credits}* kredytów do Twojego konta.\n\nAktualny stan kredytów: *{total}*",
        
        # Do programu referencyjnego
        "referral_title": "👥 *Program Referencyjny* 👥",
        "referral_description": "Zapraszaj znajomych i zdobywaj darmowe kredyty! Za każdego zaproszonego użytkownika otrzymasz *{credits}* kredytów.",
        "referral_your_code": "Twój kod referencyjny:",
        "referral_your_link": "Twój link referencyjny:",
        "referral_invited": "Zaproszeni użytkownicy:",
        "referral_users": "osób",
        "referral_earned": "Zdobyte kredyty:",
        "referral_credits": "kredytów",
        "referral_how_to_use": "Jak to działa:",
        "referral_step1": "Udostępnij swój kod lub link znajomym",
        "referral_step2": "Znajomy używa Twojego kodu podczas rozpoczynania czatu z botem",
        "referral_step3": "Otrzymujesz *{credits}* kredytów, a Twój znajomy otrzymuje bonus 25 kredytów",
        "referral_recent_users": "Ostatnio zaproszeni użytkownicy:",
        "referral_share_button": "📢 Udostępnij swój kod",
        "referral_success": "🎉 *Sukces!* 🎉\n\nUżyłeś kodu referencyjnego. Na Twoje konto zostało dodane *{credits}* kredytów bonusowych.",
        
        # Do informacji i pomocy
        "subscription_expired": "Nie masz wystarczającej liczby kredytów, aby wykonać tę operację. \n\nKup kredyty za pomocą komendy /buy lub sprawdź swoje saldo za pomocą komendy /credits.",
        "help_text": "*Pomoc i informacje*\n\n*Dostępne komendy:*\n/start - Rozpocznij korzystanie z bota\n/credits - Sprawdź saldo kredytów i kup więcej\n/buy - Kup pakiet kredytów\n/status - Sprawdź stan konta\n/newchat - Rozpocznij nową konwersację\n/mode - Wybierz tryb czatu\n/image [opis] - Wygeneruj obraz\n/restart - Odśwież informacje o bocie\n/menu - Pokaż to menu\n/code [kod] - Aktywuj kod promocyjny\n\n*Używanie bota:*\n1. Po prostu wpisz wiadomość, aby otrzymać odpowiedź\n2. Użyj przycisków menu, aby uzyskać dostęp do funkcji\n3. Możesz przesyłać zdjęcia i dokumenty do analizy\n\n*Wsparcie:*\nJeśli potrzebujesz pomocy, skontaktuj się z nami: @twoj_kontakt_wsparcia",
        "low_credits_warning": "Uwaga:",
        "low_credits_message": "Pozostało Ci tylko *{credits}* kredytów. Kup więcej za pomocą komendy /buy.",
        
        # Komunikaty onboardingu
        "onboarding_welcome": "Witaj w przewodniku po funkcjach bota {bot_name}! 🚀\n\nW tym przewodniku poznasz wszystkie możliwości, które oferuje nasz bot. Każda wiadomość wprowadzi Cię w inną funkcjonalność.\n\nGotowy, by rozpocząć?",
        "onboarding_chat": "💬 **Czat z AI**\n\nMożesz prowadzić rozmowy z różnymi modelami AI:\n• GPT-3.5 Turbo (szybki i ekonomiczny)\n• GPT-4o (inteligentny i wszechstronny)\n• GPT-4 (zaawansowany ekspert)\n\nPo prostu wyślij wiadomość, a bot odpowie!\n\n**Dostępne komendy:**\n/models - Wybierz model AI\n/newchat - Rozpocznij nową rozmowę",
        "onboarding_modes": "🔄 **Tryby czatu**\n\nBot może działać w różnych trybach, dostosowanych do Twoich potrzeb:\n• Asystent - pomoc ogólna\n• Programista - pomoc z kodem\n• Kreatywny pisarz - tworzenie treści\ni wiele innych!\n\n**Dostępne komendy:**\n/mode - Wybierz tryb czatu",
        "onboarding_images": "🖼️ **Generowanie obrazów**\n\nMożesz tworzyć unikalne obrazy na podstawie Twoich opisów za pomocą modelu DALL-E 3.\n\n**Dostępne komendy:**\n/image [opis] - Wygeneruj obraz na podstawie opisu",
        "onboarding_analysis": "🔍 **Analiza dokumentów i zdjęć**\n\nBot może analizować przesłane przez Ciebie dokumenty i zdjęcia.\n\nWystarczy przesłać plik lub zdjęcie, a bot dokona ich analizy. Obsługiwane są różne formaty plików.",
        "onboarding_credits": "💰 **System kredytów**\n\nKorzystanie z bota wymaga kredytów. Różne operacje kosztują różną liczbę kredytów:\n• Standardowa wiadomość: 1 kredyt\n• Premium wiadomość: 3 kredyty\n• Ekspercka wiadomość: 5 kredytów\n• Obraz DALL-E: 10-15 kredytów\n\n**Dostępne komendy:**\n/credits - Sprawdź stan kredytów\n/buy - Kup pakiet kredytów\n/creditstats - Analiza wykorzystania kredytów\n/code - Aktywuj kod promocyjny",
        "onboarding_export": "📤 **Eksport rozmów**\n\nMożesz wyeksportować historię Twoich rozmów do pliku PDF.\n\n**Dostępne komendy:**\n/export - Eksportuj bieżącą rozmowę do PDF",
        "onboarding_themes": "📑 **Tematy konwersacji**\n\nOrganizuj swoje rozmowy w tematyczne wątki. Każdy temat tworzy osobną konwersację.\n\n**Dostępne komendy:**\n/theme - Zarządzaj tematami\n/theme [nazwa] - Utwórz nowy temat\n/notheme - Przełącz na rozmowę bez tematu",
        "onboarding_reminders": "⏰ **Przypomnienia**\n\nBot może ustawić dla Ciebie przypomnienia o określonych porach.\n\n**Dostępne komendy:**\n/remind [czas] [treść] - Ustaw przypomnienie\n/reminders - Pokaż listę przypomnień",
        "onboarding_notes": "📝 **Notatki**\n\nZapisuj ważne informacje jako notatki i łatwo je odnajduj.\n\n**Dostępne komendy:**\n/note [tytuł] [treść] - Utwórz notatkę\n/notes - Pokaż listę notatek",
        "onboarding_settings": "⚙️ **Ustawienia i personalizacja**\n\nDostosuj bota do swoich preferencji.\n\n**Dostępne komendy:**\n/menu - Otwórz menu główne\n/language - Zmień język\n/setname - Ustaw swoją nazwę\n/restart - Zrestartuj bota",
        "onboarding_finish": "🎉 **Gratulacje!**\n\nZakończyłeś przewodnik po funkcjach bota {bot_name}. Teraz znasz już wszystkie możliwości, które oferuje nasz bot!\n\nJeśli masz jakiekolwiek pytania, użyj komendy /menu, aby otworzyć menu główne lub po prostu zapytaj bota.\n\nMiłego korzystania! 🚀",
        "onboarding_next": "Dalej ➡️",
        "onboarding_back": "⬅️ Wstecz",
        "onboarding_finish_button": "🏁 Zakończ przewodnik"
    },
    
    "en": {
        # Ogólne błędy
        "error": "An error occurred",
        "restart_error": "An error occurred while restarting the bot. Please try again later.",
        "initialization_error": "An error occurred during bot initialization. Please try again later.",
        "database_error": "A database error occurred. Please try again later.",
        "conversation_error": "An error occurred while retrieving the conversation. Try /newchat to create a new one.",
        "response_error": "An error occurred while generating the response: {error}",
        
        # Teksty do start i restart
        "language_selection_neutral": "🌐 Choose language / Wybierz język / Выберите язык:",
        "welcome_message": "What can this bot do?\n❤️ ChatGPT, GPT-4o, DALLE-3 and more for you\n\nType /onboarding to learn all features\n\nSupport: @mypremiumsupport_bot",
        "restart_suggestion": "To apply the new language to all bot elements, use the button below.",
        "restart_button": "🔄 Restart bot",
        "restarting_bot": "Restarting the bot with new language...",
        "language_restart_complete": "✅ Bot has been restarted! All interface elements are now in: *{language_display}*",
    
        # Status konta
        "your_account": "your account in {bot_name}",
        "available_credits": "Available credits",
        "operation_costs": "Operation costs",
        "standard_message": "Standard message",
        "premium_message": "Premium message",
        "expert_message": "Expert message",
        "dalle_image": "DALL-E image",
        "document_analysis": "Document analysis",
        "photo_analysis": "Photo analysis",
        "credit": "credit",
        "credits_per_message": "credit(s) per message",
        "messages_info": "Messages information",
        "messages_used": "Used messages",
        "messages_limit": "Messages limit",
        "messages_left": "Messages left",
        "buy_more_credits": "To buy more credits, use the command",
        "no_mode": "none",
        
        # Do funkcji credits
        "user_credits": "Your credits",
        "credit_packages": "Credit packages",
        "buy_package": "Buy package",
        "purchase_success": "Purchase completed successfully!",
        "purchase_error": "An error occurred during the purchase.",
        "credits": "credits",
        "credits_status": "Your current credit balance: *{credits}* credits",
        "credits_info": "💰 *Your credits in {bot_name}* 💰\n\nCurrent balance: *{credits}* credits\n\nOperation costs:\n• Standard message (GPT-3.5): 1 credit\n• Premium message (GPT-4o): 3 credits\n• Expert message (GPT-4): 5 credits\n• DALL-E image: 10-15 credits\n• Document analysis: 5 credits\n• Photo analysis: 8 credits\n\nUse the /buy command to buy more credits.",
        "buy_credits": "🛒 *Buy credits* 🛒\n\nSelect a credit package:\n\n{packages}\n\nTo buy, use the command:\n/buy [package_number]\n\nFor example, to buy the Standard package:\n/buy 2",
        "credit_purchase_success": "✅ *Purchase completed successfully!*\n\nYou bought the *{package_name}* package\nAdded *{credits}* credits to your account\nCost: *{price} PLN*\n\nCurrent credit balance: *{total_credits}*\n\nThank you for your purchase! 🎉",
        
        # Do funkcji image
        "image_description": "Image description",
        "generating_image": "Generating image, please wait...",
        "image_generation_error": "An error occurred while generating the image. Please try again with a different description.",
        "image_usage": "Usage: /image [image description]",
        "generated_image": "Generated image:",
        "cost": "Cost",
        
        # Do funkcji file i photo
        "file_too_large": "The file is too large. Maximum size is 25MB.",
        "analyzing_file": "Analyzing file, please wait...",
        "analyzing_photo": "Analyzing photo, please wait...",
        "file_analysis": "File analysis",
        "photo_analysis": "Photo analysis",
        
        # Do funkcji menu i nawigacja
        "menu": "Menu",
        "back": "Back",
        "status": "Status",
        "current_mode": "Current mode",
        "current_model": "Model",
        "current_language": "Language",
        "select_option": "Select an option from the menu below:",
        "menu_credits": "Credits",
        "image_generate": "Generate image",
        "menu_chat_mode": "🔄 Select Chat Mode",
        "menu_dialog_history": "📂 Conversation History",
        "menu_get_tokens": "👥 Free Tokens",
        "menu_balance": "💰 Balance (Credits)",
        "menu_settings": "⚙️ Settings",
        "menu_help": "❓ Help",
        "main_menu": "📋 *Main Menu*\n\nSelect an option from the list or enter a message to chat with the bot.",
        
        # Do ustawień i personalizacji
        "check_balance": "Check balance",
        "buy_credits_btn": "Buy credits",
        "credit_stats": "Statistics",
        "promo_code": "Promo code",
        "view_history": "View history",
        "new_chat": "New chat",
        "export_conversation": "Export conversation",
        "delete_history": "Delete history",
        "select_chat_mode": "Select chat mode:",
        "current_credits": "Current credits",
        "credit_options": "Select an option:",
        "history_options": "Select a history option:",
        "settings_options": "Select an option:",
        "select_model": "Select AI model:",
        "select_language": "Select language:",
        "select_package": "Select credit package:",
        "model_selected_short": "Model has been changed",
        "language_selected_short": "Language has been changed",
        "purchase_complete": "Purchase completed successfully!",
        "purchase_error_short": "Purchase error",
        "refresh": "Refresh",
        "settings_title": "*Settings*\n\nChoose what you want to change:",
        "settings_model": "🤖 AI Model",
        "settings_language": "🌐 Language",
        "settings_name": "👤 Your Name",
        "settings_choose_model": "Choose the AI model you want to use:",
        "settings_choose_language": "*Language Selection*\n\nSelect interface language:",
        "settings_change_name": "*Change Name*\n\nType the command /setname [your_name] to change your name in the bot.",
        
        # Do rozpoczynania i zarządzania czatem
        "new_chat_created": "New chat created",
        "new_chat_success": "✅ New chat created. You can now ask a question.",
        "new_chat_error": "An error occurred while creating a new chat.",
        "yes": "Yes",
        "no": "No",
        "history_delete_confirm": "Are you sure you want to delete the chat history?",
        "mode_selected": "Mode has been changed",
        "mode_changed": "Mode changed to",
        "per_message": "per message",
        "switched_to_mode": "Switched to mode",
        "ask_coding_question": "You can now ask a programming-related question.",
        "name_changed": "Your name has been changed to",
        "contextual_options": "Contextual options:",
        "generate_image": "Generate image",
        "switch_to_code_mode": "Switch to developer mode",
        "detailed_explanation": "Detailed explanation",
        "translate": "Translate",
        "dont_show": "Don't show",
        "menu_hidden": "Menu has been hidden",
        "detailed_explanation_requested": "Detailed explanation requested",
        "translation_requested": "Translation requested",
        "history_title": "*Conversation History*",
        "history_user": "You",
        "history_bot": "Bot",
        "history_no_conversation": "You don't have any active conversations.",
        "history_empty": "Conversation history is empty.",
        "history_delete_button": "🗑️ Delete History",
        "history_deleted": "*History has been cleared*\n\nA new conversation has been started.",
        "generating_response": "⏳ Generating response...",
        
        # Do modeli i trybów
        "model_not_available": "The selected model is not available.",
        "model_selected": "Selected model: *{model}*\nCost: *{credits}* credit(s) per message\n\nYou can now ask a question.",
        "language_selected": "Language has been changed to: *{language_display}*",
        "choose_language": "Choose interface language:",
        
        # Do kodów aktywacyjnych
        "activation_code_usage": "Usage: /code [activation_code]\n\nFor example: /code ABC123",
        "activation_code_invalid": "❌ *Error!* ❌\n\nThe provided activation code is invalid or has already been used.",
        "activation_code_success": "✅ *Code Activated!* ✅\n\nCode *{code}* has been successfully activated.\n*{credits}* credits have been added to your account.\n\nCurrent credit balance: *{total}*",
        
        # Do programu referencyjnego
        "referral_title": "👥 *Referral Program* 👥",
        "referral_description": "Invite friends and earn free credits! For each invited user, you'll receive *{credits}* credits.",
        "referral_your_code": "Your referral code:",
        "referral_your_link": "Your referral link:",
        "referral_invited": "Invited users:",
        "referral_users": "users",
        "referral_earned": "Credits earned:",
        "referral_credits": "credits",
        "referral_how_to_use": "How it works:",
        "referral_step1": "Share your code or link with friends",
        "referral_step2": "Your friend uses your code when starting to chat with the bot",
        "referral_step3": "You receive *{credits}* credits, and your friend gets a 25 credit bonus",
        "referral_recent_users": "Recently invited users:",
        "referral_share_button": "📢 Share your code",
        "referral_success": "🎉 *Success!* 🎉\n\nYou used a referral code. *{credits}* bonus credits have been added to your account.",
        
        # Do informacji i pomocy
        "subscription_expired": "You don't have enough credits to perform this operation. \n\nBuy credits using the /buy command or check your balance using the /credits command.",
        "help_text": "*Help and Information*\n\n*Available commands:*\n/start - Start using the bot\n/credits - Check credit balance and buy more\n/buy - Buy credit package\n/status - Check account status\n/newchat - Start a new conversation\n/mode - Choose chat mode\n/image [description] - Generate an image\n/restart - Refresh bot information\n/menu - Show this menu\n/code [code] - Activate promotional code\n\n*Using the bot:*\n1. Simply type a message to get a response\n2. Use the menu buttons to access features\n3. You can upload photos and documents for analysis\n\n*Support:*\nIf you need help, contact us: @twoj_kontakt_wsparcia",
        "low_credits_warning": "Warning:",
        "low_credits_message": "You only have *{credits}* credits left. Buy more using the /buy command.",
        
        # Komunikaty onboardingu
        "onboarding_welcome": "Welcome to the {bot_name} feature guide! 🚀\n\nIn this guide, you'll learn about all the capabilities our bot offers. Each message will introduce you to a different feature.\n\nReady to start?",
        "onboarding_chat": "💬 **Chat with AI**\n\nYou can have conversations with different AI models:\n• GPT-3.5 Turbo (fast and economical)\n• GPT-4o (intelligent and versatile)\n• GPT-4 (advanced expert)\n\nJust send a message and the bot will respond!\n\n**Available commands:**\n/models - Choose AI model\n/newchat - Start a new conversation",
        "onboarding_modes": "🔄 **Chat Modes**\n\nThe bot can operate in different modes, tailored to your needs:\n• Assistant - general help\n• Developer - code assistance\n• Creative writer - content creation\nand many more!\n\n**Available commands:**\n/mode - Choose chat mode",
        "onboarding_images": "🖼️ **Image Generation**\n\nYou can create unique images based on your descriptions using the DALL-E 3 model.\n\n**Available commands:**\n/image [description] - Generate an image based on description",
        "onboarding_analysis": "🔍 **Document and Photo Analysis**\n\nThe bot can analyze documents and photos you send.\n\nJust upload a file or photo, and the bot will analyze it. Various file formats are supported.",
        "onboarding_credits": "💰 **Credit System**\n\nUsing the bot requires credits. Different operations cost different amounts of credits:\n• Standard message: 1 credit\n• Premium message: 3 credits\n• Expert message: 5 credits\n• DALL-E image: 10-15 credits\n\n**Available commands:**\n/credits - Check credit balance\n/buy - Buy credit package\n/creditstats - Credit usage analysis\n/code - Activate promo code",
        "onboarding_export": "📤 **Conversation Export**\n\nYou can export your conversation history to a PDF file.\n\n**Available commands:**\n/export - Export current conversation to PDF",
        "onboarding_themes": "📑 **Conversation Themes**\n\nOrganize your conversations into thematic threads. Each theme creates a separate conversation.\n\n**Available commands:**\n/theme - Manage themes\n/theme [name] - Create a new theme\n/notheme - Switch to themeless conversation",
        "onboarding_reminders": "⏰ **Reminders**\n\nThe bot can set reminders for you at specific times.\n\n**Available commands:**\n/remind [time] [content] - Set a reminder\n/reminders - Show reminder list",
        "onboarding_notes": "📝 **Notes**\n\nSave important information as notes and easily find them later.\n\n**Available commands:**\n/note [title] [content] - Create a note\n/notes - Show notes list",
        "onboarding_settings": "⚙️ **Settings and Personalization**\n\nCustomize the bot to your preferences.\n\n**Available commands:**\n/menu - Open main menu\n/language - Change language\n/setname - Set your name\n/restart - Restart the bot",
        "onboarding_finish": "🎉 **Congratulations!**\n\nYou've completed the {bot_name} feature guide. Now you know all the capabilities our bot offers!\n\nIf you have any questions, use the /menu command to open the main menu or simply ask the bot.\n\nEnjoy using it! 🚀",
        "onboarding_next": "Next ➡️",
        "onboarding_back": "⬅️ Back",
        "onboarding_finish_button": "🏁 Finish guide"
    },
    
    "ru": {
        # Ogólne błędy
        "error": "Произошла ошибка",
        "restart_error": "Произошла ошибка при перезапуске бота. Пожалуйста, попробуйте позже.",
        "initialization_error": "Произошла ошибка при инициализации бота. Пожалуйста, попробуйте позже.",
        "database_error": "Произошла ошибка базы данных. Пожалуйста, попробуйте позже.",
        "conversation_error": "Произошла ошибка при получении разговора. Попробуйте /newchat, чтобы создать новый.",
        "response_error": "Произошла ошибка при создании ответа: {error}",
        
        # Teksty do start i restart
        "language_selection_neutral": "🌐 Выберите язык / Choose language / Wybierz język:",
        "welcome_message": "Что может делать этот бот?\n❤️ ChatGPT, GPT-4o, DALLE-3 и больше для вас\n\nВведите /onboarding чтобы узнать все функции\n\nПоддержка: @mypremiumsupport_bot",
        "restart_suggestion": "Чтобы применить новый язык ко всем элементам бота, используйте кнопку ниже.",
        "restart_button": "🔄 Перезапустить бота",
        "restarting_bot": "Перезапуск бота с новым языком...",
        "language_restart_complete": "✅ Бот был перезапущен! Все элементы интерфейса теперь на языке: *{language_display}*",
        
        # Status konta
        "your_account": "вашего аккаунта в {bot_name}",
        "available_credits": "Доступные кредиты",
        "operation_costs": "Стоимость операций",
        "standard_message": "Стандартное сообщение",
        "premium_message": "Премиум сообщение",
        "expert_message": "Экспертное сообщение",
        "dalle_image": "Изображение DALL-E",
        "document_analysis": "Анализ документа",
        "photo_analysis": "Анализ фото",
        "credit": "кредит",
        "credits_per_message": "кредит(ов) за сообщение",
        "messages_info": "Информация о сообщениях",
        "messages_used": "Использованные сообщения",
        "messages_limit": "Лимит сообщений",
        "messages_left": "Оставшиеся сообщения",
        "buy_more_credits": "Чтобы купить больше кредитов, используйте команду",
        "no_mode": "нет",
        
        # Do funkcji credits
        "user_credits": "Ваши кредиты",
        "credit_packages": "Пакеты кредитов",
        "buy_package": "Купить пакет",
        "purchase_success": "Покупка успешно завершена!",
        "purchase_error": "Произошла ошибка при покупке.",
        "credits": "кредитов",
        "credits_status": "Ваш текущий баланс кредитов: *{credits}* кредитов",
        "credits_info": "💰 *Ваши кредиты в {bot_name}* 💰\n\nТекущий баланс: *{credits}* кредитов\n\nСтоимость операций:\n• Стандартное сообщение (GPT-3.5): 1 кредит\n• Премиум сообщение (GPT-4o): 3 кредита\n• Экспертное сообщение (GPT-4): 5 кредитов\n• Изображение DALL-E: 10-15 кредитов\n• Анализ документа: 5 кредитов\n• Анализ фото: 8 кредитов\n\nИспользуйте команду /buy, чтобы купить больше кредитов.",
        "buy_credits": "🛒 *Купить кредиты* 🛒\n\nВыберите пакет кредитов:\n\n{packages}\n\nДля покупки используйте команду:\n/buy [номер_пакета]\n\nНапример, чтобы купить пакет Стандарт:\n/buy 2",
        "credit_purchase_success": "✅ *Покупка успешно завершена!*\n\nВы купили пакет *{package_name}*\nДобавлено *{credits}* кредитов на ваш счет\nСтоимость: *{price} PLN*\n\nТекущий баланс кредитов: *{total_credits}*\n\nСпасибо за покупку! 🎉",
        
        # Do funkcji image
        "image_description": "Описание изображения",
        "generating_image": "Генерирую изображение, пожалуйста, подождите...",
        "image_generation_error": "Произошла ошибка при создании изображения. Пожалуйста, попробуйте с другим описанием.",
        "image_usage": "Использование: /image [описание изображения]",
        "generated_image": "Сгенерированное изображение:",
        "cost": "Стоимость",
        
        # Do funkcji file i photo
        "file_too_large": "Файл слишком большой. Максимальный размер 25MB.",
        "analyzing_file": "Анализирую файл, пожалуйста, подождите...",
        "analyzing_photo": "Анализирую фото, пожалуйста, подождите...",
        "file_analysis": "Анализ файла",
        "photo_analysis": "Анализ фото",
        
        # Do funkcji menu i nawigacja
        "menu": "Меню",
        "back": "Назад",
        "status": "Статус",
        "current_mode": "Текущий режим",
        "current_model": "Модель",
        "current_language": "Язык",
        "select_option": "Выберите опцию из меню ниже:",
        "menu_credits": "Кредиты",
        "image_generate": "Создать изображение",
        "menu_chat_mode": "🔄 Выбрать режим чата",
        "menu_dialog_history": "📂 История разговоров",
        "menu_get_tokens": "👥 Бесплатные токены",
        "menu_balance": "💰 Баланс (Кредиты)",
        "menu_settings": "⚙️ Настройки",
        "menu_help": "❓ Помощь",
        "main_menu": "📋 *Главное меню*\n\nВыберите опцию из списка или введите сообщение, чтобы начать разговор с ботом.",
        
        # Do ustawień i personalizacji
        "check_balance": "Проверить баланс",
        "buy_credits_btn": "Купить кредиты",
        "credit_stats": "Статистика",
        "promo_code": "Промокод",
        "view_history": "Просмотреть историю",
        "new_chat": "Новый чат",
        "export_conversation": "Экспорт разговора",
        "delete_history": "Удалить историю",
        "select_chat_mode": "Выберите режим чата:",
        "current_credits": "Текущие кредиты",
        "credit_options": "Выберите опцию:",
        "history_options": "Выберите опцию для истории:",
        "settings_options": "Выберите опцию:",
        "select_model": "Выберите модель ИИ:",
        "select_language": "Выберите язык:",
        "select_package": "Выберите пакет кредитов:",
        "model_selected_short": "Модель изменена",
        "language_selected_short": "Язык изменен",
        "purchase_complete": "Покупка успешно завершена!",
        "purchase_error_short": "Ошибка покупки",
        "refresh": "Обновить",
        "settings_title": "*Настройки*\n\nВыберите, что вы хотите изменить:",
        "settings_model": "🤖 Модель ИИ",
        "settings_language": "🌐 Язык",
        "settings_name": "👤 Ваше имя",
        "settings_choose_model": "Выберите модель ИИ, которую вы хотите использовать:",
        "settings_choose_language": "*Выбор языка*\n\nВыберите язык интерфейса:",
        "settings_change_name": "*Изменение имени*\n\nВведите команду /setname [ваше_имя], чтобы изменить свое имя в боте.",
        
        # Do rozpoczynania i zarządzania czatem
        "new_chat_created": "Создан новый чат",
        "new_chat_success": "✅ Создан новый чат. Теперь вы можете задать вопрос.",
        "new_chat_error": "Произошла ошибка при создании нового чата.",
        "yes": "Да",
        "no": "Нет",
        "history_delete_confirm": "Вы уверены, что хотите удалить историю чата?",
        "mode_selected": "Режим изменен",
        "mode_changed": "Режим изменен на",
        "per_message": "за сообщение",
        "switched_to_mode": "Переключено на режим",
        "ask_coding_question": "Теперь вы можете задать вопрос, связанный с программированием.",
        "name_changed": "Ваше имя изменено на",
        "contextual_options": "Контекстные опции:",
        "generate_image": "Создать изображение",
        "switch_to_code_mode": "Переключиться на режим разработчика",
        "detailed_explanation": "Подробное объяснение",
        "translate": "Перевести",
        "dont_show": "Не показывать",
        "menu_hidden": "Меню скрыто",
        "detailed_explanation_requested": "Запрошено подробное объяснение",
        "translation_requested": "Запрошен перевод",
        "history_title": "*История разговоров*",
        "history_user": "Вы",
        "history_bot": "Бот",
        "history_no_conversation": "У вас нет активных разговоров.",
        "history_empty": "История разговоров пуста.",
        "history_delete_button": "🗑️ Удалить историю",
        "history_deleted": "*История была очищена*\n\nНачат новый разговор.",
        "generating_response": "⏳ Генерация ответа...",
        
        # Do modeli i trybów
        "model_not_available": "Выбранная модель недоступна.",
        "model_selected": "Выбранная модель: *{model}*\nСтоимость: *{credits}* кредит(ов) за сообщение\n\nТеперь вы можете задать вопрос.",
        "language_selected": "Язык изменен на: *{language_display}*",
        "choose_language": "Выберите язык интерфейса:",
        
        # Do kodów aktywacyjnych
        "activation_code_usage": "Использование: /code [активационный_код]\n\nНапример: /code ABC123",
        "activation_code_invalid": "❌ *Ошибка!* ❌\n\nУказанный активационный код недействителен или уже использован.",
        "activation_code_success": "✅ *Код активирован!* ✅\n\nКод *{code}* успешно активирован.\nДобавлено *{credits}* кредитов на ваш счет.\n\nТекущий баланс кредитов: *{total}*",
        
        # Do programu referencyjnego
        "referral_title": "👥 *Реферальная программа* 👥",
        "referral_description": "Приглашайте друзей и получайте бесплатные кредиты! За каждого приглашенного пользователя вы получите *{credits}* кредитов.",
        "referral_your_code": "Ваш реферальный код:",
        "referral_your_link": "Ваша реферальная ссылка:",
        "referral_invited": "Приглашенные пользователи:",
        "referral_users": "пользователей",
        "referral_earned": "Заработано кредитов:",
        "referral_credits": "кредитов",
        "referral_how_to_use": "Как это работает:",
        "referral_step1": "Поделитесь своим кодом или ссылкой с друзьями",
        "referral_step2": "Ваш друг использует ваш код при начале разговора с ботом",
        "referral_step3": "Вы получаете *{credits}* кредитов, а ваш друг получает бонус в 25 кредитов",
        "referral_recent_users": "Недавно приглашенные пользователи:",
        "referral_share_button": "📢 Поделиться вашим кодом",
        "referral_success": "🎉 *Успех!* 🎉\n\nВы использовали реферальный код. На ваш счет добавлено *{credits}* бонусных кредитов.",
        
        # Do informacji i pomocy
        "subscription_expired": "У вас недостаточно кредитов для выполнения этой операции. \n\nКупите кредиты с помощью команды /buy или проверьте свой баланс с помощью команды /credits.",
        "help_text": "*Помощь и информация*\n\n*Доступные команды:*\n/start - Начать использование бота\n/credits - Проверить баланс кредитов и купить больше\n/buy - Купить пакет кредитов\n/status - Проверить статус аккаунта\n/newchat - Начать новый разговор\n/mode - Выбрать режим чата\n/image [описание] - Сгенерировать изображение\n/restart - Обновить информацию о боте\n/menu - Показать это меню\n/code [код] - Активировать промокод\n\n*Использование бота:*\n1. Просто введите сообщение, чтобы получить ответ\n2. Используйте кнопки меню для доступа к функциям\n3. Вы можете загружать фотографии и документы для анализа\n\n*Поддержка:*\nЕсли вам нужна помощь, свяжитесь с нами: @twoj_kontakt_wsparcia",
        "low_credits_warning": "Внимание:",
        "low_credits_message": "У вас осталось только *{credits}* кредитов. Купите больше с помощью команды /buy.",
        
        # Komunikaty onboardingu
        "onboarding_welcome": "Добро пожаловать в руководство по функциям бота {bot_name}! 🚀\n\nВ этом руководстве вы узнаете обо всех возможностях, которые предлагает наш бот. Каждое сообщение познакомит вас с разными функциями.\n\nГотовы начать?",
        "onboarding_chat": "💬 **Чат с ИИ**\n\nВы можете вести беседы с разными моделями ИИ:\n• GPT-3.5 Turbo (быстрый и экономичный)\n• GPT-4o (умный и универсальный)\n• GPT-4 (продвинутый эксперт)\n\nПросто отправьте сообщение, и бот ответит!\n\n**Доступные команды:**\n/models - Выбрать модель ИИ\n/newchat - Начать новый разговор",
        "onboarding_modes": "🔄 **Режимы чата**\n\nБот может работать в разных режимах, адаптированных к вашим потребностям:\n• Ассистент - общая помощь\n• Разработчик - помощь с кодом\n• Креативный писатель - создание контента\nи многие другие!\n\n**Доступные команды:**\n/mode - Выбрать режим чата",
        "onboarding_images": "🖼️ **Генерация изображений**\n\nВы можете создавать уникальные изображения на основе ваших описаний с помощью модели DALL-E 3.\n\n**Доступные команды:**\n/image [описание] - Сгенерировать изображение на основе описания",
        "onboarding_analysis": "🔍 **Анализ документов и фотографий**\n\nБот может анализировать отправленные вами документы и фотографии.\n\nПросто загрузите файл или фото, и бот проведет их анализ. Поддерживаются различные форматы файлов.",
        "onboarding_credits": "💰 **Система кредитов**\n\nИспользование бота требует кредитов. Разные операции стоят разное количество кредитов:\n• Стандартное сообщение: 1 кредит\n• Премиум сообщение: 3 кредита\n• Экспертное сообщение: 5 кредитов\n• Изображение DALL-E: 10-15 кредитов\n\n**Доступные команды:**\n/credits - Проверить баланс кредитов\n/buy - Купить пакет кредитов\n/creditstats - Анализ использования кредитов\n/code - Активировать промокод",
        "onboarding_export": "📤 **Экспорт разговоров**\n\nВы можете экспортировать историю ваших разговоров в файл PDF.\n\n**Доступные команды:**\n/export - Экспортировать текущий разговор в PDF",
        "onboarding_themes": "📑 **Темы бесед**\n\nОрганизуйте свои разговоры в тематические ветки. Каждая тема создает отдельный разговор.\n\n**Доступные команды:**\n/theme - Управление темами\n/theme [название] - Создать новую тему\n/notheme - Переключиться на разговор без темы",
        "onboarding_reminders": "⏰ **Напоминания**\n\nБот может устанавливать для вас напоминания в определенное время.\n\n**Доступные команды:**\n/remind [время] [содержание] - Установить напоминание\n/reminders - Показать список напоминаний",
        "onboarding_notes": "📝 **Заметки**\n\nСохраняйте важную информацию в виде заметок и легко находите их позднее.\n\n**Доступные команды:**\n/note [заголовок] [содержание] - Создать заметку\n/notes - Показать список заметок",
        "onboarding_settings": "⚙️ **Настройки и персонализация**\n\nНастройте бота под свои предпочтения.\n\n**Доступные команды:**\n/menu - Открыть главное меню\n/language - Изменить язык\n/setname - Установить свое имя\n/restart - Перезапустить бота",
        "onboarding_finish": "🎉 **Поздравляем!**\n\nВы завершили руководство по функциям бота {bot_name}. Теперь вы знаете все возможности, которые предлагает наш бот!\n\nЕсли у вас есть вопросы, используйте команду /menu, чтобы открыть главное меню, или просто спросите бота.\n\nПриятного использования! 🚀",
        "onboarding_next": "Далее ➡️",
        "onboarding_back": "⬅️ Назад",
        "onboarding_finish_button": "🏁 Завершить руководство"
    }
}

def get_text(key, language="pl", **kwargs):
    """
    Pobiera przetłumaczony tekst dla określonego klucza i języka.
    
    Args:
        key (str): Klucz tekstu do przetłumaczenia
        language (str): Kod języka (pl, en, ru)
        **kwargs: Argumenty do formatowania tekstu
        
    Returns:
        str: Przetłumaczony tekst
    """
    # Domyślny język, jeśli podany język nie jest obsługiwany
    if language not in translations:
        language = "pl"
    
    # Pobierz tekst lub zwróć klucz jako fallback
    text = translations[language].get(key, kwargs.get('default', key))
    
    # Formatuj tekst z podanymi argumentami
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            # Jeśli formatowanie nie powiedzie się, zwróć nieformatowany tekst
            return text
    
    return text