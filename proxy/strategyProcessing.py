import os
from re import split
import subprocess
import json
import time
from ProcessManage import ProcessManage
from globalDir import*
from warning import*

tdModel = "nohup $KFC_HOME/kfc -l info td -s __EXCHANGE__ -a __ACCOUNT__ > $KFC_LOG/td__EXCHANGE__.log 2>&1 &\n"
mdModel = "nohup $KFC_HOME/kfc -l info md -s __EXCHANGE__  > $KFC_LOG/md__EXCHANGE__.log 2>&1 &\n"
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
rm -r -f  $KFC_DATA/system/master/\n\
nohup $KFC_HOME/kfc -l info master > $KFC_LOG/master.log 2>&1 &\n\
sleep 4s\n\
nohup $KFC_HOME/kfc -l info ledger > $KFC_LOG/ledger.log 2>&1 &\n\
sleep 4s\n\
__PROCESS_MODEL__"

timeModel = "sleep 4s\n"
ModelEnd = "exit"

warningDir = ""

# supervisor model
svProcessMasterModel="#!/bin/sh\n\
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
rm -r -f  $KFC_DATA/system/master/\n\
nohup $KFC_HOME/kfc -l info master > $KFC_LOG/master.log 2>&1\n\
sleep 4s\n"

svProcessLedgerModel="#!/bin/sh\n\
export KFC_HOME=__KFC_HOME__\n\
export KFC_LOG=__ROOT_DIR__/log\n\
mkdir $KFC_LOG\n\
cd $KFC_HOME\n\
nohup $KFC_HOME/kfc -l info ledger > $KFC_LOG/ledger.log 2>&1\n\
sleep 4s\n"

svProcessStragetyModel="#!/bin/sh\n\
export KFC_HOME=__KFC_HOME__\n\
export KFC_LOG=__ROOT_DIR__/log\n\
mkdir $KFC_LOG\n\
cd $KFC_HOME\n\
nohup $KFC_HOME/kfc -l info strategy  -n test -p $KFC_LOG/../__STRATEGY__.py > $KFC_LOG/test__STRATEGY__log 2>&1\n\
sleep 4s\n"

svProcessTdModel="#!/bin/sh\n\
export KFC_HOME=__KFC_HOME__\n\
export KFC_LOG=__ROOT_DIR__/log\n\
mkdir $KFC_LOG\n\
cd $KFC_HOME\n\
nohup $KFC_HOME/kfc -l info td -s __EXCHANGE__ -a __ACCOUNT__ > $KFC_LOG/td__EXCHANGE__.log 2>&1\n\
sleep 4s\n"

svProcessMdModel="#!/bin/sh\n\
export KFC_HOME=__KFC_HOME__\n\
export KFC_LOG=__ROOT_DIR__/log\n\
mkdir $KFC_LOG\n\
cd $KFC_HOME\n\
nohup $KFC_HOME/kfc -l info md -s __EXCHANGE__  > $KFC_LOG/md__EXCHANGE__.log 2>&1\n\
sleep 4s\n"

svConfigModel="[group:__STRATEGY__]\n\
programs: master,ledger,stragety__TDMD__\n\
\n\
[program:master]\n\
command = sh __ROOT_DIR__/master.sh\n\
priority=1\n\
autostart = false\n\
startsecs = 5\n\
autorestart = true\n\
startretries = 3\n\
redirect_stderr = true\n\
stdout_logfile_maxbytes = 10MB\n\
stdout_logfile_backups = 5\n\
stdout_logfile = /tmp/kungfu_master_stdout.log\n\
\n\
[program:ledger]\n\
command = sh __ROOT_DIR__/ledger.sh\n\
priority=2\n\
autostart = false \n\
startsecs = 5\n\
autorestart = true\n\
startretries = 3\n\
redirect_stderr = true\n\
stdout_logfile_maxbytes = 10MB\n\
stdout_logfile_backups = 5\n\
stdout_logfile = /tmp/kungfu_ledger_stdout.log\n\
\n\
[program:stragety]\n\
command = sh __ROOT_DIR__/__STRATEGY__.sh\n\
priority=3\n\
autostart = false \n\
startsecs = 5\n\
autorestart = true\n\
startretries = 3\n\
redirect_stderr = true\n\
stdout_logfile_maxbytes = 10MB\n\
stdout_logfile_backups = 5\n\
stdout_logfile = /tmp/kungfu_stragety_stdout.log\n\
\n"

