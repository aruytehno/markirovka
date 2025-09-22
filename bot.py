import os
import logging
import tempfile
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from telegram.error import TelegramError
from config import BOT_TOKEN
from core.code_service import CodeService
from core.code_manager import FreeCodeManager
from utils.file_utils import format_validation_results

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarkirovkaBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.code_service = CodeService()
        self.free_manager = FreeCodeManager()
        self.setup_handlers()

    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("validate", self.validate))
        self.app.add_handler(CommandHandler("extract", self.extract))
        self.app.add_handler(CommandHandler("available", self.available))
        self.app.add_handler(CallbackQueryHandler(self.handle_inline_button))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        self.app.add_handler(MessageHandler(filters.Document.FileExtension("txt"), self.handle_txt_file))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🔍 Проверка кодов через API", callback_data="mode_validate")],
            [InlineKeyboardButton("📄 Извлечение кодов из PDF", callback_data="mode_extract")],
            [InlineKeyboardButton("📦 Получение свободных кодов", callback_data="mode_available")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🎯 Markirovka Bot\n\n"
            "Выберите режим работы:",
            reply_markup=reply_markup
        )

    async def validate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🔍 Отправьте коды для проверки (каждый код с новой строки) или прикрепите txt-файл")
        context.user_data['awaiting_codes_for'] = 'validate'

    async def extract(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📄 Отправьте коды для извлечения (каждый код с новой строки) или прикрепите txt-файл")
        context.user_data['awaiting_codes_for'] = 'extract'

    async def available(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            products = self.free_manager.get_available_products()
            if not products:
                await update.message.reply_text("❌ Нет доступных товаров")
                return

            # Создаем инлайн кнопки для выбора товара
            keyboard = []
            for i, product in enumerate(products):
                keyboard.append([InlineKeyboardButton(product, callback_data=f"product_{i}")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "📦 Выберите товар для получения свободных кодов:",
                reply_markup=reply_markup
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
            logger.error(f"Available error: {e}")

    async def handle_inline_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатия инлайн кнопок"""
        query = update.callback_query
        await query.answer()

        try:
            if query.data.startswith('product_'):
                product_idx = int(query.data.split('_')[1])
                products = self.free_manager.get_available_products()

                if 0 <= product_idx < len(products):
                    product_name = products[product_idx]
                    context.user_data['selected_product'] = product_name

                    await query.edit_message_text(
                        f"📦 Выбран товар: {product_name}\n\n"
                        "Введите количество кодов, которое нужно получить:"
                    )
                else:
                    await query.edit_message_text("❌ Ошибка выбора товара")

            elif query.data == 'mode_validate':
                await query.edit_message_text(
                    "🔍 Отправьте коды для проверки (каждый код с новой строки) или прикрепите txt-файл")
                context.user_data['awaiting_codes_for'] = 'validate'

            elif query.data == 'mode_extract':
                await query.edit_message_text(
                    "📄 Отправьте коды для извлечения (каждый код с новой строки) или прикрепите txt-файл")
                context.user_data['awaiting_codes_for'] = 'extract'

            elif query.data == 'mode_available':
                try:
                    products = self.free_manager.get_available_products()
                    if not products:
                        await query.edit_message_text("❌ Нет доступных товаров")
                        return

                    keyboard = []
                    for i, product in enumerate(products):
                        keyboard.append([InlineKeyboardButton(product, callback_data=f"product_{i}")])

                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(
                        "📦 Выберите товар для получения свободных кодов:",
                        reply_markup=reply_markup
                    )

                except Exception as e:
                    await query.edit_message_text(f"❌ Ошибка: {str(e)}")

        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")
            logger.error(f"Inline button error: {e}")

    async def process_codes(self, update: Update, context: ContextTypes.DEFAULT_TYPE, codes: list[str], operation: str):
        """Обработка кодов для разных операций"""
        try:
            if not codes:
                await update.message.reply_text("❌ Не получены коды для обработки")
                return

            if operation == 'validate':
                results = self.code_service.get_api_data(codes)

                # Создаем отчет в памяти
                report_content = format_validation_results(results)
                report_file = BytesIO(report_content.encode('utf-8'))
                report_file.name = f"validation_report_{len(codes)}_codes.txt"

                await update.message.reply_document(document=report_file)
                await update.message.reply_text(f"✅ Проверено {len(codes)} кодов")

            elif operation == 'extract':
                results_api = self.code_service.get_api_data(codes)
                results_pdf = self.code_service.get_pdf_with_codes(codes)

                # Отправляем отчет по API
                report_content = format_validation_results(results_api)
                report_file = BytesIO(report_content.encode('utf-8'))
                report_file.name = f"validation_report_{len(codes)}_codes.txt"
                await update.message.reply_document(document=report_file)

                # Отправляем PDF файлы
                for count, product_name, pdf_bytes in results_pdf:
                    pdf_file = BytesIO(pdf_bytes)
                    pdf_file.name = f"({count})_{product_name}.pdf"
                    await update.message.reply_document(document=pdf_file)

                await update.message.reply_text(f"✅ Обработано {len(codes)} кодов")

            elif operation == 'available':
                results_api = self.code_service.get_api_data(codes)
                results_pdf = self.code_service.get_pdf_with_codes(codes)

                # Отправляем отчет
                report_content = format_validation_results(results_api)
                report_file = BytesIO(report_content.encode('utf-8'))
                report_file.name = f"free_codes_report_{len(codes)}_codes.txt"
                await update.message.reply_document(document=report_file)

                # Отправляем PDF
                for count, product_name, pdf_bytes in results_pdf:
                    pdf_file = BytesIO(pdf_bytes)
                    pdf_file.name = f"({count})_{product_name}.pdf"
                    await update.message.reply_document(document=pdf_file)

                await update.message.reply_text(f"✅ Получено {len(codes)} свободных кодов")

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
            logger.error(f"Process codes error: {e}")


    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений с кодами"""
        try:
            # Проверяем, ожидаем ли мы коды для команды validate/extract
            if 'awaiting_codes_for' in context.user_data:
                operation = context.user_data['awaiting_codes_for']
                codes = self._extract_codes_from_text(update.message.text)

                if codes:
                    await self.process_codes(update, context, codes, operation)
                    context.user_data.pop('awaiting_codes_for', None)
                else:
                    await update.message.reply_text("❌ Не найдены коды в сообщении")
                return

            # Обработка количества кодов для available
            if 'selected_product' in context.user_data:
                try:
                    quantity = int(update.message.text.strip())
                    if quantity <= 0:
                        await update.message.reply_text("❌ Количество должно быть положительным числом")
                        return

                    product_name = context.user_data['selected_product']
                    await update.message.reply_text(f"🔍 Ищем {quantity} кодов для {product_name}...")

                    free_codes = self.free_manager.get_free_codes(product_name, quantity)
                    if not free_codes:
                        await update.message.reply_text("❌ Не удалось получить коды")
                        return

                    # Обрабатываем полученные коды
                    await self.process_codes(update, context, free_codes, 'available')

                    # Очищаем контекст
                    context.user_data.pop('selected_product', None)

                except ValueError:
                    await update.message.reply_text("❌ Введите число - количество кодов")
                except Exception as e:
                    await update.message.reply_text(f"❌ Ошибка: {str(e)}")
                    logger.error(f"Available quantity error: {e}")

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
            logger.error(f"Handle text message error: {e}")

    async def handle_txt_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка txt-файлов с кодами"""
        try:
            if 'awaiting_codes_for' not in context.user_data:
                await update.message.reply_text("❌ Сначала используйте команду /validate или /extract")
                return

            document = update.message.document
            file = await document.get_file()
            file_content = await file.download_as_bytearray()
            text_content = file_content.decode('utf-8')

            codes = self._extract_codes_from_text(text_content)
            operation = context.user_data['awaiting_codes_for']

            if codes:
                await self.process_codes(update, context, codes, operation)
                context.user_data.pop('awaiting_codes_for', None)
            else:
                await update.message.reply_text("❌ Не найдены коды в файле")

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при обработке файла: {str(e)}")
            logger.error(f"Handle txt file error: {e}")

    def _extract_codes_from_text(self, text: str) -> list[str]:
        """Извлечение кодов из текста - каждая непустая строка это отдельный код"""
        lines = text.splitlines()
        codes = []
        for line in lines:
            line = line.strip()
            if line and any(char.isdigit() for char in line) and len(line) >= 10:
                codes.append(line)
        return codes

    def run(self):
        logger.info("Bot started")
        self.app.run_polling()


if __name__ == "__main__":
    bot = MarkirovkaBot()
    bot.run()