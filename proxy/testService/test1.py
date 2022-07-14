
import time
from threading import Thread, Lock
test = 1

def __init__():
    print("iniititii")

def fun1():
    global test
    print("testfun1", test)


def thfun2():
    global test
    test = 3
    print("thfun2", test)
    while(True):
        time.sleep(1)

def run():
    wst = Thread(target=thfun2, args=())
    wst.daemon = True
    wst.start()
