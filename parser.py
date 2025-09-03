import json

import websockets
from websockets.asyncio.client import ClientConnection


async def parse_msg(msgs: dict, userfilter: list, last_msg_id: int, wss: ClientConnection, chat_id: int):
    print(type(wss))
    text_messages = []
    if "messages" in msgs["payload"]:
        for msg in msgs["payload"]["messages"]:
            if (not userfilter or msg["sender"] in userfilter ) and int(msg["id"]) > int(last_msg_id):
                text = msg["text"]
                text_messages.append(text)
                last_msg_id = int(msg["id"])
                text_messages.extend(await parse_attaches(msg, wss, chat_id))
    if "message" in msgs["payload"]:
        msg = msgs["payload"]["message"]
        if (not userfilter or msg["sender"] in userfilter) and int(msg["id"]) > int(last_msg_id) and int(msgs["payload"]["chatId"]) == chat_id:
            text = msg["text"]
            text_messages.append(text)
            last_msg_id = int(msg["id"])
            if msg["attaches"]:
                for attach in msg["attaches"]:
                    text_messages.extend(await parse_attaches(msg, wss, chat_id))


    with open("bot_mem", "r") as bot_mem:
        chat_id = bot_mem.readlines()[0].rstrip("\n")
    with open("bot_mem", "w") as bot_mem:
        bot_mem.write(chat_id)
        bot_mem.write("\n")
        bot_mem.write(str(last_msg_id))
    return text_messages

async def parse_attaches(msg, wss, chat_id):
    res = []
    if msg["attaches"]:
        for attach in msg["attaches"]:
            if attach["_type"] == 'PHOTO':
                if "preview" in attach:
                    res.append(attach["preview"]["baseUrl"])
                else:
                    res.append(attach["baseUrl"])
            if attach["_type"] == 'FILE':
                await wss.send(json.dumps({
                    "ver": 11,
                    "cmd": 0,
                    "seq": 18,
                    "opcode": 88,
                    "payload": {
                        "fileId": attach["fileId"],
                        "chatId": chat_id,
                        "messageId": msg["id"]
                                }
                }))
                file = await wss.recv()
                file = json.loads(file)
                while int(file["opcode"]) != 88:
                    file = await wss.recv()
                    file = json.loads(file)
                print(file)
                res.append(file["payload"]["url"])

    return res