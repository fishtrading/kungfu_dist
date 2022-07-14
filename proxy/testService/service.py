import asyncio
from hashlib import new
import websockets
import json
from threading import Thread, Lock

list = []

async def check_permit(websocket):
    while True:
        recv_str = await websocket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "123456":
            response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
            await websocket.send(response_str)
            return True
        else:
            response_str = "sorry, the username or password is wrong, please submit again"
            await websocket.send(response_str)
            


async def recv_msg(websocket):
    print("reveeeeee")
    j = 0
    while True:
        recv_text = await websocket.recv()
        print("ttttttttttteee{}", recv_text)
        if recv_text == "admin:123456":
            response_t = "{\"type\":\"file\",\"name\":\"testgate@1123\",\"content\":\"111111\",\"exchange\":{\"gate\":\"888\",\"bian\":\"666\"},\"size\":6}"
            response_stop = "{\"type\":\"stop\",\"strategyName\":\"testgate@1123\"}"
        #response_text = f"your submit context: {recv_text}"
            await websocket.send(response_t)
        elif  recv_text.find("write") != -1:
            response_start = "{\"type\":\"start\",\"strategyName\":\"testgate@1123\"}"
            await websocket.send(response_start)


async def main_logic(websocket, path):
    #await check_permit(websocket)
    #readd = websocket.remote_address()
    print("addddddd7777777777777777")
    await recv_msg(websocket)

def function():
    global list
    i = 0
    for item in list:
        if i == 0:
            i = i + 1
            item.send("1")
        elif i == 1:
            item.send("2")

# 把ip换成自己本地的ip
start_server = websockets.serve(main_logic, '127.0.0.1', 5001)

#wst = Thread(target=function, args=())
#wst.daemon = True
#wst.start()
# 如果要给被回调的main_logic传递自定义参数，可使用以下形式
# 一、修改回调形式
# import functools
# start_server = websockets.serve(functools.partial(main_logic, other_param="test_value"), '10.10.6.91', 5678)
# 修改被回调函数定义，增加相应参数
# async def main_logic(websocket, path, other_param)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()