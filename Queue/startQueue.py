import threading
import Services.get_web_news as get_web_news
import Queue.NewsQueue as NewsQueue
from telegram import Bot
import Services.functions as functions

# 获取Telegram Bot的API Token
API_TOKEN = functions.get_bot_token()

# 获取Telegram频道ID
channel_id = functions.get_Channel_id()

# 创建Telegram Bot实例
bot = Bot(token=API_TOKEN)

# 启动消息处理线程
def start_message_processor():
    message_processor = threading.Thread(target=NewsQueue.process_news, args=(bot, channel_id))
    message_processor.start()

# 读取新闻数据
basketball_news = get_web_news.get_hupu_basketball_news()

# 将新闻数据加入队列
NewsQueue.enqueue_news(basketball_news)

# 启动消息处理线程
start_message_processor()