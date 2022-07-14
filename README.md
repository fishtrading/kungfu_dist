# kungfu_dist
proxy部署于交易服务器上，用于和策略管理服务器通信。从websocket连接接收并执行策略发布，启动/停止策略等操作命令。

## 安装方法
* pip3 install -r requirements.txt

## 配置
* 修改配置文件 ./proxy/globalDir.py 中的文件目录配置

## 运行方法
* cd ./proxy
* python3 app.py 前台调试模式运行，退出登录程序中止
* nohup python3 app.py > nohup.out 2>&1 & 后台模式运行
