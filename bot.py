import logging
import requests
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


# Токен вашего бота
TOKEN = '5613235199:AAEgAf-FW8r264B1cStR9SfFSOAaGzptlv8'

# URL вашего FastAPI приложения
API_URL = 'http://localhost:8000'

# Инициализация логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Обработчик команды /start
async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я могу отправить тебе график за последние сутки. Просто введи команду /plot")


# Обработчик команды /plot
async def plot(update, context):
    # Отправляем запрос к FastAPI приложению для получения картинки
    response = requests.get(API_URL + '/plot')
    if response.status_code != 200:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ошибка при получении графика")
        return

    # Отправляем пользователю картинку
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=response.content)


# Обработчик текстовых сообщений
async def echo(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, я не понимаю эту команду. Попробуйте /start или /plot")


def main():
    # Инициализация бота
    app = Application.builder().token(TOKEN).build()

    # Добавление обработчиков команд и сообщений
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('plot', plot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запуск бота
    app.run_polling()


if __name__ == '__main__':
    main()
