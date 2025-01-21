import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import router


# Создаем экземпляры бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

# docker build -t healthtracker - создание образа
# docker run -d --name healthtracker healthtracker - запуск образа


# Основная функция запуска бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
