import os
import subprocess
import json
from ProcessManage import ProcessManage
from globalDir import*

tdModel = "nohup $KFC_HOME/kfc -l info td -s __EXCHANGE__ -a __ACCOUNT__ > $KFC_LOG/td__EXCHANGE__.log 2>&1 &\n"
mdModel = "nohup $KFC_HOME/kfc md -s __EXCHANGE__  > $KFC_LOG/md__EXCHANGE__.log 2>&1 &\n"
strategyModel = "nohup $KFC_HOME/kfc -l info strategy  -n test -p $KFC_LOG/../__STRATEGY__.py > $KFC_LOG/test__STRATEGY__log 2>&1 &\n"

processModel="#!/bin/sh\n\
ps -ef|grep kfc|grep -v grep\n\
if [ $? -eq 0 ];\
then\n\
   echo \"kfc is good!\"\n\
   ps -ef | grep kfc | grep -v grep | awk '{print $2}' | xargs kill -9\n\
else\
   echo \"kfc is bad!\"\n\
fi\n\
export KFC_HOME=__KFC_HOME__\n\
export KFC_LOG=__ROOT_DIR__/log\n\
export KFC_DATA=__KFC_DATA__\n\
mkdir $KFC_LOG\n\
cd $KFC_HOME\n\
rm -r -f  $KFC_DATA/md\n\
rm -r -f  $KFC_DATA/system/service/\n\
rm -r -f  $KFC_DATA/system/master/\n\
nohup $KFC_HOME/kfc -l info master > $KFC_LOG/master.log 2>&1 &\n\
sleep 4s\n\
nohup $KFC_HOME/kfc -l info ledger > $KFC_LOG/ledger.log 2>&1 &\n\
sleep 4s\n\
__PROCESS_MODEL__"

timeModel = "sleep 4s\n"
ModelEnd = "exit"


class strategyProcessing:
    def __init__(self):
        global kfcdata
        global kfchome
        global strategyhome
        global kfccli
        self.numbers = 0
        #self.rootdir = '/home/centos/strategyDir'
        self.rootdir = strategyhome
        self.kfchome = kfchome
        self.cli = kfccli
        self.data = kfcdata
        self.dic = {}
        self.processManage = ProcessManage()
        if not os.path.isdir(self.rootdir):
            os.mkdir(self.rootdir)
        dirs = os.listdir(self.rootdir)
        for d in dirs:
            if(os.path.isdir(self.rootdir + '/' + d)):
                dirstrage = self.rootdir + "/" + d
                shName = dirstrage + "/start_" + d + ".sh"
                self.dic[d] = shName

    def getHome(self):
        return self.rootdir
        
    def write(self, fileDataName, fileData, dict, username):
        global processModel
        global tdModel
        global mdModel
        global strategyModel
        global timeModel
        global ModelEnd
        global currntuserId

        processModel = processModel.replace("__KFC_HOME__", self.kfchome)
        processModel = processModel.replace("__KFC_DATA__", self.data)
        dirstrage = self.rootdir + "/" + fileDataName
        if not os.path.isdir(self.rootdir):
            os.mkdir(self.rootdir)
        if not os.path.isdir(dirstrage):
            os.mkdir(dirstrage)
        print(dirstrage)
        f = open(dirstrage + "/" + fileDataName + ".py", "w")
        f.write(fileData)   
        f.close()
        
        shName = dirstrage + "/start_" + fileDataName + ".sh"
        s = open(shName, "w")
        processStr = ""
        #print(dict.size())
        userId = currntuserId
        user = open(userId, "w")
        user.write(username)
        user.close()

        tdlist = []
        mdlist = []
        sdel = strategyModel.replace("__STRATEGY__", fileDataName)
        processStr = sdel + timeModel
        for key, value in dict.items():
            strmol = tdModel.replace("__EXCHANGE__", str(key))
            remol = strmol.replace("__ACCOUNT__", str(value))
            mdel = mdModel.replace("__EXCHANGE__", str(key))
            processStr = processStr + remol + timeModel + mdel + timeModel
            tdlist.append(key)
            mdlist.append(key)
          
        self.processManage.processDic["td"] = tdlist
        self.processManage.processDic["md"] = mdlist
        strategylist = []
        strategylist.append(fileDataName)
        self.processManage.processDic["strategy"] = strategylist
        resumedl = processModel.replace("__ROOT_DIR__", dirstrage)
        prmedl = resumedl.replace("__PROCESS_MODEL__", processStr)
        prmedl = prmedl + ModelEnd
        print(prmedl)
        s.write(prmedl)
        s.close()

        self.dic[fileDataName] = shName

    def startStrategy(self, strategyName):
        cmd = "sh " + self.dic[strategyName]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    
    def stopStrategy(self, strategyName):
        cmd = self.cli + "/kungfu-cli shutdown"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)


    


