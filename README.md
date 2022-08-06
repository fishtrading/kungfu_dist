# kungfu初始安装
* 访问kungfu软件安装包发布区 https://github.com/fishtrading/kungfu_dist/releases   找到最新的下载链接，比如：https://github.com/fishtrading/kungfu_dist/releases/download/v2.3/kungfu-2.3.8.tar.gz
* 登录linux服务器，推荐操作系统：centos 7.9。
  * 下载kungfu安装包，wget https://.../kungfu-2.3.8.tar.gz
  * 解压缩到/opt/kungfu/ 目录
  * 编辑/etc/profile，文件末尾添加一行。“export LC_ALL=en_US.utf8”
  * yum install libicu
* 执行以下命令
  * /opt/kungfu/kfc/kfc migrate
  * /opt/kungfu/cli/kungfu-cli monit
* 进入monit界面后按Ctrl+c退出，完成初始配置工作。

# 配置交易柜台
* 访问kungfu软件安装包发布区 https://github.com/fishtrading/kungfu_dist/releases  找到最新交易柜台软件下载链接，比如：https://github.com/fishtrading/kungfu_dist/releases/download/v2.3/kfext_exbian-v1.0.1.tgz
* 登录kungfu服务器。
  * 进入目录 /opt/kungfu/kfc/kungfu_extensions
  * 下载软件包 wget https://.../kfext_exbian-v1.0.1.tgz
  * 解压缩下载软件包 tar xvfz kfext_exbian-v1.0.1.tgz
  * 解压的默认文件夹是package，修改为柜台软件名称 mv package exbian
* 执行/opt/kungfu/cli/kungfu-cli ext -l，如果交易柜台是否安装正确，应该在列表里看到exbian

# 添加修改交易账号
* 新增账号 /opt/kungfu/cli/kungfu-cli add
  * 选择md或td
  * 选择交易柜台
  * 输入账号配置信息
* 修改账号 /opt/kungfu/cli/kungfu-cli update
  * 选择账号
  * 修改账号配置信息
  * 修改柜台配置文件。在/opt/kungfu/kfc/kungfu_extentions/

# proxy
proxy部署于交易服务器上，用于和策略管理服务器通信。从websocket连接接收并执行策略发布，启动/停止策略等操作命令。

## 安装方法
* pip3 install -r requirements.txt

## 配置
* 修改配置文件 ./proxy/globalDir.py 中的文件目录配置

## 运行方法
* cd ./proxy
* python3 app.py 前台调试模式运行，退出登录程序中止
* nohup python3 app.py > nohup.out 2>&1 & 后台模式运行

# 编译注意问题
* 安装软件包 yum install -y boost169 boost169-devel
* 设置环境变量
  * export BOOST_INCLUDEDIR=/usr/include/boost169
  * export BOOST_LIBRARYDIR=/usr/lib64/boost169
* 编译动作
  * yarn install
  * yarn build
  * yarn build-cli
  * yarn workspace kfext_exbian build
