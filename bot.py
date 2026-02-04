import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    total_specialties = database.get_specialty_count()
    total_universities = database.get_total_universities()

    welcome_text = (
        "🏫 **Бот для выбора вузов**\n\n"
        f"📊 *В базе данных:*\n"
        f"• *{total_specialties} популярных специальностей*\n"
        f"• *{total_universities} вузов*\n"
        f"• *Акцент на московские вузы*\n\n"
        "Выберите специальность:"
    )

    specialties = database.get_all_specialties()

    keyboard = []
    row = []
    for i, specialty in enumerate(specialties, 1):
        if i == 1:
            emoji = "💻"
        elif i == 2:
            emoji = "💰"
        elif i == 3:
            emoji = "⚖️"
        elif i == 4:
            emoji = "🏥"
        elif i == 5:
            emoji = "🧠"
        elif i == 6:
            emoji = "🏗️"
        elif i == 7:
            emoji = "🗣️"
        elif i == 8:
            emoji = "📊"
        elif i == 9:
            emoji = "📰"
        else:
            emoji = "🎨"

        button_text = f"{emoji} {specialty[:20]}" if len(specialty) > 20 else f"{emoji} {specialty}"
        row.append(InlineKeyboardButton(button_text, callback_data=f"spec_{specialty}"))

        if len(row) == 2 or i == len(specialties):
            keyboard.append(row)
            row = []

    keyboard.append([InlineKeyboardButton("❓ Помощь", callback_data="help")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_specialty_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    specialty = query.data.replace("spec_", "")

    universities = database.get_universities_by_specialty(specialty, limit=8)

    if not universities:
        keyboard = [
            [InlineKeyboardButton("🔙 Назад к выбору", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(
            f"По специальности '{specialty}' вузы не найдены.",
            reply_markup=reply_markup
        )
        return

    moscow_count = sum(1 for uni in universities if uni[1] == 'Москва')
    other_count = len(universities) - moscow_count

    result_text = f"🎓 **Специальность:** {specialty}\n\n"
    result_text += f"🏛 **Найдено вузов:** {len(universities)} (Москва: {moscow_count}, другие: {other_count})\n\n"

    moscow_unis = [u for u in universities if u[1] == 'Москва']
    other_unis = [u for u in universities if u[1] != 'Москва']

    if moscow_unis:
        result_text += "**📍 Московские вузы:**\n\n"
        for i, (name, city, passing_score, link) in enumerate(moscow_unis, 1):
            result_text += f"{i}. **{name}**\n"
            result_text += f"   🎯 Проходной балл: {passing_score}\n"
            if link and link not in ['None', '']:
                clean_link = link.strip()
                if not clean_link.startswith('http'):
                    clean_link = 'https://' + clean_link
                result_text += f"   🔗 [Сайт]({clean_link})\n"
            result_text += "\n"

    if other_unis:
        result_text += "**🌍 Вузы других городов:**\n\n"
        for i, (name, city, passing_score, link) in enumerate(other_unis, 1):
            result_text += f"{i}. **{name}** ({city})\n"
            result_text += f"   🎯 Проходной балл: {passing_score}\n"
            if link and link not in ['None', '']:
                clean_link = link.strip()
                if not clean_link.startswith('http'):
                    clean_link = 'https://' + clean_link
                result_text += f"   🔗 [Сайт]({clean_link})\n"
            result_text += "\n"

    keyboard = [
        [InlineKeyboardButton("🔙 Выбрать другую специальность", callback_data="back_to_start")],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="start")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.message.edit_text(
            result_text,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        if len(result_text) > 4000:
            part1 = result_text[:4000]
            await query.message.edit_text(part1, parse_mode='Markdown')
            part2 = result_text[4000:]
            await query.message.reply_text(part2, parse_mode='Markdown')


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "❓ **Помощь по использованию бота**\n\n"

        "🎯 **Особенности базы данных:**\n"
        "• 10 самых популярных специальностей\n"
        "• Акцент на московские вузы\n"
        "• Для каждой специальности показаны 5-8 лучших вузов\n"
        "• Проходные баллы за 2024 год\n\n"

        "📱 **Как пользоваться:**\n"
        "1. Нажмите /start\n"
        "2. Выберите специальность из списка\n"
        "3. Посмотрите список подходящих вузов\n"
        "4. Московские вузы показываются первыми\n\n"

        "💡 **Проходной балл:**\n"
        "• Это сумма баллов ЕГЭ, необходимая для поступления\n"
        "• Чем выше балл, тем престижнее вуз\n"
        "• Баллы обновляются ежегодно\n\n"

        "🏛 **О вузах:**\n"
        "• Для каждого вуза указан проходной балл\n"
        "• Есть ссылки на официальные сайты\n"
        "• Московские вузы выделены отдельно"
    )

    keyboard = [
        [InlineKeyboardButton("🏠 В главное меню", callback_data="start")],
        [InlineKeyboardButton("📋 Список специальностей", callback_data="back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_help(update, context)


async def handle_back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await start(update, context)


def main() -> None:
    TOKEN = "8510360465:AAH7bBJuHkAWWHT8KqObi9lV4s6hGLbTXAA"

    print("Запуск бота с 10 специальностями...")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CallbackQueryHandler(start, pattern="^start$"))
    application.add_handler(CallbackQueryHandler(handle_specialty_selection, pattern="^spec_"))
    application.add_handler(CallbackQueryHandler(show_help, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(handle_back_to_start, pattern="^back_to_start$"))

    application.add_error_handler(error_handler)

    print("Бот запущен. Ожидание сообщений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Ошибка: {context.error}")

    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Произошла ошибка. Пожалуйста, нажмите /start."
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение: {e}")


if __name__ == '__main__':
    main()