svTdConfigModel="[program:td__EXCHANGE__]\n\
command = sh __ROOT_DIR__/td__EXCHANGE__.sh\n\
priority=4\n\
autostart = false \n\
startsecs = 5\n\
autorestart = true\n\
startretries = 3\n\
redirect_stderr = true\n\
stdout_logfile_maxbytes = 10MB\n\
stdout_logfile_backups = 5\n\
stdout_logfile = /tmp/kungfu_td__EXCHANGE___stdout.log\n\
\n"

svMdConfigModel="[program:md__EXCHANGE__]\n\
command = sh __ROOT_DIR__/md__EXCHANGE__.sh\n\
priority=5\n\
autostart = false \n\
startsecs = 5\n\
autorestart = true\n\
startretries = 3\n\
redirect_stderr = true\n\
stdout_logfile_maxbytes = 10MB\n\
stdout_logfile_backups = 5\n\
stdout_logfile = /tmp/kungfu_md__EXCHANGE___stdout.log\n\
\n"

svStartModel="#!/bin/sh\n\
ps -ef|grep supervisord|grep -v grep\n\
if [ $? -eq 0 ];\
then\n\
   echo \"supervisord is good!start strategy...\"\n\
   supervisorctl stop __STRATEGY__:*\n\
   sleep 5s\n\
   ps -ef|grep kfc|grep -v grep\n\
   if [ $? -eq 0 ];\
   then\n\
        echo \"kfc is good!\"\n\
        ps -ef | grep kfc | grep -v grep | awk '{print $2}' | xargs kill -9\n\
   else\
        echo \"kfc is bad!\"\n\
   fi\n\
   supervisorctl reread\n\
   supervisorctl update\n\
   supervisorctl start __STRATEGY__:*\n\
else\
   echo \"supervisord is bad!\"\n\
fi\n\
exit\n"

svStopModel="#!/bin/sh\n\
ps -ef|grep supervisord|grep -v grep\n\
if [ $? -eq 0 ];\
then\n\
   echo \"supervisord is good!stop strategy...\"\n\
   supervisorctl stop __STRATEGY__:*\n\
   sleep 5s\n\
   __KFC_CLI__/kungfu-cli shutdown\n\
else\
   echo \"supervisord is bad!\"\n\
fi\n\
exit\n"


