#!/bin/bash 
cd /root/proxy
# export CLI=/home/kungfu2.3.6/kungfu2/app/build/app/linux-unpacked/resources/kungfu-cli
# export CLI=/home/kungfu2/app/build/app/linux-unpacked/resources/kungfu-cli
export CLI=/home/centos/kungfu2/app/build/app/linux-unpacked/resources/kungfu-cli
cat /home/userId |  while read line
do
   mkdir `date +%y%m%d`$line
   date=`date +%y%m%d`
   echo $line_$date
   expect << -EOF
   set timeout 5
   spawn $CLI/kungfu-cli export
   expect "*Input date*"
   send "\r"
   expect "Input trading"
   # send /root/newproxy/$date$line\r
   send /home/centos/newproxy/$date$line\r
expect eof
-EOF
   # tar -cvf $date$line.tar /root/newproxy/$date$line
   tar -cvf $date$line.tar /home/centos/newproxy/$date$line
   sleep 200
   python3.6 uploadTrade.py $date$line.tar
done
