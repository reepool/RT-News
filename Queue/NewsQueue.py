import Services.functions as functions
import time
import queue


# 获取Telegram Bot的API Token
API_TOKEN = functions.get_bot_token()

# 获取Telegram频道ID
channel_id = functions.get_Channel_id()

# 创建Telegram Bot实例
bot = functions.get_bot_instance()

# 初始化一个空的哈希表来存储新闻数据
news_hash = {}

# 初始化消息队列
news_queue = queue.Queue()

# 将消息加入队列的函数
def enqueue_news(news_data_list):
    for news_data in news_data_list:
        news_queue.put(news_data)
        # print(f"Added news to queue: {news_data}")

# 处理消息并发送到频道的函数
def process_news(bot, channel_id):
    while True:
        try:
            news_data = news_queue.get(timeout=5)  # 从队列中获取新闻数据，设置超时时间
            # 发送新闻到 Telegram 频道
            bot.send_message(chat_id=channel_id, text=news_data[0], parse_mode='html')
            # 将新闻数据存储到哈希表
            news_hash[news_data[1]] = {'time': news_data[2], 'link': news_data[3]}
            # 将新闻数据记录到文件中
            with open('news_log.txt', 'a') as file:
                file.write(f"Title: {news_data[1]}, Time: {news_data[2]}, Link: {news_data[3]}\n")
            news_queue.task_done()  # 标记消息处理完成
            time.sleep(2)  # 控制发送速率为每2秒发送一条消息
        except queue.Empty:
            time.sleep(1)  # 队列为空时等待一段时间



