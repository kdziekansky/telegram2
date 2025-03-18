from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import BOT_NAME
from utils.translations import get_text
from database.credits_client import (
    get_user_credits, add_user_credits, deduct_user_credits, 
    get_credit_packages, get_package_by_id, purchase_credits,
    get_user_credit_stats
)
# Add imports at the beginning of the file
from utils.credit_analytics import (
    generate_credit_usage_chart, generate_usage_breakdown_chart, 
    get_credit_usage_breakdown, predict_credit_depletion
)
import matplotlib
matplotlib.use('Agg')  # Required for operation without a graphical interface

from database.credits_client import add_stars_payment_option, get_stars_conversion_rate


# Function moved from menu_handler.py to avoid circular import
def get_user_language(context, user_id):
    """
    Get the user's language from context or database
    
    Args:
        context: Bot context
        user_id: User ID
        
    Returns:
        str: Language code (pl, en, ru)
    """
    # Check if language is saved in context
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data'] and 'language' in context.chat_data['user_data'][user_id]:
        return context.chat_data['user_data'][user_id]['language']
    
    # If not, get from database
    try:
        from database.sqlite_client import sqlite3, DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT language FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            # Save in context for future use
            if 'user_data' not in context.chat_data:
                context.chat_data['user_data'] = {}
            
            if user_id not in context.chat_data['user_data']:
                context.chat_data['user_data'][user_id] = {}
            
            context.chat_data['user_data'][user_id]['language'] = result[0]
            return result[0]
    except Exception as e:
        print(f"Error getting language from database: {e}")
    
    # Default language if not found in database
    return "pl"

