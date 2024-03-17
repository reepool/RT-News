#!/bin/bash

# 定义日志文件路径
LOG_FILE=$(pwd)/log/news_crawl.log

# 启动程序
start_program() {
  echo "启动basketball进程..."
  nohup /home/python/RT-News/start.sh > $LOG_FILE 2>&1 &
}

# 检查进程是否已经在运行
check_process() {
  if [ -f /home/python/RT-News/log/process.pid ]; then
    pid=$(cat /home/python/RT-News/log/process.pid)
    if ps -p $pid > /dev/null; then
       return 0
    else
       return 1
    fi
  else
    return 1
  fi
}

# 启动过程
start_process() {
  check_process
  if [ $? -eq 1 ]; then  # 检查最后一条命令的退出状态
    start_program
    sleep 2
    
    # 尝试多次启动进程，确保进程被启动
    local retries=5
    for ((i=1; i<=retries; i++)); do
      check_process
      if [ $? -eq 0 ]; then
        echo "进程已启动"
        return 0
      else
        echo "尝试再次启动进程（尝试次数 $i）"
        start_program
        sleep 2
      fi
    done
    echo "程序已成功启动"
    return 0
  else
    echo "进程已经在运行"
    return 0
  fi
}

# 停止程序
stop_program() {
  echo "停止basketball进程..."
  check_process
  if [ $? -eq 0 ]; then  # 检查最后一条命令的退出状态
    /home/python/RT-News/terminate.sh
    sleep 8
    
    # 尝试多次停止进程，确保进程被终止
    local retries=5
    for ((i=1; i<=retries; i++)); do
      check_process
      if [ $? -eq 1 ]; then
        echo "进程已停止"
        return 0
      else
        echo "尝试再次停止进程（尝试次数 $i）"
        /home/python/RT-News/terminate.sh
        sleep 5
      fi
    done

    echo "程序仍未停止"
    return 1
  else
    echo "进程并未运行"
    return 0
  fi
}

# 停止过程
stop_process() {
  stop_program
}

# 重启过程
restart_process() {
  stop_process
  start_process
}

# 主程序
case "$1" in
  start)
    start_process
    ;;
  stop)
    stop_process
    ;;
  restart)
    restart_process
    ;;
  *)
    echo "用法: $0 {start|stop|restart}"
    exit 1
esac

exit 0
