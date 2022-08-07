import os
import subprocess
import time
#import psutil
from globalDir import*

class ProcessManage:
    def __init__(self): 
        self.processDic = {"master": ["master"], "ledger": ["ledger"]}

    def watchProcess(self, processStr):
        global processInfofile
        pro = {}
        prostr = ""
        processfile = processInfofile
        #if os.path.exists(processfile) and os.path.isfile(processfile):
        # os.remove(processfile)
        try:
            os.system("ps -ef | grep kfc | grep -v grep >%s" % processfile)
            file = open(processfile, "r")
            prostr = file.read()
            file.close
        except Exception:
            print("Exception")
        listpro = []
        itpro = []
        for key, value in self.processDic.items():
            if prostr.find(key) == -1:
                listpro.append(key)
            else:
                for item in value:
                    if prostr.find(item) == -1:
                        itpro.append(item + "_" + key)
        if len(listpro):
            pro["mainpro"] = listpro
        if len(itpro):
            pro["branch"] = itpro
        processStr["process"] = pro
        if pro == {}:

            return True 
        return False






