import time
import os
from websocketManager import websocketClient
from ProcessManage import ProcessManage

class ProcessClient:
    def __init__(self):
        self.ws = websocketClient()
        self.process = ProcessManage()
        

def watchStart():
    processClient = ProcessClient()
    while(True):
        pro = {}
        processClient.process.watchProcess(pro)
        time.sleep(10)
