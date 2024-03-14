import Services.functions as functions
import Services.BotService as BotService
import logging, asyncio, sys, signal

# 获取日志配置
functions.setup_logging()
logger = logging.getLogger()

# 记录进程pid
functions.record_pid()

# 将自定义的异常处理函数注册为全局的未捕获异常处理钩子
sys.excepthook = functions.handle_uncaught_exception

# 定义一个自定义信号，用于终止程序
CUSTOM_SIGNAL = signal.SIGUSR1

# 定义一个全局变量，用于标志主程序是否需要循环运行
should_loop = True

# 定义一个自定义信号处理函数
def custom_signal_handler(sig, frame):
    global should_loop
    logger.info(f'接收到信号: {sig}')
    should_loop = False
    if BotService.BotRunner.instance is not None: # 如果BotRunner实例不为空
        asyncio.create_task(BotService.BotRunner.instance.stop()) # 调用BotRunner类的stop_instance()方法停止进程
    logger.info('接收到终止进程信号，调用BotRunner类的stop_instance()方法停止进程')

# 绑定信号处理函数, 用于终止程序
signal.signal(CUSTOM_SIGNAL, custom_signal_handler)

async def main():
    global should_loop
    restart_interval = functions.get_restart_interval()
    while should_loop:
        try:
            bot_runner = BotService.BotRunner()
            await bot_runner.run()
        except KeyboardInterrupt:
            logger.info("收到 KeyboardInterrupt，程序终止。")
            should_loop = False
        except Exception as e:
            logger.error(f"遇到错误，准备重启: {e}")
            if not should_loop:
                break
            await asyncio.sleep(restart_interval)
        finally:
            if BotService.BotRunner.instance is not None:
                await BotService.BotRunner.instance.stop()
        if not should_loop:
            break

    

if __name__ == "__main__":
    asyncio.run(main())