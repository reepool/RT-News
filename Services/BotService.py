import Services.functions as functions
import Services.process_tg_news as process_tg_news
import asyncio

# 生成一个日志实例
logger = functions.setup_logging()

# 创建Telegthon bot实例的函数
async def create_telethon_instance():
    bot_thon = await functions.get_telethon_bot_instance()
    return bot_thon

class BotRunner:
    instance = None # 类变量，用于保存BotRunner实例

    def __init__(self):
        self.running_status = True # 运行标志设置为True
        BotRunner.instance = self # 将BotRunner实例保存到类变量中
        self.bot_thon = None # 用于保存telethon bot实例

    # 定义一个类方法，用于停止BotRunner实例
    @classmethod
    def stop_instance(cls):
        if cls.instance is not None:
            cls.instance.stop()

    async def create_telethon_instance(self):
        logger.info("开始创建telethon bot实例")
        self.bot_thon = await create_telethon_instance()

    async def run(self):
        await self.create_telethon_instance()
        # 获取tg新闻来源频道名称
        # channel_news_name = functions.get_tg_news_channel_name()
        channel_news_names = functions.get_all_tg_news_channel_names()
        # 获取待上传的tg频道名称
        channel_dest_name = functions.get_Channel_id()
        logger.info(f"共有{len(channel_news_names)}个新闻频道的信息需要处理")
        while self.running_status:
            try:
                # 获取和处理频道消息
                for channel_news_name in channel_news_names:
                    logger.info(f"开始获取来源频道{channel_news_name}的消息")
                    message_content = await process_tg_news.get_channel_messages(self.bot_thon, channel_news_name)
                    if message_content is None:
                        error_message = f"获取频道{channel_news_name}的消息失败"
                        print(error_message)
                        continue
                    else:
                        print(f"获取{channel_news_name}频道的消息的工作已完成")
                    # 翻译和处理频道消息
                    logger.info(f"开始翻译和处理获取的消息")
                    translated_messages = await process_tg_news.handel_channel_messages(self.bot_thon, message_content, channel_news_name)
                    if translated_messages is None:
                        error_message = f"翻译和处理{channel_news_name}消息失败"
                        print(error_message)
                        continue
                    else:
                        print(f"翻译和处理{channel_news_name}频道消息的工作已完成")
                    # 上传处理好的消息到频道
                    logger.info(f"开始上传翻译后的{channel_news_name}消息到频道")
                    news_count = await process_tg_news.send_translated_messages_to_channel(self.bot_thon, channel_dest_name, translated_messages, channel_news_name)
                    if news_count is None:
                        logger.error(f"上传翻译后的{channel_news_name}消息到频道失败")
                        continue
                    elif news_count == 0:
                        print(f"{channel_news_name}频道没有新的消息需要上传")
                        logger.info(f"{channel_news_name}频道没有新的消息需要上传")
                        
                    print(f"成功上传翻译后的{channel_news_name}频道消息: 共{news_count}条")
                    logger.info(f"成功上传翻译后的{channel_news_name}频道消息: 共{news_count}条")

            except Exception as e:
                error_message = f"获取频道{channel_news_name}消息失败: {e}"
                logger.error(error_message)
                await functions.send_error_message_async(self.bot_thon, error_message)
                message_content = None

            # 每隔一段时间检查一次running_status的状态，如果为False则退出循环，否则持续等待，直到触发crawl_interval_time的等待时间
            for _ in range(0, functions.get_crawl_interval_time()*60, 10):  # 每10秒检查一次running_status的状态
                if not self.running_status:
                    break
                await asyncio.sleep(10)
            # await asyncio.sleep(functions.get_crawl_interval_time()*60)

    async def stop(self):
        logger.info("准备释放所有资源并退出程序...")
        self.running_status = False
        # 循环结束后清理资源并退出程序
        if self.bot_thon:
            await self.bot_thon.disconnect()
            logger.info("Telegram-telethon bot连接断开")
