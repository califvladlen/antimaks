import json
import os
import asyncio
import websockets
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from parser import parse_msg

dp = Dispatcher()

async def run_bot(first_msg, second_msg, from_chat_id, userfilter, request_domen):
    tasks = [dp.start_polling(bot), parse_wss(first_msg, second_msg, from_chat_id, userfilter, request_domen)]
    await asyncio.gather(*tasks)

@dp.message(Command("start"))
async def start(message):
    with open("bot_mem", "r") as bot_mem:
        last_msg = bot_mem.readlines()[1].rstrip("\n")
    with open("bot_mem", "w") as f1:
        f1.write(str(message.chat.id))
        f1.write("\n")
        f1.write(last_msg)
    await bot.send_message(message.chat.id, "чат изменён")


def main():
    global bot
    global dp
    global admins_list
    if ("bot_mem" not in os.listdir() or "first.json" not in os.listdir() or
            "second.json" not in os.listdir() or "bot_settings.json" not in os.listdir()):
        print("Внимание! Необходимо прописать начальные сообщения! Как и откуда взять необходимые данные смотреть тут:")
        return
    with open("first.json") as first:
        first_msg = json.load(first)
    with open("second.json") as second:
        second_msg = json.load(second)
    with open("bot_settings.json") as settings_file:
        settings_file = json.load(settings_file)
        bot_token = settings_file["token"]
        admins_list = settings_file["admins"]
        from_chat_id = settings_file["from_chat_id"]
        userfilter = settings_file["userfilter"]
        request_domen = settings_file["requests_domen"]
    bot = Bot(bot_token)
    asyncio.run(run_bot(first_msg, second_msg, from_chat_id, userfilter, request_domen))



async def parse_wss(first_msg, second_msg, from_chat_id, userfilter, request_domen):
    try:
        async with websockets.connect(request_domen) as wss:
            await wss.send(json.dumps(first_msg))
            res = await wss.recv()
            print(res)
            await wss.send(json.dumps(second_msg))
            res = await wss.recv()
            print(res)
            get_msg_req = json.dumps({"ver": 11,
                           "cmd": 0,
                           "seq": 14,
                           "opcode": 49,
                           "payload":
                               {"chatId": int(from_chat_id),
                                "from": 9999999999999,
                                "forward": 0,
                                "backward": 30,
                                "getMessages": True}})
            while True:
                with open("bot_mem", "r") as bot_mem:
                    last_msg = int(bot_mem.readlines()[1].rstrip("\n"))
                await wss.send(get_msg_req)
                res = await wss.recv()
                res = json.loads(res)
                print(res)
                meseges = await parse_msg(res, userfilter, last_msg, wss, int(from_chat_id))
                with open("bot_mem", "r") as bot_mem:
                    to_chat = int(bot_mem.readlines()[0].rstrip("\n"))
                for i in meseges:
                    if i:
                        await bot.send_message(to_chat, i)
                        await asyncio.sleep(2)
                await asyncio.sleep(10)
    except Exception as ex:
        print(ex)
        asyncio.get_event_loop().stop()
if __name__ == "__main__":
    main()
