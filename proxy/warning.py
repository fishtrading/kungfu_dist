#!/usr/bin/env python
# -*- coding: utf-8 -*-
warninghead = "import os\n\
import sys\n\
import logging\n\
from logging.handlers import RotatingFileHandler\n\
import time\n\
import threading\n\
import subprocess\n\
from datetime import datetime\n\
from datetime import timedelta\n\
import requests\n\
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY\n\
import re\n\
import json\n"
# from wxWork import GroupRobot as wxrobot
warningInfo = "_LOG_INFO = {\n\
    \"log_level\": logging.INFO,\n\
    \"log_format\": '%(asctime)-15s %(levelname)s %(lineno)s %(message)s',\n\
    \"log_file\": '/tmp/daemon.log',\n\
    \"log_max_size\": 100000000,\n\
    \"log_backup\": 7,\n\
}\n"

warningProcess = "_Process_Monit = {\"master\": [\"master\"], \"ledger\": [\"ledger\"], \"td\": [\"__EXCHANGEID__\"], \"md\": [\"__EXCHANGEID__\"], \"strategy\": [\"__STRATEGY__\"]}\n" 

warninglogfile = "__LOGFILE__: [\n\
        __LOGFILE__,\n\
        0,\n\
        False,\n\
        [re.compile(\"ERROR\", re.IGNORECASE)]\n\
    ]"

