import os
import mmh3
import sqlite3
import json

class accountManage:
    def __init__(self):
        self.accountdic = {}
        self.conn = sqlite3.connect('config.db')
        self.cursor = self.conn.cursor()

    def has_locationuid(self, uidstr):
        return mmh3.hash(uidstr, 42) 
    
    def insertConfig(self, category, group, value):
        mdOrtd = ""
        if category == "md":
            mdOrtd = 0
        elif category == "td":
            mdOrtd == 1
        userid = value["user_id"] 
                                                           #需要处理一下异常
        location_uidStr = mdOrtd + "/" + group + "/" + userid + "/live"
        location_uid = self.has_locationuid(location_uidStr)

        sqlStr = "insert into Config (location_uid, category, group, name, mode, value) values({}, {}, {}, {}, {},{})".format(location_uid, mdOrtd, group, userid, "live", vjson)
        self.cursor.execute(sqlStr)
        self.conn.commit()
        return 
    
    def removeConfig(self, category, group, uid):
        sqlStr = "delete from Config where category = {} and group = {} and name = {}".format(category, group, uid)
        self.cursor.execute(sqlStr) 
        self.conn.commit()
        return
    
 