from aiogram import Bot, Dispatcher
import asyncio
from aiogram.filters import Command
import json
import os

# Инициализация

dp = Dispatcher()

async def main():

    tasks=[dp.start_polling(bot)]
    await asyncio.gather(*tasks)

@dp.message(Command("start"))
async def start(message):
    with open("bot_mem", "w") as f1:
        f1.write(str(message.chat.id))
        f1.write("\n")
        f1.write("0")
    await bot.send_message(message.chat.id, "первичная настройка окончена")
    exit(0)


if __name__ == "__main__":
    if "bot_mem" not in os.listdir():
        open("bot_mem", "w").close()
    if "first.json" not in os.listdir() or "second.json" not in os.listdir() or "bot_settings.json" not in os.listdir():
        print("Внимание! Необходимо прописать начальные сообщения! Как и откуда взять необходимые данные смотреть тут:")
        open("first.json", "w").close()
        open("second.json", "w").close()
        with open("bot_settings.json", "w") as settings_file:
            settings_file.write('{\n"token": "",\n"admins": [""],\n"from_chat_id": "",\n"userfilter": [],\n"requests_domen": ""\n}')
        exit(0)
    with open("bot_settings.json") as settings_file:
        bot_token = json.load(settings_file)["token"]
    bot = Bot(bot_token)
    asyncio.run(main())