warningLog = "_PID_FILE = '/tmp/daemon.pid'\n\
_DEBUG = False\n\
_NTP_SERVER_ADDRESS = 'ntpupdate.tencentyun.com' # 时间服务器地址\n\
_NTP_UPDATE_TIME = 300\n\
_DATA_DIR = '/opt/daemon/data'  # 系统信息存储目录\n\
_SS_CHECK_INTERVAL = 60\n\
_PS_CHECK_INTERVAL = 60\n\
_DATA_RETAIN_DAYS = 7\n\
_SS_DIR = \"tcp_status\"\n\
_PS_DIR = \"ps_status\"\n\
_monitor_dict = {\n\
    __LOGFILES__\n\
}\n"
# 设置微信告警机器人webhook
warningcode ="_alert_webhook = \"__WEBHOOK__\"\n\
_hostname = subprocess.getstatusoutput(\"hostname\")[1]\n\
_first_start = True\n\
\n\
class EventHandler(ProcessEvent):\n\
    def __init__(self, logger):\n\
        global _monitor_dict\n\
        ProcessEvent.__init__(self)\n\
        self._logger = logger\n\
        self._path_list = [v[0] for v in _monitor_dict.values()]\n\
        self._logger.info(\"init Eventhandler\")\n\
\n\
    def process_IN_DELETE(self, event):\n\
        global _monitor_dict\n\
        file_path = event.path\n\
        if file_path in self._path_list:\n\
            _monitor_dict[file_path][2] = True\n\
            self._logger.info(\"Delete file:%s\" % file_path)\n\
\n\
    def process_IN_CREATE(self, event):\n\
        global _hostname, _monitor_dict\n\
        file_path = event.path.replace('$', '')\n\
        self._logger.info(\"Create file:%s\" % file_path)\n\
        if file_path in self._path_list:\n\
            _monitor_dict[file_path][1] = 0\n\
            self._logger.info(\"Create file: {0}\".format(file_path))\n\
            try:\n\
                with open(file_path, 'r') as log_file:\n\
                    while True:\n\
                        log_file.seek(_monitor_dict[file_path][1])\n\
                        line = log_file.readline().replace('\\n\', '')\n\
                        for m in _monitor_dict[file_path][3]:\n\
                            if re.search(m, line):\n\
                                line = line+'   --- '+_hostname+\"---\"+file_path\n\
                                send_message(\n\
                                    line, self._logger)\n\
                        if not line:\n\
                            break\n\
                        else:\n\
                            _monitor_dict[file_path][1] = log_file.tell()\n\
            except Exception as e:\n\
                self._logger.error(str(e))\n\
\n\
    def process_IN_MODIFY(self, event):\n\
        global _hostname, _monitor_dict\n\
        #self._logger.info(\"file_name: \"+event.name+\" \"+event.path)\n\
        file_path = event.path.replace('$', '')\n\
        if file_path in self._path_list:\n\
            #self._logger.info('Modify file: %s' % file_path)\n\
            if _monitor_dict[file_path][2]:\n\
                _monitor_dict[file_path][2] = False\n\
                _monitor_dict[file_path][1] = 0\n\
            try:\n\
                self._logger.info(\"start read {1} on {0}\".format(\n\
                    str(_monitor_dict[file_path][1]), file_path))\n\
                with open(file_path, 'r') as log_file:\n\
                    while True:\n\
                        log_file.seek(_monitor_dict[file_path][1])\n\
                        line = log_file.readline().replace('\\n\', '')\n\
                        for m in _monitor_dict[file_path][3]:\n\
                            if re.search(m, line):\n\
                                line = line + '---'+_hostname+\"---\"+file_path\n\
                                send_message(\n\
                                    line, self._logger)\n\
                        if not line:\n\
                            break\n\
                        else:\n\
                            _monitor_dict[file_path][1] = log_file.tell()\n\
            except Exception as e:\n\
                self._logger.error(str(e))\n\
\n\
def start_monitor(logger, path):\n\
    wm = WatchManager()\n\
    mask = IN_DELETE | IN_CREATE | IN_MODIFY\n\
    notifier = Notifier(wm, EventHandler(logger))\n\
    wm.add_watch(path, mask, auto_add=True, rec=True)\n\
    while True:\n\
        try:\n\
            notifier.process_events()\n\
            if notifier.check_events():\n\
                notifier.read_events()\n\
        except Exception as e:\n\
            logger.error(str(e))\n\
\n\
def monitor_file(logger):\n\
    global _first_run, _monitor_dict\n\
    path_list = [v[0] for k, v in _monitor_dict.items()]\n\
    logger.info(str(path_list))\n\
    logger.info(\"start log monitor thread  monitor file: \"+str(path_list))\n\
    if _first_start:\n\
        _first_run = False\n\
        msg = 'start location \\n'\n\
        for file_path in path_list:\n\
            if os.path.exists(file_path):\n\
                total_chars_count = subprocess.getstatusoutput(\n\
                    \"wc -m \"+file_path+\"|awk '{print $1}'\")[1]\n\
                pointer = int(total_chars_count) if int(\n\
                    total_chars_count) > 0 else 0\n\
                _monitor_dict[file_path][1] = pointer\n\
                msg = msg+\" \" + \\\n\
                    file_path+\"  pointer: \"+str(pointer)+'\\n\'\n\
        logger.info(msg)\n\
    monitor_threads = []\n\
    for path in path_list:\n\
        monitor_threads.append(threading.Thread(\n\
            target=start_monitor, args=(logger, path)))\n\
\n\
    def threads_join(threads):\n\
        for thread in threads:\n\
            while True:\n\
                if thread.isAlive():\n\
                    time.sleep(3)\n\
                else:\n\
                    break\n\
\n\
    for thread in monitor_threads:\n\
        thread.setDaemon(True)\n\
        thread.start()\n\
    threads_join(monitor_threads)\n\
\n\
def send_message(mess, logger=None, url=None):\n\
    global _alert_webhook\n\
    if url:\n\
        web_url = url\n\
    else:\n\
        web_url = _alert_webhook\n\
    mess = mess\n\
    data = {\"msgtype\": \"text\", \"text\": {\"content\": mess}}\n\
    headers = {\"Content-Type\": \"application/json\"}\n\
    try:\n\
        requests.post(web_url, headers=headers, data=json.dumps(data))\n\
    except Exception as e:\n\
        if logger is not None:\n\
            logger.info(str(e))\n\
\n\
def sync_server_datetime(logger):\n\
    global _NTP_SERVER_ADDRESS, _NTP_UPDATE_TIME\n\
    if not os.path.exists('/usr/sbin/ntpdate'):\n\
        cmd = False\n\
        logger.info('/usr/sbin/ntpdate commands do not exists . skip this task')\n\
    else:\n\
        cmd = '/usr/sbin/ntpdate  -u  {0}'.format(_NTP_SERVER_ADDRESS)\n\
    if cmd:\n\
        while True:\n\
            res, output = subprocess.getstatusoutput(cmd)\n\
            logger.info(output)\n\
            time.sleep(_NTP_UPDATE_TIME)\n\
\n\
def clean_old_data(logger, type_dir):\n\
    global _DATA_RETAIN_DAYS, _DATA_DIR\n\
    remove_day = datetime.strftime(\n\
        datetime.now()+timedelta(days=-_DATA_RETAIN_DAYS), \"%Y-%m-%d\")\n\
    remove_dir = os.path.join(os.path.join(_DATA_DIR, type_dir), remove_day)\n\
    if os.path.exists(remove_dir) and remove_dir not in [\"/\", \"/.\", \"./.\", \"/boot\", \"/etc\"]:\n\
        cmd = \"rm -rf {0}\".format(remove_dir)\n\
        os.system(cmd)\n\
        logger.info(\"clean data dir: {0}\".format(remove_dir))\n\
\n\
def tcp_status_by_ss(logger):\n\
    global _DATA_DIR, _SS_CHECK_INTERVAL, _SS_DIR\n\
    ss_dir = os.path.join(_DATA_DIR, _SS_DIR)\n\
    while True:\n\
        output_dir = os.path.join(\n\
            ss_dir, datetime.strftime(datetime.now(), '%Y-%m-%d'))\n\
        if not os.path.exists(output_dir):\n\
            os.system('mkdir -p {0}'.format(output_dir))\n\
        output_file = os.path.join(\n\
            output_dir, datetime.strftime(datetime.now(), '%H%M%S'))\n\
        cmd = '/usr/sbin/ss -ant4 &> {0}'.format(output_file)\n\
        result = os.system(cmd)\n\
        logger.info(\n\
            \"tcp_status_by_ss method run result: {0}\".format(str(result)))\n\
        clean_old_data(logger, _SS_DIR)\n\
        time.sleep(_SS_CHECK_INTERVAL)\n\
def watchProcess():\n\
    global _Process_Monit\n\
    pro = {}\n\
    prostr = \"\"\n\
    processfile = \"__PROCEESSINFOLOCK__\"\n\
    #if os.path.exists(processfile) and os.path.isfile(processfile):\n\
    # os.remove(processfile)\n\
    try:\n\
        os.system(\"ps -ef | grep kfc | grep -v grep >%s\" % processfile)\n\
        file = open(processfile, \"r\")\n\
        prostr = file.read()\n\
        file.close\n\
    except Exception:\n\
        print(\"Exception\")\n\
    listpro = []\n\
    itpro = []\n\
    for key, value in _Process_Monit.items():\n\
        if prostr.find(key) == -1:\n\
            listpro.append(key)\n\
        else:\n\
            for item in value:\n\
                if prostr.find(item) == -1:\n\
                    itpro.append(item + \"_\" + key)\n\
    if len(listpro):\n\
        pro[\"mainpro\"] = listpro\n\
    if len(itpro):\n\
        pro[\"branch\"] = itpro\n\
    if pro == {}:\n\
        return True \n\
    send_message(\"process is stroped[error]->\" + str(pro))\n\
    return False\n\
\n\
def process_status_by_ps(logger):\n\
    global _DATA_DIR, _PS_CHECK_INTERVAL, _PS_DIR\n\
    ps_dir = os.path.join(_DATA_DIR, _PS_DIR)\n\
    while True:\n\
        output_dir = os.path.join(\n\
            ps_dir, datetime.strftime(datetime.now(), '%Y-%m-%d'))\n\
        if not os.path.exists(output_dir):\n\
            os.system('mkdir -p {0}'.format(output_dir))\n\
        output_file = os.path.join(\n\
            output_dir, datetime.strftime(datetime.now(), '%H%M%S'))\n\
        cmd = '/bin/top -b -c -n 1 &> {0} && /usr/bin/ps aux &>> {1}'.format(\n\
            output_file, output_file)\n\
        result = os.system(cmd)\n\
        logger.info(\n\
            \"ps_status_by_ss method run result: {0}\".format(str(result)))\n\
        clean_old_data(logger, _PS_DIR)\n\
        watchProcess()\n\
        time.sleep(_PS_CHECK_INTERVAL)\n\
\n\
# callbacks 填入编写的监控函数名\n\
CALL_BACKS = [  #sync_server_datetime,\n\
                #tcp_status_by_ss,\n\
                process_status_by_ps,\n\
                monitor_file\n\
            ]\n\
# 检测时间间隔\n\
CHECK_INTERNAL = 60\n\
\n\
\n\
class Daemon(object):\n\
    def __init__(self):\n\
        self._pid_file = _PID_FILE\n\
        self._std_in_file = '/dev/null'\n\
        self._std_out_file = '/dev/null'\n\
        self._std_err_file = _LOG_INFO.get('log_file', '/var/log/agent.log')\n\
        self.logger_ok = False\n\
        self.logger = None\n\
\n\
    def set_logger(self):\n\
        global _LOG_INFO, _DEBUG\n\
        logging.basicConfig(level=logging.DEBUG, filename='/dev/null')\n\
        Logger = logging.getLogger('Agent')\n\
        log_level = _LOG_INFO.get('log_level', logging.INFO)\n\
        log_format = logging.Formatter(_LOG_INFO.get('log_format', ''))\n\
        log_file = _LOG_INFO.get('log_file', '/tmp/agent.log')\n\
        if _DEBUG:\n\
            handler = logging.StreamHandler()\n\
        else:\n\
            log_max_size = _LOG_INFO.get('log_max_size', 100000)\n\
            log_backup = _LOG_INFO.get('log_backup', 7)\n\
            log_folder = os.path.dirname(_LOG_INFO.get('log_file'))\n\
            if os.path.exists(log_folder):\n\
                os.system('mkdir -p {0}'.format(log_folder))\n\
            handler = RotatingFileHandler(\n\
                log_file, 'a', log_max_size, log_backup)\n\
        handler.setLevel(log_level)\n\
        handler.setFormatter(log_format)\n\
        Logger.addHandler(handler)\n\
        if not self.logger:\n\
            self.logger = logging.getLogger('Agent')\n\
\n\
    def init_logger(self):\n\
        if not self.logger_ok:\n\
            self.logger_ok = True\n\
            self.set_logger()\n\
\n\
    def daemonize(self):\n\
        try:\n\
            pid = os.fork()\n\
            if pid > 0:\n\
                sys.exit(0)\n\
        except OSError as e:\n\
            self.logger.error(str(e))\n\
        os.setsid()\n\
        os.umask(0)\n\
        try:\n\
            pid = os.fork()\n\
            if pid > 0:\n\
                sys.exit(0)\n\
        except OSError as e:\n\
            self.logger.error(str(e))\n\
        for f in sys.stdout, sys.stderr:\n\
            f.flush()\n\
        si = open(self._std_in_file, 'r')\n\
        so = open(self._std_out_file, 'a+')\n\
        se = open(self._std_err_file, 'a+')\n\
        os.dup2(si.fileno(), sys.stdin.fileno())\n\
        os.dup2(so.fileno(), sys.stdout.fileno())\n\
        os.dup2(se.fileno(), sys.stderr.fileno())\n\
        import atexit\n\
        atexit.register(self.del_pidfile)\n\
        pid = str(os.getpid())\n\
        self.logger.info(str(pid))\n\
        if not os.path.exists(os.path.dirname(self._pid_file)):\n\
            os.makedirs(os.path.dirname(self._pid_file))\n\
        with open(self._pid_file, 'w') as f:\n\
            f.write(pid)\n\
\n\
    def start(self):\n\
        if not _DEBUG:\n\
            if os.path.exists(self._pid_file):\n\
                self.logger.info('agent is running ?')\n\
                sys.exit(1)\n\
            self.daemonize()\n\
            self.logger.info('start agent success')\n\
        else:\n\
            self.logger.info('start agent in debug mode')\n\
        worker = Worker(CALL_BACKS)\n\
        worker.start_loop()\n\
\n\
    def stop(self):\n\
        if not os.path.exists(self._pid_file):\n\
            self.logger.error('the pid file is not exists! stop fail')\n\
            sys.exit(1)\n\
        pid = None\n\
        with open(self._pid_file) as f:\n\
            pid = int(f.readline())\n\
        if pid:\n\
            os.system('kill -9 {0}'.format(str(pid)))\n\
            self.logger.info('Stop publisher process Success')\n\
        try:\n\
            os.remove(self._pid_file)\n\
        except Exception as e:\n\
            self.logger.info(str(e))\n\
\n\
    def del_pidfile(self):\n\
        os.remove(self._pid_file)\n\
\n\
    def restart(self):\n\
        self.stop()\n\
        time.sleep(1)\n\
        self.start()\n\
\n\
    def parse_input(self, opt):\n\
        if opt == 'start':\n\
            self.start()\n\
        elif opt == 'stop':\n\
            self.stop()\n\
        elif opt == 'restart':\n\
            self.restart()\n\
        else:\n\
            self.logger.error(\n\
                'bad params ,exsample: ./daemon  start|stop|restart')\n\
            sys.exit(1)\n\
\n\
class Worker(object):\n\
    def __init__(self, callbacks=None, internal=CHECK_INTERNAL):\n\
        self._callbacks = callbacks\n\
        self.logger = logging.getLogger('Agent')\n\
        self._internal = internal\n\
\n\
    def start_loop(self):\n\
        # while True:\n\
        callbacks = self._callbacks\n\
        threads = []\n\
        if callbacks:\n\
            for callback in callbacks:\n\
                threads.append(threading.Thread(\n\
                    target=callback, args=(self.logger,)))\n\
            for t in threads:\n\
                try:\n\
                    t.start()\n\
                except Exception as e:\n\
                    self.logger(str(e))\n\
                    threads.remove(t)\n\
            for t in threads:\n\
                t.join(timeout=600)\n\
\n\
if __name__ == '__main__':\n\
    if len(sys.argv) == 2:\n\
        daemon = Daemon()\n\
        daemon.init_logger()\n\
        daemon.parse_input(sys.argv[1])\n\
    else:\n\
        print('bad params')"