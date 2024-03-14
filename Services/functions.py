import configparser
import re, pickle, traceback
import os, logging, hashlib
import telegram, json
from telethon import TelegramClient
from telethon.tl.types import MessageMediaWebPage
from telethon.errors import FloodError
import asyncio


# 定义读取配置文件内变量的函数
def read_config(section, key):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config.get(section, key)

# 定义读取系统日志文件名的函数
def get_system_log_file_name():
    system_log_file_name = read_config('file', 'syslog_file_name')
    dir_path = read_config('file', 'dir_path')
    file = os.path.join(dir_path, system_log_file_name)   
    return file

# 定义日志记录的函数
def setup_logging():
    filename = get_system_log_file_name()
    logging.basicConfig(filename=filename, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

setup_logging()
logger = logging.getLogger()


# 定义一个读取进程PID并记录到文件中的函数
def record_pid():
    # 读取记录PID的文件名
    pure_pid_file_name = read_config('file', 'pid_file_name')
    dir_path = read_config('file', 'dir_path')
    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    pid_file_name = os.path.join(dir_path, pure_pid_file_name)
    # 获取当前进程的PID
    pid = os.getpid()
    # 将PID写入文件
    with open(pid_file_name, 'w') as file:
        file.write(str(pid))
        # 记录日志到系统日志文件
        logger = logging.getLogger()
        logger.info(f'PID: {pid} has been recorded to file: {pid_file_name}')

# 定义一个从记录PID的文件中读取PID的函数
def get_pid():
    # 读取记录PID的文件名
    pure_pid_file_name = read_config('file', 'pid_file_name')
    dir_path = read_config('file', 'dir_path')
    pid_file_name = os.path.join(dir_path, pure_pid_file_name)
    # 检查文件是否存在，如果不存在这返回0
    if not os.path.exists(pid_file_name):
        logger.error(f"PID文件不存在: {pid_file_name}")
        return 0
    # 从文件中读取PID
    with open(pid_file_name, 'r') as file:
        return int(file.read())

# 定义读取配置文件中的Telegram Bot Token的函数
def get_bot_token():
    bot_token = read_config('Telegram', 'token')
    return bot_token

# 定义读取配置文件中的Telegram Chat ID 的函数
def get_chat_id():
    chat_id = read_config('Telegram', 'chat_id')
    return chat_id

# 定义读取配置文件中的Telegram Channel ID 的函数
def get_Channel_id():
    channel_id = read_config('Telegram', 'channel_id')
    return channel_id

# 定义读取配置文件中TG API id和hash，以及会话名的函数
def get_tg_api_id_hash():
    tg_api_id = read_config('Telegram', 'api_id')
    tg_api_hash = read_config('Telegram', 'api_hash')
    session_name = read_config('Telegram', 'session_name')
    return (tg_api_id, tg_api_hash, session_name)

# 定义读取配置文件中一次获取的新闻条数的函数
def get_msg_number():
    msg_number = read_config('Telegram', 'msg_number_2get')
    return int(msg_number)

# 读取配置文件中的翻译API的URL
def get_translation_api_url():
    translation_api_url = read_config('Translations', 'translator')
    return translation_api_url

# 读取配置文件中的翻译源语言
def get_source_lang():
    from_lang = read_config('Translations', 'from_lang')
    return from_lang

# 读取配置文件中的翻译目标语言
def get_target_lang():
    to_lang = read_config('Translations', 'to_lang')
    return to_lang

# 定义读取配置文件中的重传次数的函数
def get_transfer_retry_times():
    transfer_retry_times = read_config('Transmission', 'max_transfer_retries')
    return int(transfer_retry_times)

# 计算变量的哈希值
def get_hash(variable):
    return hashlib.md5(str(variable).encode('utf-8')).hexdigest()

# 定义发送报错消息的同步函数
def send_error_message(error_message):
    from telegram.error import TimedOut
    chat_id = get_chat_id()
    bot = get_bot_instance()
    try:
        bot.send_message(chat_id=chat_id, text=error_message)
    except TimedOut as e:
        logger.error(f"发送报错消息超时: {e}")

# 定义发送报错消息的异步函数
async def send_error_message_async(bot_thon,error_message):
    chat_id = get_chat_id()
    try:
        await bot_thon.send_message(chat_id=chat_id, text=error_message)
    except Exception as e:
        logger.error(f"发送报错消息时出错: {e}")

# 定义同步非捕获异常处理函数
def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    error_message = f"程序出现未捕获的异常: {exc_type.__name__}: {exc_value}\n{traceback.format_exception(exc_type, exc_value, exc_traceback)}"
    logger.error(error_message)
    send_error_message(error_message)

# 定义异步异常处理函数
async def handle_error_async(bot_thon, error_message):
    logger.error(f"程序出现未捕获的异常: {error_message}")
    await send_error_message_async(bot_thon, error_message)


# 定义使用python-telegram-bot进行Bot实例化的函数
def get_bot_instance():
    API_TOKEN = get_bot_token()
    Bot_instance = telegram.Bot(token=API_TOKEN)
    logger.info(f"python-telegram-bot bot实例化成功: {Bot_instance}")
    return Bot_instance

# 定义使用telethon进行bot实例化的函数
async def get_telethon_bot_instance():
    api_id, api_hash, session_name = get_tg_api_id_hash()
    # 创建Telegram客户端实例
    bot_thon = await TelegramClient(session_name, api_id, api_hash).start()
    logger.info(f"Telegram-telethon bot实例化成功: {bot_thon}")
    return bot_thon

# 定义测试tg Bot发送消息的函数
def tg_send_message(chat_id, text):
    bot = get_bot_instance()
    bot.send_message(chat_id=chat_id, text=text)

# 定义tg Updater实例化的函数
def get_updater_instance(Bot_instance):
    from telegram.ext import Updater
    updater = Updater(bot=Bot_instance, use_context=True)
    logger.info(f"python-telegram-bot updater实例化成功: {updater}")
    return updater

# 定义构建翻译数据结构为一个json文件的函数
def build_translation_payload(text, source_lang, target_lang):
    translation_data = {
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang
    }
    return json.dumps(translation_data)

# 定义读取所有tg新闻来源频道的函数
def get_all_tg_news_channel_names():
    config = configparser.ConfigParser()
    config.read('config.ini')
    channel_names = []
    channels_section = config['tg_News_sources']
    for channel in channels_section:
        channel_names.append(channels_section[channel])
    return channel_names

# 定义读取媒体文件夹路径的函数
def get_media_dir():
    media_dir_path = read_config('file', 'media_dir')
    return media_dir_path

# 定义读取输出文件名的函数
def get_output_file_name():
    output_file = read_config('file', 'output_file_name')
    dir_path = read_config('file', 'dir_path')
    file = os.path.join(dir_path, output_file)
    return file

# 定义读取新闻上传日志文件名的函数
def get_news_log_file_name():
    news_log_file = read_config('file', 'news_log_file_name')
    dir_path = read_config('file', 'dir_path')
    file = os.path.join(dir_path, news_log_file)
    return file

# 定义记录新闻上传哈希表的函数
def write_news_log(news_hash):
    # 获取新闻上传日志文件名
    news_log_file_name = get_news_log_file_name()
    # 检查文件是否存在，如果不存在则创建
    if not os.path.exists(news_log_file_name):
        with open(news_log_file_name, 'wb') as file:
            pickle.dump({}, file)  # 创建一个空的pickle文件
    # 将news_hash写入文件
    with open(news_log_file_name, 'wb') as file:
        pickle.dump(news_hash, file)

# 定义读取新闻上传哈希表的函数
def get_news_log():
    news_log_file_name = get_news_log_file_name()
    try:
        if os.path.exists(news_log_file_name):
            with open(news_log_file_name, 'rb') as file:
                # 获取文件大小
                file.seek(0, 2)
                file_size = file.tell()
                if file_size > 0:
                    file.seek(0)  # 将文件指针移回文件开头
                    news_hash = pickle.load(file)   
                    logger.info(f"成功读取新闻哈希表，共{len(news_hash)}条新闻")
                else:
                    news_hash = {}
                    logger.info(f"新闻哈希表为空")
        else:
            # 如果哈希表文件不存在，初始化一个空的哈希表
            news_hash = {}
            errormsg = "Error: News hash log file does not exist."
            logger.error(errormsg)
            print(errormsg)
    except Exception as e:
        news_hash = {}
        logger.error(f"Error: {e}")
        print("Error: ", e)
    return news_hash

# 定义记录进输出文件的函数
def write_to_file(variable):
    output_file_name = get_output_file_name()
    # 检查文件是否存在，如果不存在则创建
    if not os.path.exists(output_file_name):
        with open(output_file_name, 'w') as file:
            file.write('')
            logger.info(f"文件不存在，创建文件: {output_file_name}")
    with open(output_file_name, 'a') as file:
        file.write(str(variable))
        logger.info(f"成功写入变量{str(variable)[:30]}到文件: {output_file_name}")

# 定义读取输出文件的函数
def read_from_file():
    output_file_name = get_output_file_name()
    with open(output_file_name, 'r') as file:
        return file.read()
    
# 定义对字符串进行转义处理的函数
def escape_markdown(text):
    # 定义需要转义的特殊字符
    special_chars = r'_*[]()~`>#+-=|{}.!'
    # 对特殊字符进行转义处理
    escaped_text = re.sub(r'([{}])'.format(re.escape(special_chars)), r'\\\1', text)
    return escaped_text

# 定义获取主进程重启次数的函数
def get_restart_times():
    restart_times = read_config('system', 'process_restart_times')
    return int(restart_times)

# 定义获取主进程重启间隔时间的函数
def get_restart_interval():
    restart_interval = read_config('Intervals', 'process_restart_interval')
    return int(restart_interval)

# 定义获取网络爬虫运行间隔时间的函数
def get_crawl_interval_time():
    crawl_interval = read_config('Intervals', 'crawl_interval')
    return int(crawl_interval)

# 定义获取新闻上传间隔时间的函数
def get_news_interval_time():
    news_interval = read_config('Intervals', 'news_item_publish_interval')
    return int(news_interval)

# 定义获取新闻重传间隔时间的函数
def get_retry_interval():
    retry_interval = read_config('Intervals', 'retry_interval')
    return int(retry_interval)

# 定义上传新闻到频道的异步函数
async def send_message_with_retry(bot_thon, channel_dest_name, msg_media, message):
    retry_interval = get_retry_interval()
    max_attempts = get_transfer_retry_times()
    for attempt in range(max_attempts):
        try_time = attempt + 1
        try:
            # 如果消息包含媒体文件
            if msg_media:
                # 检查媒体类型是否为MessageMediaWebPage
                if isinstance(msg_media, MessageMediaWebPage):
                    # 提取并发送网页信息，而不是作为文件
                    web_page_message = f"{message}\nURL: {msg_media.webpage.url}"
                    await bot_thon.send_message(channel_dest_name, web_page_message, parse_mode='md')
                else:
                    # 处理其他类型的媒体文件
                    await bot_thon.send_file(channel_dest_name, file=msg_media, caption=message, parse_mode='md')
            else:
                await bot_thon.send_message(channel_dest_name, message, parse_mode='md')
            return True  # 消息发送成功
        except FloodError as e:
            retry_after = e.seconds
            logger.warning(f"Flood error! Need to wait {retry_after} seconds. Attempt: {attempt + 1}")
            await asyncio.sleep(retry_after)
        except Exception as e:
            # 打印异常类型的名称
            exception_type = type(e).__name__
            logger.error(f"An error occurred: {e}. Exception type: {exception_type}. Attempt: {try_time}")
            await asyncio.sleep(retry_interval * (try_time))  # 重试间隔时间递增
    return False  # 消息发送失败

# 定义比较新闻上传日志和新闻哈希值的函数
def compare_news_hash_and_news_log(news_log_hash, msg_text):
    # 计算新闻的哈希值
    news_text_hash = get_hash(msg_text)
    # 检查本地哈希表中是否存在重复的新闻哈希值
    if news_text_hash in news_log_hash:
        # 本次发布的新闻数量减1
        return False
    return True

# 定义将新闻哈希值写入新闻上传日志的函数
def write_news_hash_to_log(news_log_hash, msg_text, msg_date):
    # 计算新闻的哈希值
    news_text_hash = get_hash(msg_text)
    # 将新闻要素以哈希表的形式写入文件，以备后续查重
    news_log_hash[news_text_hash] = {'date': msg_date, 'text': msg_text}
    write_news_log(news_log_hash)
    logger.info(f"成功写入新闻哈希值到日志: {news_text_hash}")