import os


class logManage:
    def __init__(self, path):
        self.rootPath = path
        self.dic = {}
        self.logtype = ["master", "ledger", "td", "md", "strategy"]
    
    def createdependlog(self, strategyName):
        if not self.dic.__contains__(strategyName):
            logroot = self.rootPath + "/" + strategyName
            masterlog = logroot + "/master.log"
            ledgerlog = logroot + "/ledger.log"
            mdlog = logroot + "/md.log" 
            tdlog = logroot + "/td.log"
            strategylog = logroot + "/" + strategyName
            self.dic[strategyName] = [masterlog, ledgerlog, mdlog, tdlog, strategylog]

    def checklog(self, logname):
        if not os.path.exists(logname):
            return False
        return True

    def sendlog(self, client, strategyName, logtype):
        for item in self.dic[strategyName]:
            if not self.checklog(item):
                return item
            else:
                if(item.find(logtype)):
                    f = os.open(item, "r")
                    logcontent = f.read()
                    f.close()
                    client.send("{\"op\":\"log\",\"content\":" + logcontent + "}")
        
        return "success"


