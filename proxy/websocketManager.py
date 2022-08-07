import json
import time
from threading import Thread, Lock
from typing import Sized
from websocket import WebSocketApp
from strategyProcessing import strategyProcessing
from logManage import logManage
from accountManage import accountManage

class WebsocketManager:
    _CONNECT_TIMEOUT_S = 5

    def __init__(self):
        self.connect_lock = Lock()
        self.ws = None
        self.isconnect = False

    def _get_url(self):
        raise NotImplementedError()

    def _on_message(self, ws, message):
        raise NotImplementedError()

    def send(self, message):
        self.connect()
        self.ws.send(message)

    def send_json(self, message):
        self.send(json.dumps(message))

    def _connect(self):
        print(self._get_url())
        assert not self.ws, "ws should be closed before attempting to connect"

        self.ws = WebSocketApp(
            self._get_url(),
            on_message=self._wrap_callback(self._on_message),
            on_close=self._wrap_callback(self._on_close),
            on_error=self._wrap_callback(self._on_error),
        )
        #self._run_websocket(self.ws)
        wst = Thread(target=self._run_websocket, args=(self.ws,))
        wst.daemon = True
        wst.start()
        # Wait for socket to connect
        ts = time.time()
        while self.ws and (not self.ws.sock or not self.ws.sock.connected):
            if time.time() - ts > self._CONNECT_TIMEOUT_S:
                print("timtiie")
                self.ws = None
                return
            time.sleep(0.1)

    def _wrap_callback(self, f):
        def wrapped_f(ws, *args, **kwargs):
            if ws is self.ws:
                try:
                    f(ws, *args, **kwargs)
                except Exception as e:
                    raise Exception(f'Error running websocket callback: {e}')
        return wrapped_f

    def _run_websocket(self, ws):
        try:
            print("----------------")
            ws.run_forever()
        except Exception as e:
            raise Exception(f'Unexpected error while running websocket: {e}')
        finally:
            print("fffffffffffffffffffffff")
            self.isconnect = False
            self._reconnect(ws)

    def _reconnect(self, ws):
        assert ws is not None, '_reconnect should only be called with an existing ws'
        if ws is self.ws:
            ws.close()
            

    def connect(self):
        if self.ws:
            return
        with self.connect_lock:
            while not self.ws:
                self._connect()
                if self.ws:
                    return

    def _on_close(self, ws):
        print("---------_on_close_on_close")
        if not self.isconnect:
            self.ws.sock = None
            self.ws = None
            self.isconnect = True
            self.connect()
        #self._reconnect(ws)

    def _on_error(self, ws, error):
        print("---------++++++++++---errror",error)
        #self._reconnect(ws)
        if not self.isconnect:
            self.ws.sock = None
            self.ws = None


            self.isconnect = True
            self.connect()

    def reconnect(self) -> None:
        if self.ws is not None:
            self._reconnect(self.ws)
        
class websocketClient(WebsocketManager):
    _ENDPOINT = 'ws://18.166.202.8:9999'   
    #_ENDPOINT = 'ws://192.168.0.13:9999'
    def __init__(self) -> None:
        super().__init__()
        self.strategyProcessing = strategyProcessing()
        self.logManage = logManage(self.strategyProcessing.getHome())
        self.accountManage = accountManage()
        wst = Thread(target=self.watchProcess, args=())
        wst.daemon = True
        wst.start()
    
    def watchProcess(self):
        while(True):
            time.sleep(5)
            if self.ws and self.ws.sock and self.ws.sock.connected:
                proc = {}
                self.strategyProcessing.processManage.watchProcess(processStr=proc)
                #dic = {}
                proc['op'] = 'watch'
                #dic['pro'] = proc
                js = json.dumps(proc)
                self.send(js)

    def _get_url(self) -> str:
        return self._ENDPOINT
    
    def NameFormat(self, strategyName):
        pos = strategyName.find("@")
        print(pos)
        return strategyName[0:pos]

    def _on_message(self, ws, raw_message: str) -> None:
        print("on_message{}", raw_message)
        message = json.loads(raw_message)
        message_type = message['type']
        if message_type == 'file':                                                         #策略接收
            fileName = message["name"]
            fileName = self.NameFormat(fileName)
            content = str(message["content"])
            dict = message["exchange"]
            size = message["size"]
            username = message["accountuser"]
            if(len(content) == size):
                dict = json.loads(dict)
                self.strategyProcessing.write(fileName, content, dict, username)
                self.send("{\"op\":\"write\",\"name\":\"" + message["name"] + "\",\"result\":\"success\"}")    
            else:
                self.send("{\"op\":\"write\",\"name\":\"" + message["name"] + "\",\"result\":\"faild\"}")
            self.logManage.createdependlog(fileName)   
        elif message_type == 'start':                                                        #策略执行开始
            strategyName = message["strategyName"]
            strategyName = self.NameFormat(strategyName)
            self.strategyProcessing.startStrategy(strategyName)
            time.sleep(23)
            proc = {}
            if self.strategyProcessing.processManage.watchProcess(processStr=proc):
                self.send("{\"op\":\"start\",\"name:\":\"" + message["strategyName"] + "\",\"result\":\"success\"}")
            else:
                print("----------------------")
                self.send("{\"op\":\"start\",\"name\":\"" + message["strategyName"] + "\",\'pro\":" + str(proc) + ",\"result\":\"faild\"}")
            print("proc__", proc)
        elif message_type == "stop":                                                          #策略停止
            strategyName = message["strategyName"]
            strategyName = self.NameFormat(strategyName)
            self.strategyProcessing.stopStrategy(strategyName)
            self.send("{\"op\":\"stop\",\"name:\":\"" + message["strategyName"] + "\",\"result\":\"success\"}")  
        elif message_type == "log":                                                           #回传日志
            strategyName = message["strategyName"]
            strategyName = self.NameFormat(strategyName)
            result = self.logManage.sendlog(self, message["strategyName"], "strategy")
            if result != "success":
                self.send("{\"op\":log,\"result\":" + result + "\"faild\"}")
        elif message_type == "addAccount":                                                   #添加账号                                         
            group = message["source"]
            if "md" in message:
                md_value = json.loads(message["md"])
                accountManage.insertConfig(category=0, group=group, value=md_value)
            if "td" in message:
                td_value = json.loads(message["td"])
                accountManage.insertConfig(category=1, group=group, value=td_value)

        

def ProcessStart():
    client = websocketClient()
    client.send("{\"admin\":\"123456\"}")
    while(True):
        time.sleep(20)

ProcessStart()