async def credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /credits command
    Display information about user's credits
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    credits = get_user_credits(user_id)
    
    # Create buttons to buy credits
    keyboard = [[InlineKeyboardButton("🛒 Buy credits", callback_data="buy_credits")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send credit information
    await update.message.reply_text(
        get_text("credits_info", language, bot_name=BOT_NAME, credits=credits),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /buy command
    Allows the user to buy credits
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Check if package number is specified
    if context.args and len(context.args) > 0:
        try:
            package_id = int(context.args[0])
            await process_purchase(update, context, package_id)
            return
        except ValueError:
            await update.message.reply_text("Invalid package number. Use a number, e.g. /buy 2")
            return
    
    # If no package number specified, show available packages
    packages = get_credit_packages()
    
    packages_text = ""
    for pkg in packages:
        packages_text += f"*{pkg['id']}.* {pkg['name']} - *{pkg['credits']}* credits - *{pkg['price']} PLN*\n"
    
    # Create buttons to buy credits
    keyboard = []
    for pkg in packages:
        keyboard.append([
            InlineKeyboardButton(
                f"{pkg['name']} - {pkg['credits']} credits ({pkg['price']} PLN)", 
                callback_data=f"buy_package_{pkg['id']}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text("buy_credits", language, packages=packages_text),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def process_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, package_id):
    """
    Process credit package purchase
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Simulate credit purchase (in a real scenario, there would be payment system integration)
    success, package = purchase_credits(user_id, package_id)
    
    if success and package:
        current_credits = get_user_credits(user_id)
        await update.message.reply_text(
            get_text("credit_purchase_success", language,
                package_name=package['name'],
                credits=package['credits'],
                price=package['price'],
                total_credits=current_credits
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            "An error occurred while processing your purchase. Please try again or choose a different package.",
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_credit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle buttons related to credits
    """
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    if query.data == "buy_credits" or query.data == "credits_buy" or query.data == "menu_credits_buy":
        # Redirect to the buy command
        packages = get_credit_packages()
        
        packages_text = ""
        for pkg in packages:
            packages_text += f"*{pkg['id']}.* {pkg['name']} - *{pkg['credits']}* {get_text('credits', language)} - *{pkg['price']} PLN*\n"
        
        # Create buttons to buy credits
        keyboard = []
        for pkg in packages:
            keyboard.append([
                InlineKeyboardButton(
                    f"{pkg['name']} - {pkg['credits']} {get_text('credits', language)} ({pkg['price']} PLN)", 
                    callback_data=f"buy_package_{pkg['id']}"
                )
            ])
        
        # Add button for star purchases
        keyboard.append([
            InlineKeyboardButton("⭐ " + get_text("buy_with_stars", language, default="Buy with Telegram Stars"), 
                                callback_data="show_stars_options")
        ])
        
        # Add button to go back to credits menu
        keyboard.append([
            InlineKeyboardButton(get_text("back", language), callback_data="menu_section_credits")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                get_text("buy_credits", language, packages=packages_text),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Błąd przy edycji wiadomości: {e}")
            try:
                # Bez formatowania Markdown
                await query.edit_message_text(
                    get_text("buy_credits", language, packages=packages_text),
                    reply_markup=reply_markup
                )
            except Exception as e2:
                print(f"Drugi błąd przy edycji wiadomości: {e2}")
    
    elif query.data == "credits_check" or query.data == "menu_credits_check":
        # Show user's credit balance
        credits = get_user_credits(user_id)
        
        # Create buttons for credit options
        keyboard = [
            [InlineKeyboardButton(get_text("buy_credits_btn", language), callback_data="credits_buy")],
            [InlineKeyboardButton(get_text("credit_stats", language, default="Statistics"), callback_data="credits_stats")],
            [InlineKeyboardButton(get_text("back", language), callback_data="menu_section_credits")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                get_text("credits_info", language, bot_name=BOT_NAME, credits=credits),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Błąd przy edycji wiadomości: {e}")
            try:
                # Bez formatowania Markdown
                await query.edit_message_text(
                    get_text("credits_info", language, bot_name=BOT_NAME, credits=credits),
                    reply_markup=reply_markup
                )
            except Exception as e2:
                print(f"Drugi błąd przy edycji wiadomości: {e2}")
    
    elif query.data == "credits_stats":
        # Show credit statistics
        stats = get_user_credit_stats(user_id)
        
        # Format the date of last purchase
        last_purchase = "None" if not stats['last_purchase'] else stats['last_purchase'].split('T')[0]
        
        # Create message with statistics
        message = f"""
*📊 {get_text("credits_analytics", language, default="Credit Analytics")}*

{get_text("current_balance", language, default="Current balance")}: *{stats['credits']}* {get_text("credits", language)}
{get_text("total_purchased", language, default="Total purchased")}: *{stats['total_purchased']}* {get_text("credits", language)}
{get_text("total_spent", language, default="Total spent")}: *{stats['total_spent']}* PLN
{get_text("last_purchase", language, default="Last purchase")}: *{last_purchase}*

*📝 {get_text("credit_history", language, default="Transaction history")} ({get_text("last_10", language, default="last 10")}):*
"""
        
        if not stats['usage_history']:
            message += f"\n{get_text('no_transactions', language, default='No transaction history.')}"
        else:
            for i, transaction in enumerate(stats['usage_history']):
                date = transaction['date'].split('T')[0]
                if transaction['type'] == "add" or transaction['type'] == "purchase":
                    message += f"\n{i+1}. ➕ +{transaction['amount']} {get_text('credits', language)} ({date})"
                    if transaction['description']:
                        message += f" - {transaction['description']}"
                else:
                    message += f"\n{i+1}. ➖ -{transaction['amount']} {get_text('credits', language)} ({date})"
                    if transaction['description']:
                        message += f" - {transaction['description']}"
        
        # Add buttons for navigation
        keyboard = [
            [InlineKeyboardButton(get_text("credit_analytics", language, default="Advanced Analytics"), callback_data="credit_advanced_analytics")],
            [InlineKeyboardButton(get_text("back", language), callback_data="credits_check")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Błąd przy edycji wiadomości: {e}")
            try:
                await query.edit_message_text(
                    message,
                    reply_markup=reply_markup
                )
            except Exception as e2:
                print(f"Drugi błąd przy edycji wiadomości: {e2}")
    
    elif query.data.startswith("buy_package_"):
        # Handle purchase of a specific package
        package_id = int(query.data.split("_")[2])
        
        # Simulate credit purchase
        success, package = purchase_credits(user_id, package_id)
        
        if success and package:
            current_credits = get_user_credits(user_id)
            
            # Create buttons
            keyboard = [
                [InlineKeyboardButton(get_text("menu_credits", language), callback_data="menu_section_credits")],
                [InlineKeyboardButton(get_text("back", language), callback_data="menu_back_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_text(
                    get_text("credit_purchase_success", language,
                        package_name=package['name'],
                        credits=package['credits'],
                        price=package['price'],
                        total_credits=current_credits
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            except Exception as e:
                print(f"Błąd przy edycji wiadomości: {e}")
                try:
                    # Bez formatowania Markdown
                    await query.edit_message_text(
                        get_text("credit_purchase_success", language,
                            package_name=package['name'],
                            credits=package['credits'],
                            price=package['price'],
                            total_credits=current_credits
                        ),
                        reply_markup=reply_markup
                    )
                except Exception as e2:
                    print(f"Drugi błąd przy edycji wiadomości: {e2}")
        else:
            # Create button to go back
            keyboard = [[InlineKeyboardButton(get_text("back", language), callback_data="credits_buy")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                get_text("purchase_error", language),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
    # Handle star options button
    elif query.data == "show_stars_options":
        # Get conversion rate
        conversion_rates = get_stars_conversion_rate()
        
        # Create buttons for different star purchase options
        keyboard = []
        for stars, credits in conversion_rates.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"⭐ {stars} stars = {credits} credits", 
                    callback_data=f"buy_stars_{stars}"
                )
            ])
        
        # Add return button
        keyboard.append([
            InlineKeyboardButton(get_text("back", language, default="Back to purchase options"), callback_data="credits_buy")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_text("stars_purchase_info", language, default="🌟 *Purchase Credits with Telegram Stars* 🌟\n\nChoose one of the options below to exchange Telegram stars for credits.\nThe more stars you exchange at once, the better bonus you'll receive!\n\n⚠️ *Note:* To purchase with stars, a Telegram Premium account is required."),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        return
    
    # Handle star purchase buttons
    elif query.data.startswith("buy_stars_"):
        stars_amount = int(query.data.split("_")[2])
        
        # Get conversion rate
        conversion_rates = get_stars_conversion_rate()
        
        # Check if the specified star amount is supported
        if stars_amount not in conversion_rates:
            await query.edit_message_text(
                get_text("stars_invalid_amount", language, default="An error occurred. Invalid number of stars."),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        credits_amount = conversion_rates[stars_amount]
        
        # Here should be a call to Telegram Payments API to collect stars
        # Since this is just a simulation, we assume the payment was successful
        
        # Add credits to user's account
        success = add_stars_payment_option(user_id, stars_amount, credits_amount)
        
        if success:
            current_credits = get_user_credits(user_id)
            await query.edit_message_text(
                get_text("stars_purchase_success", language, default=f"✅ *Purchase completed successfully!*\n\nExchanged *{stars_amount}* stars for *{credits_amount}* credits\n\nCurrent credit balance: *{current_credits}*\n\nThank you for your purchase! 🎉",
                    stars=stars_amount,
                    credits=credits_amount,
                    total=current_credits
                ),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                get_text("purchase_error", language, default="An error occurred while processing the payment. Please try again later."),
                parse_mode=ParseMode.MARKDOWN
            )
    
    elif query.data == "credit_advanced_analytics":
        # This would handle showing more detailed analytics
        # Could display charts or more detailed statistics
        # For now, just redirect to the creditstats command
        
        # Create a fake update to pass to the creditstats command
        class FakeMessage:
            def __init__(self, chat_id):
                self.chat_id = chat_id
                
            async def reply_text(self, *args, **kwargs):
                pass
                
        class FakeUpdate:
            def __init__(self, user_id, chat_id):
                self.effective_user = type('obj', (object,), {'id': user_id})
                self.message = FakeMessage(chat_id)
                self.effective_chat = type('obj', (object,), {'id': chat_id})
        
        fake_update = FakeUpdate(user_id, query.message.chat_id)
        
        # Create fake context args
        if not hasattr(context, 'args'):
            context.args = ["30"]  # Default to 30 days
        
        # Call the creditstats command
        await credit_analytics_command(fake_update, context)
        
        # Return to credit stats
        keyboard = [[InlineKeyboardButton(get_text("back", language), callback_data="credits_stats")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_text("analytics_sent", language, default="Credit usage analytics have been sent as separate messages."),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def credit_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /creditstats command
    Display detailed statistics on user's credits
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    stats = get_user_credit_stats(user_id)
    
    # Format the date of last purchase
    last_purchase = "None" if not stats['last_purchase'] else stats['last_purchase'].split('T')[0]
    
    # Create message with statistics
    message = f"""
*📊 Credit Statistics*

Current balance: *{stats['credits']}* credits
Total purchased: *{stats['total_purchased']}* credits
Total spent: *{stats['total_spent']}* PLN
Last purchase: *{last_purchase}*

*📝 Usage history (last 10 transactions):*
"""
    
    if not stats['usage_history']:
        message += "\nNo transaction history."
    else:
        for i, transaction in enumerate(stats['usage_history']):
            date = transaction['date'].split('T')[0]
            if transaction['type'] == "add" or transaction['type'] == "purchase":
                message += f"\n{i+1}. ➕ +{transaction['amount']} credits ({date})"
                if transaction['description']:
                    message += f" - {transaction['description']}"
            else:
                message += f"\n{i+1}. ➖ -{transaction['amount']} credits ({date})"
                if transaction['description']:
                    message += f" - {transaction['description']}"
    
    # Add button to buy credits
    keyboard = [[InlineKeyboardButton("🛒 Buy credits", callback_data="buy_credits")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

# Add a new function
async def credit_analytics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display credit usage analysis
    Usage: /creditstats [days]
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Check if number of days is specified
    days = 30  # Default 30 days
    if context.args and len(context.args) > 0:
        try:
            days = int(context.args[0])
            # Limit range
            if days < 1:
                days = 1
            elif days > 365:
                days = 365
        except ValueError:
            pass
    
    # Inform user that analysis is starting
    status_message = await update.message.reply_text(
        "⏳ Analyzing credit usage data..."
    )
    
    # Get credit depletion forecast
    depletion_info = predict_credit_depletion(user_id, days)
    
    if not depletion_info:
        await status_message.edit_text(
            "You don't have enough credit usage history to perform analysis. "
            "Try again after performing several operations.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Prepare analysis message
    message = f"📊 *Credit Usage Analysis*\n\n"
    message += f"Current balance: *{depletion_info['current_balance']}* credits\n"
    message += f"Average daily usage: *{depletion_info['average_daily_usage']}* credits\n"
    
    if depletion_info['days_left']:
        message += f"Predicted credit depletion: in *{depletion_info['days_left']}* days "
        message += f"({depletion_info['depletion_date']})\n\n"
    else:
        message += f"Not enough data to predict credit depletion.\n\n"
    
    # Get credit usage breakdown
    usage_breakdown = get_credit_usage_breakdown(user_id, days)
    
    if usage_breakdown:
        message += f"*Credit usage breakdown:*\n"
        for category, amount in usage_breakdown.items():
            percentage = amount / sum(usage_breakdown.values()) * 100
            message += f"- {category}: *{amount}* credits ({percentage:.1f}%)\n"
    
    # Send analysis message
    await status_message.edit_text(
        message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Generate and send usage history chart
    usage_chart = generate_credit_usage_chart(user_id, days)
    
    if usage_chart:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=usage_chart,
            caption=f"📈 Credit usage history for the last {days} days"
        )
    
    # Generate and send usage breakdown chart
    breakdown_chart = generate_usage_breakdown_chart(user_id, days)
    
    if breakdown_chart:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=breakdown_chart,
            caption=f"📊 Credit usage breakdown for the last {days} days"
        )

async def show_stars_purchase_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show options to purchase credits using Telegram stars
    """
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Get conversion rate
    conversion_rates = get_stars_conversion_rate()
    
    # Create buttons for different star purchase options
    keyboard = []
    for stars, credits in conversion_rates.items():
        keyboard.append([
            InlineKeyboardButton(
                f"⭐ {stars} stars = {credits} credits", 
                callback_data=f"buy_stars_{stars}"
            )
        ])
    
    # Add return button
    keyboard.append([
        InlineKeyboardButton("🔙 Return to purchase options", callback_data="buy_credits")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌟 *Purchase Credits with Telegram Stars* 🌟\n\n"
        "Choose one of the options below to exchange Telegram stars for credits.\n"
        "The more stars you exchange at once, the better bonus you'll receive!\n\n"
        "⚠️ *Note:* To purchase with stars, a Telegram Premium account is required.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def process_stars_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, stars_amount):
    """
    Process purchase of credits using Telegram stars
    """
    query = update.callback_query
    user_id = query.from_user.id
    language = get_user_language(context, user_id)
    
    # Get conversion rate
    conversion_rates = get_stars_conversion_rate()
    
    # Check if the specified star amount is supported
    if stars_amount not in conversion_rates:
        await query.edit_message_text(
            "An error occurred. Invalid number of stars.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    credits_amount = conversion_rates[stars_amount]
    
    # Here should be a call to Telegram Payments API to collect stars
    # Since this is just a simulation, we assume the payment was successful
    
    # Add credits to user's account
    success = add_stars_payment_option(user_id, stars_amount, credits_amount)
    
    if success:
        current_credits = get_user_credits(user_id)
        await query.edit_message_text(
            f"✅ *Purchase completed successfully!*\n\n"
            f"Exchanged *{stars_amount}* stars for *{credits_amount}* credits\n\n"
            f"Current credit balance: *{current_credits}*\n\n"
            f"Thank you for your purchase! 🎉",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await query.edit_message_text(
            "An error occurred while processing the payment. Please try again later.",
            parse_mode=ParseMode.MARKDOWN
        )

# Modify the buy_command function, adding support for stars
# Add these conditions at the beginning of the buy_command function:
    
    # Check if user wants to buy with stars
    if context.args and len(context.args) > 0 and context.args[0].lower() == "stars":
        await show_stars_purchase_options(update, context)
        return

# In the handle_credit_callback function, add handling for star buttons
# Add this condition to the handle_credit_callback function before other conditions:

    # Handle star options button
    if query.data == "show_stars_options":
        await show_stars_purchase_options(update, context)
        return
    
    # Handle star purchase buttons
    if query.data.startswith("buy_stars_"):
        stars_amount = int(query.data.split("_")[2])
        await process_stars_purchase(update, context, stars_amount)
        return