class strategyProcessing:
    def __init__(self):
        global kfcdata
        global kfchome
        global strategyhome
        global kfccli
        global supervisorhome
        self.numbers = 0
        #self.rootdir = '/home/centos/strategyDir'
        self.rootdir = strategyhome
        self.kfchome = kfchome
        self.cli = kfccli
        self.svhome = supervisorhome
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
        if not os.path.isdir(self.svhome):
            os.mkdir(self.svhome)

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
        user.write(username + "_" + fileDataName + "\n")
        user.close()

        tdlist = []
        mdlist = []
        sdel = strategyModel.replace("__STRATEGY__", fileDataName)
        processStr = sdel + timeModel
        for key, value in dict.items():
            if str(key) != 'exbian':
                strmol = tdModel.replace("__EXCHANGE__", str(key))
                remol = strmol.replace("__ACCOUNT__", str(value))
                mdel = mdModel.replace("__EXCHANGE__", str(key))
                processStr = processStr + remol + timeModel + mdel + timeModel
                tdlist.append(key)
                mdlist.append(key)
        for key, value in dict.items():
            if str(key) == 'exbian':
                strmol = tdModel.replace("__EXCHANGE__", str(key))
                remol = strmol.replace("__ACCOUNT__", str(value))
                mdel = mdModel.replace("__EXCHANGE__", str(key))
                processStr = processStr + mdel + timeModel + remol + timeModel
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

    def writewarning(self, strategyName, exchanges, webhook):
        global warningProcess
        global warningcode
        global warninglogfile
        global warningLog
        global warninghead
        global warningInfo
        global processInfofile
        global warningDir

        wpro = warningProcess.replace("__EXCHANGEID__", exchanges)
        wpro = wpro.replace("__STRATEGY__", strategyName)
        webstr = warningcode.replace("__WEBHOOK__", webhook)
        webstr = webstr.replace("__PROCEESSINFOLOCK__", processInfofile)
        listexchange = exchanges.split(',')
        logs = ""
        count = 1
        for log in listexchange:
            logtdfile = warninglogfile.replace("__LOGFILE__", "\"" + self.rootdir + "/log/td" + log + "\"")
            logmdfile = warninglogfile.replace("__LOGFILE__", "\"" + self.rootdir + "log/md" + log + "\"")
            logs = logtdfile + "," + logmdfile
            if count < len(listexchange):
                logs += ","
            count += 1
        logs += "," + warninglogfile.replace("__LOGFILE__", "\"" + self.rootdir + "/log/test" + strategyName + "\"")
        logfiles = warningLog.replace("__LOGFILES__", logs)
        warningcontent = warninghead + warningInfo + wpro + logfiles + webstr
        dirstrage = self.rootdir + "/" + strategyName
        warningDir = dirstrage
        if not os.path.isdir(self.rootdir):
            os.mkdir(self.rootdir)
        if not os.path.isdir(dirstrage):
            os.mkdir(dirstrage)
        
        f = open(dirstrage + "/warning.py", "w")
        f.write(warningcontent)   
        f.close()
        return dirstrage

    def startmonit(self, dirstrage):
        cmd = "sudo python3 " + dirstrage + "/warning.py stop"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        time.sleep(5)
        cmd = "sudo python3 "  + dirstrage + "/warning.py start"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

    def stopmonit(self):
        global warningDir
        cmd = "sudo python3 " + warningDir + "/warning.py stop"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        
    def writeIncludeSv(self, fileDataName, fileData, dict, username):
        global timeModel
        global ModelEnd
        global currntuserId
        global svProcessMasterModel
        global svProcessLedgerModel
        global svProcessStragetyModel
        global svProcessTdModel
        global svProcessMdModel
        global svConfigModel
        global svTdConfigModel
        global svMdConfigModel
        global svStartModel
        global svStopModel

        svpmm_kfc_home = svProcessMasterModel.replace("__KFC_HOME__", self.kfchome)
        svpmm_kfc_home_data = svpmm_kfc_home.replace("__KFC_DATA__", self.data)
        svplm_kfc_home = svProcessLedgerModel.replace("__KFC_HOME__", self.kfchome)
        svpsm_kfc_home = svProcessStragetyModel.replace("__KFC_HOME__", self.kfchome)
        svptdm_kfc_home = svProcessTdModel.replace("__KFC_HOME__", self.kfchome)
        svpmdm_kfc_home = svProcessMdModel.replace("__KFC_HOME__", self.kfchome)
        dirstrage = self.rootdir + "/" + fileDataName
        if not os.path.isdir(self.rootdir):
            os.mkdir(self.rootdir)
        if not os.path.isdir(dirstrage):
            os.mkdir(dirstrage)
        print(dirstrage)
        f = open(dirstrage + "/" + fileDataName + ".py", "w")
        f.write(fileData)   
        f.close()
        
        userId = currntuserId
        user = open(userId, "w")
        user.write(username + "_" + fileDataName + "\n")
        user.close()
        
        shMasterName = dirstrage + "/master.sh"
        masterFile = open(shMasterName, "w")
        svpmm_kfc_home_data_root = svpmm_kfc_home_data.replace("__ROOT_DIR__", dirstrage)
        print("master.sh: {}",svpmm_kfc_home_data_root)
        masterFile.write(svpmm_kfc_home_data_root)
        masterFile.close()
        
        shLedgerName = dirstrage + "ledger.sh"
        ledgerFile = open(shLedgerName, "w")
        svplm_kfc_home_root = svplm_kfc_home.replace("__ROOT_DIR__", dirstrage)
        print("ledger.sh: {}",svplm_kfc_home_root)
        ledgerFile.write(svplm_kfc_home_root)
        ledgerFile.close()
        
        shStragetyName = dirstrage + "/" + fileDataName + ".sh"
        stragetyFile = open(shStragetyName, "w")
        svpsm_kfc_home_root = svpsm_kfc_home.replace("__ROOT_DIR__", dirstrage)
        svpsm_kfc_home_root_strategy = svpsm_kfc_home_root.replace("__STRATEGY__", fileDataName)
        strategylist = []
        strategylist.append(fileDataName)
        self.processManage.processDic["strategy"] = strategylist
        print("stragety.sh: {}",svpsm_kfc_home_root_strategy)
        stragetyFile.write(svpsm_kfc_home_root_strategy)
        stragetyFile.close()
        
        tdlist = []
        mdlist = []
        svptdm_kfc_home_root = svptdm_kfc_home.replace("__ROOT_DIR__", dirstrage)
        svpmdm_kfc_home_root = svpmdm_kfc_home.replace("__ROOT_DIR__", dirstrage)
        svcm_root = svConfigModel.replace("__ROOT_DIR__", dirstrage)
        svcm_root_stragety = svcm_root.replace("__STRATEGY__", fileDataName)
        svtdcm_root = svTdConfigModel.replace("__ROOT_DIR__", dirstrage)
        svmdcm_root = svMdConfigModel.replace("__ROOT_DIR__", dirstrage)
        svProcessConfigStr = svcm_root_stragety
        tdmdStr = ""
        for key, value in dict.items():
            shTdName = dirstrage + "/td" + str(key) + ".sh"            
            strmol = svptdm_kfc_home_root.replace("__EXCHANGE__", str(key))
            remol = strmol.replace("__ACCOUNT__", str(value))            
            tdFile = open(shTdName, "w")
            print("td.sh: {}",remol)
            tdFile.write(remol)
            tdFile.close()
            
            shMdName = dirstrage + "/md" + str(key) + ".sh"
            mdel = svpmdm_kfc_home_root.replace("__EXCHANGE__", str(key))
            mdFile = open(shMdName, "w")
            print("md.sh: {}",mdel)
            mdFile.write(mdel)
            mdFile.close()
            
            contdmol = svtdcm_root.replace("__EXCHANGE__", str(key))
            conmdmol = svmdcm_root.replace("__EXCHANGE__", str(key))
            svProcessConfigStr = svProcessConfigStr + contdmol + conmdmol    
            tdmdStr = tdmdStr + ",td" + str(key) + ",md" + str(key)        
            
            tdlist.append(key)
            mdlist.append(key)
          
        self.processManage.processDic["td"] = tdlist
        self.processManage.processDic["md"] = mdlist
        
        svProcessConfigStr = svProcessConfigStr.replace("__TDMD__", tdmdStr)      
        svConfigName = self.svhome + "/" + fileDataName + ".conf"
        svConfigFile = open(svConfigName, "w")
        print("supervisor config: {}",svProcessConfigStr)
        svConfigFile.write(svProcessConfigStr)
        svConfigFile.close()
        
        shStartName = dirstrage + "/start_" + fileDataName + ".sh"
        startFile = open(shStartName, "w")
        processStartStr = svStartModel.replace("__STRATEGY__", fileDataName)        
        print("start_strategy.sh: {}",processStartStr)
        startFile.write(processStartStr)
        startFile.close()
        
        shStopName = dirstrage + "/stop_" + fileDataName + ".sh"
        stopFile = open(shStopName, "w")
        processStopStr = svStopModel.replace("__STRATEGY__", fileDataName)
        processStopStr = processStopStr.replace("__KFC_CLI__", self.cli)            
        print("stop_strategy.sh: {}",processStopStr)
        stopFile.write(processStopStr)
        stopFile.close()

        self.dic[fileDataName] = shStartName
        self.dic["stop_"+fileDataName] = shStopName

    def startStrategyIncludeSv(self, strategyName):
        cmd = "sh " + self.dic[strategyName]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    
    def stopStrategyIncludeSv(self, strategyName):
        cmd = "sh " + self.dic["stop_"+strategyName]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)


    


