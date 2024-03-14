import Services.functions as functions
import logging, signal, os


# 读取主程序的PID
pid = functions.get_pid()
print(f'pid: {pid}')
signal_number = signal.SIGUSR1  # 使用与主程序中相同的信号

# 读取日志配置
functions.setup_logging()
logger = logging.getLogger()

# 将信号发送给主程序
os.kill(pid, signal_number)
logger.info('进程终止信号已发送给主程序...')
