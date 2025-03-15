# translations.py
# Moduł obsługujący tłumaczenia dla bota Telegram

# Słownik z tłumaczeniami dla każdego obsługiwanego języka
translations = {
    "pl": {
        "welcome_message": "Witaj w {bot_name}! 🤖✨\n\nJestem zaawansowanym botem AI, który pomoże Ci w wielu zadaniach - od odpowiadania na pytania po generowanie obrazów.\n\nDo korzystania z moich funkcji potrzebujesz kredytów. Sprawdź swoje saldo i dostępne pakiety za pomocą komendy /credits.\n\nDostępne komendy:\n/start - Pokaż tę wiadomość\n/credits - Sprawdź saldo kredytów i kup więcej\n/buy - Kup pakiet kredytów\n/status - Sprawdź stan konta\n/newchat - Rozpocznij nową konwersację\n/mode - Wybierz tryb czatu\n/image [opis] - Wygeneruj obraz (koszt: 10 kredytów)\n/restart - Odśwież informacje o bocie\n/menu - Pokaż menu główne\n/code [kod] - Aktywuj kod promocyjny",
        "subscription_expired": "Nie masz wystarczającej liczby kredytów, aby wykonać tę operację. \n\nKup kredyty za pomocą komendy /buy lub sprawdź swoje saldo za pomocą komendy /credits.",
        "credits_info": "💰 *Twoje kredyty w {bot_name}* 💰\n\nAktualny stan: *{credits}* kredytów\n\nKoszt operacji:\n• Standardowa wiadomość (GPT-3.5): 1 kredyt\n• Wiadomość Premium (GPT-4o): 3 kredyty\n• Wiadomość Ekspercka (GPT-4): 5 kredytów\n• Obraz DALL-E: 10-15 kredytów\n• Analiza dokumentu: 5 kredytów\n• Analiza zdjęcia: 8 kredytów\n\nUżyj komendy /buy aby kupić więcej kredytów.",
        "buy_credits": "🛒 *Kup kredyty* 🛒\n\nWybierz pakiet kredytów:\n\n{packages}\n\nAby kupić, użyj komendy:\n/buy [numer_pakietu]\n\nNa przykład, aby kupić pakiet Standard:\n/buy 2",
        "credit_purchase_success": "✅ *Zakup zakończony pomyślnie!*\n\nKupiłeś pakiet *{package_name}*\nDodano *{credits}* kredytów do Twojego konta\nKoszt: *{price} zł*\n\nObecny stan kredytów: *{total_credits}*\n\nDziękujemy za zakup! 🎉",
        "main_menu": "📋 *Menu główne*\n\nWybierz opcję z listy lub wprowadź wiadomość, aby porozmawiać z botem.",
        "menu_chat_mode": "🔄 Wybierz tryb czatu",
        "menu_dialog_history": "📂 Historia rozmów",
        "menu_get_tokens": "👥 Darmowe tokeny",
        "menu_balance": "💰 Saldo (Kredyty)",
        "menu_settings": "⚙️ Ustawienia",
        "menu_help": "❓ Pomoc",
        "settings_title": "*Ustawienia*\n\nWybierz co chcesz zmienić:",
        "settings_model": "🤖 Model AI",
        "settings_language": "🌐 Język",
        "settings_name": "👤 Twoja nazwa",
        "settings_choose_model": "Wybierz model AI, którego chcesz używać:",
        "settings_choose_language": "*Wybór języka*\n\nWybierz język interfejsu:",
        "settings_change_name": "*Zmiana nazwy*\n\nWpisz komendę /setname [twoja_nazwa] aby zmienić swoją nazwę w bocie.",
        "model_not_available": "Wybrany model nie jest dostępny.",
        "model_selected": "Wybrany model: *{model}*\nKoszt: *{credits}* kredyt(ów) za wiadomość\n\nMożesz teraz zadać pytanie.",
        "language_selected": "Język został zmieniony na: *{language_display}*",
        "choose_language": "Wybierz język interfejsu:",
        "history_title": "*Historia rozmów*",
        "history_user": "Ty",
        "history_bot": "Bot",
        "history_no_conversation": "Nie masz żadnej aktywnej rozmowy.",
        "history_empty": "Historia rozmów jest pusta.",
        "history_delete_button": "🗑️ Usuń historię",
        "history_deleted": "*Historia została wyczyszczona*\n\nRozpocznęto nową konwersację.",
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
        "activation_code_usage": "Użycie: /code [kod_aktywacyjny]\n\nNa przykład: /code ABC123",
        "activation_code_invalid": "❌ *Błąd!* ❌\n\nPodany kod aktywacyjny jest nieprawidłowy lub został już wykorzystany.",
        "activation_code_success": "✅ *Kod Aktywowany!* ✅\n\nKod *{code}* został pomyślnie aktywowany.\nDodano *{credits}* kredytów do Twojego konta.\n\nAktualny stan kredytów: *{total}*",
        "credits": "kredyty",
        "credits_status": "Twój aktualny stan kredytów: *{credits}* kredytów",
        "help_text": "*Pomoc i informacje*\n\n*Dostępne komendy:*\n/start - Rozpocznij korzystanie z bota\n/credits - Sprawdź saldo kredytów i kup więcej\n/buy - Kup pakiet kredytów\n/status - Sprawdź stan konta\n/newchat - Rozpocznij nową konwersację\n/mode - Wybierz tryb czatu\n/image [opis] - Wygeneruj obraz\n/restart - Odśwież informacje o bocie\n/menu - Pokaż to menu\n/code [kod] - Aktywuj kod promocyjny\n\n*Używanie bota:*\n1. Po prostu wpisz wiadomość, aby otrzymać odpowiedź\n2. Użyj przycisków menu, aby uzyskać dostęp do funkcji\n3. Możesz przesyłać zdjęcia i dokumenty do analizy\n\n*Wsparcie:*\nJeśli potrzebujesz pomocy, skontaktuj się z nami: @twoj_kontakt_wsparcia",
        "generating_response": "⏳ Generowanie odpowiedzi...",
        "analyzing_document": "Analizuję plik, proszę czekać...",
        "analyzing_photo": "Analizuję zdjęcie, proszę czekać...",
        "generating_image": "Generuję obraz, proszę czekać...",
        
        # Klucze dla obsługi języka i restartu
        "restart_suggestion": "Aby zastosować nowy język do wszystkich elementów bota, użyj przycisku poniżej.",
        "restart_button": "🔄 Zrestartuj bota",
        "restarting_bot": "Restartuję bota z nowym językiem...",
        "language_restart_complete": "✅ Bot został zrestartowany! Wszystkie elementy interfejsu są teraz w języku: *{language_display}*",
        
        # Klucze dla obrazów
        "image_usage": "Użycie: /image [opis obrazu]",
        "generated_image": "Wygenerowany obraz:",
        "cost": "Koszt",
        "image_generation_error": "Przepraszam, wystąpił błąd podczas generowania obrazu. Spróbuj ponownie z innym opisem.",
        "low_credits_warning": "Uwaga:",
        "low_credits_message": "Pozostało Ci tylko *{credits}* kredytów. Kup więcej za pomocą komendy /buy."
    },
    "en": {
        "welcome_message": "Welcome to {bot_name}! 🤖✨\n\nI'm an advanced AI bot that will help you with many tasks - from answering questions to generating images.\n\nTo use my features, you need credits. Check your balance and available packages using the /credits command.\n\nAvailable commands:\n/start - Show this message\n/credits - Check credit balance and buy more\n/buy - Buy credit package\n/status - Check account status\n/newchat - Start a new conversation\n/mode - Choose chat mode\n/image [description] - Generate an image (cost: 10 credits)\n/restart - Refresh bot information\n/menu - Show main menu\n/code [code] - Activate promotional code",
        "subscription_expired": "You don't have enough credits to perform this operation. \n\nBuy credits using the /buy command or check your balance using the /credits command.",
        "credits_info": "💰 *Your credits in {bot_name}* 💰\n\nCurrent balance: *{credits}* credits\n\nOperation costs:\n• Standard message (GPT-3.5): 1 credit\n• Premium message (GPT-4o): 3 credits\n• Expert message (GPT-4): 5 credits\n• DALL-E image: 10-15 credits\n• Document analysis: 5 credits\n• Photo analysis: 8 credits\n\nUse the /buy command to buy more credits.",
        "buy_credits": "🛒 *Buy credits* 🛒\n\nSelect a credit package:\n\n{packages}\n\nTo buy, use the command:\n/buy [package_number]\n\nFor example, to buy the Standard package:\n/buy 2",
        "credit_purchase_success": "✅ *Purchase completed successfully!*\n\nYou bought the *{package_name}* package\nAdded *{credits}* credits to your account\nCost: *{price} PLN*\n\nCurrent credit balance: *{total_credits}*\n\nThank you for your purchase! 🎉",
        "main_menu": "📋 *Main Menu*\n\nSelect an option from the list or enter a message to chat with the bot.",
        "menu_chat_mode": "🔄 Select Chat Mode",
        "menu_dialog_history": "📂 Conversation History",
        "menu_get_tokens": "👥 Free Tokens",
        "menu_balance": "💰 Balance (Credits)",
        "menu_settings": "⚙️ Settings",
        "menu_help": "❓ Help",
        "settings_title": "*Settings*\n\nChoose what you want to change:",
        "settings_model": "🤖 AI Model",
        "settings_language": "🌐 Language",
        "settings_name": "👤 Your Name",
        "settings_choose_model": "Choose the AI model you want to use:",
        "settings_choose_language": "*Language Selection*\n\nSelect interface language:",
        "settings_change_name": "*Change Name*\n\nType the command /setname [your_name] to change your name in the bot.",
        "model_not_available": "The selected model is not available.",
        "model_selected": "Selected model: *{model}*\nCost: *{credits}* credit(s) per message\n\nYou can now ask a question.",
        "language_selected": "Language has been changed to: *{language_display}*",
        "choose_language": "Choose interface language:",
        "history_title": "*Conversation History*",
        "history_user": "You",
        "history_bot": "Bot",
        "history_no_conversation": "You don't have any active conversations.",
        "history_empty": "Conversation history is empty.",
        "history_delete_button": "🗑️ Delete History",
        "history_deleted": "*History has been cleared*\n\nA new conversation has been started.",
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
        "activation_code_usage": "Usage: /code [activation_code]\n\nFor example: /code ABC123",
        "activation_code_invalid": "❌ *Error!* ❌\n\nThe provided activation code is invalid or has already been used.",
        "activation_code_success": "✅ *Code Activated!* ✅\n\nCode *{code}* has been successfully activated.\n*{credits}* credits have been added to your account.\n\nCurrent credit balance: *{total}*",
        "credits": "credits",
        "credits_status": "Your current credit balance: *{credits}* credits",
        "help_text": "*Help and Information*\n\n*Available commands:*\n/start - Start using the bot\n/credits - Check credit balance and buy more\n/buy - Buy credit package\n/status - Check account status\n/newchat - Start a new conversation\n/mode - Choose chat mode\n/image [description] - Generate an image\n/restart - Refresh bot information\n/menu - Show this menu\n/code [code] - Activate promotional code\n\n*Using the bot:*\n1. Simply type a message to get a response\n2. Use the menu buttons to access features\n3. You can upload photos and documents for analysis\n\n*Support:*\nIf you need help, contact us: @twoj_kontakt_wsparcia",
        "generating_response": "⏳ Generating response...",
        "analyzing_document": "Analyzing file, please wait...",
        "analyzing_photo": "Analyzing photo, please wait...",
        "generating_image": "Generating image, please wait...",
        
        # Klucze dla obsługi języka i restartu
        "restart_suggestion": "To apply the new language to all bot elements, use the button below.",
        "restart_button": "🔄 Restart bot",
        "restarting_bot": "Restarting the bot with new language...",
        "language_restart_complete": "✅ Bot has been restarted! All interface elements are now in: *{language_display}*",
        
        # Klucze dla obrazów
        "image_usage": "Usage: /image [image description]",
        "generated_image": "Generated image:",
        "cost": "Cost",
        "image_generation_error": "Sorry, there was an error generating the image. Please try again with a different description.",
        "low_credits_warning": "Warning:",
        "low_credits_message": "You only have *{credits}* credits left. Buy more using the /buy command."
    },
    "ru": {
        "welcome_message": "Добро пожаловать в {bot_name}! 🤖✨\n\nЯ продвинутый ИИ-бот, который поможет вам во многих задачах - от ответов на вопросы до генерации изображений.\n\nДля использования моих функций вам нужны кредиты. Проверьте свой баланс и доступные пакеты с помощью команды /credits.\n\nДоступные команды:\n/start - Показать это сообщение\n/credits - Проверить баланс кредитов и купить больше\n/buy - Купить пакет кредитов\n/status - Проверить статус аккаунта\n/newchat - Начать новый разговор\n/mode - Выбрать режим чата\n/image [описание] - Сгенерировать изображение (стоимость: 10 кредитов)\n/restart - Обновить информацию о боте\n/menu - Показать главное меню\n/code [код] - Активировать промокод",
        "subscription_expired": "У вас недостаточно кредитов для выполнения этой операции. \n\nКупите кредиты с помощью команды /buy или проверьте свой баланс с помощью команды /credits.",
        "credits_info": "💰 *Ваши кредиты в {bot_name}* 💰\n\nТекущий баланс: *{credits}* кредитов\n\nСтоимость операций:\n• Стандартное сообщение (GPT-3.5): 1 кредит\n• Премиум сообщение (GPT-4o): 3 кредита\n• Экспертное сообщение (GPT-4): 5 кредитов\n• Изображение DALL-E: 10-15 кредитов\n• Анализ документа: 5 кредитов\n• Анализ фото: 8 кредитов\n\nИспользуйте команду /buy, чтобы купить больше кредитов.",
        "buy_credits": "🛒 *Купить кредиты* 🛒\n\nВыберите пакет кредитов:\n\n{packages}\n\nДля покупки используйте команду:\n/buy [номер_пакета]\n\nНапример, чтобы купить пакет Стандарт:\n/buy 2",
        "credit_purchase_success": "✅ *Покупка успешно завершена!*\n\nВы купили пакет *{package_name}*\nДобавлено *{credits}* кредитов на ваш счет\nСтоимость: *{price} PLN*\n\nТекущий баланс кредитов: *{total_credits}*\n\nСпасибо за покупку! 🎉",
        "main_menu": "📋 *Главное меню*\n\nВыберите опцию из списка или введите сообщение, чтобы начать разговор с ботом.",
        "menu_chat_mode": "🔄 Выбрать режим чата",
        "menu_dialog_history": "📂 История разговоров",
        "menu_get_tokens": "👥 Бесплатные токены",
        "menu_balance": "💰 Баланс (Кредиты)",
        "menu_settings": "⚙️ Настройки",
        "menu_help": "❓ Помощь",
        "settings_title": "*Настройки*\n\nВыберите, что вы хотите изменить:",
        "settings_model": "🤖 Модель ИИ",
        "settings_language": "🌐 Язык",
        "settings_name": "👤 Ваше имя",
        "settings_choose_model": "Выберите модель ИИ, которую вы хотите использовать:",
        "settings_choose_language": "*Выбор языка*\n\nВыберите язык интерфейса:",
        "settings_change_name": "*Изменение имени*\n\nВведите команду /setname [ваше_имя], чтобы изменить свое имя в боте.",
        "model_not_available": "Выбранная модель недоступна.",
        "model_selected": "Выбранная модель: *{model}*\nСтоимость: *{credits}* кредит(ов) за сообщение\n\nТеперь вы можете задать вопрос.",
        "language_selected": "Язык изменен на: *{language_display}*",
        "choose_language": "Выберите язык интерфейса:",
        "history_title": "*История разговоров*",
        "history_user": "Вы",
        "history_bot": "Бот",
        "history_no_conversation": "У вас нет активных разговоров.",
        "history_empty": "История разговоров пуста.",
        "history_delete_button": "🗑️ Удалить историю",
        "history_deleted": "*История была очищена*\n\nНачат новый разговор.",
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
        "activation_code_usage": "Использование: /code [активационный_код]\n\nНапример: /code ABC123",
        "activation_code_invalid": "❌ *Ошибка!* ❌\n\nУказанный активационный код недействителен или уже использован.",
        "activation_code_success": "✅ *Код активирован!* ✅\n\nКод *{code}* успешно активирован.\nДобавлено *{credits}* кредитов на ваш счет.\n\nТекущий баланс кредитов: *{total}*",
        "credits": "кредитов",
        "credits_status": "Ваш текущий баланс кредитов: *{credits}* кредитов",
        "help_text": "*Помощь и информация*\n\n*Доступные команды:*\n/start - Начать использование бота\n/credits - Проверить баланс кредитов и купить больше\n/buy - Купить пакет кредитов\n/status - Проверить статус аккаунта\n/newchat - Начать новый разговор\n/mode - Выбрать режим чата\n/image [описание] - Сгенерировать изображение\n/restart - Обновить информацию о боте\n/menu - Показать это меню\n/code [код] - Активировать промокод\n\n*Использование бота:*\n1. Просто введите сообщение, чтобы получить ответ\n2. Используйте кнопки меню для доступа к функциям\n3. Вы можете загружать фотографии и документы для анализа\n\n*Поддержка:*\nЕсли вам нужна помощь, свяжитесь с нами: @twoj_kontakt_wsparcia",
        "generating_response": "⏳ Генерация ответа...",
        "analyzing_document": "Анализирую файл, пожалуйста, подождите...",
        "analyzing_photo": "Анализирую фото, пожалуйста, подождите...",
        "generating_image": "Генерирую изображение, пожалуйста, подождите...",
        
        # Klucze dla obsługi języka i restartu
        "restart_suggestion": "Чтобы применить новый язык ко всем элементам бота, используйте кнопку ниже.",
        "restart_button": "🔄 Перезапустить бота",
        "restarting_bot": "Перезапуск бота с новым языком...",
        "language_restart_complete": "✅ Бот был перезапущен! Все элементы интерфейса теперь на языке: *{language_display}*",
        
        # Klucze dla obrazów
        "image_usage": "Использование: /image [описание изображения]",
        "generated_image": "Сгенерированное изображение:",
        "cost": "Стоимость",
        "image_generation_error": "Извините, произошла ошибка при генерации изображения. Пожалуйста, попробуйте снова с другим описанием.",
        "low_credits_warning": "Внимание:",
        "low_credits_message": "У вас осталось только *{credits}* кредитов. Купите больше с помощью команды /buy."
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