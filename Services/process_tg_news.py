import Services.functions as functions
import Services.translate as translate
import asyncio, re

# 获取日志配置
logger = functions.setup_logging()

# 定义一个异步函数，使用telethon获取Telegram频道的消息
async def get_channel_messages(bot_thon,channel_name):
    # 频道的用户名或ID
    channel_username = channel_name
    # 读取每次获取频道信息的次数
    count = functions.get_msg_number()
    # 初始化一个列表，用于存储消息内容
    messages_content = []
    # 初始化一个消息数量计数器
    msg_count = 0
    # 读取新闻上传日志进入哈希表
    news_log_hash = functions.get_news_log()
    try:
        # 获取频道消息
        async for message in bot_thon.iter_messages(channel_username, limit=count):
            msg_date = message.date
            msg_text = message.text
            msg_media = message.media

            if msg_text is None:
                logger.warning(f"消息内容为空，跳过处理")
                continue
            # 检查本地哈希表中是否存在重复的新闻哈希值
            compare_result = functions.compare_news_hash_and_news_log(news_log_hash, msg_text)
            if compare_result is False: # 如果存在相同新闻哈希值
                logger.info(f"已发布过重复新闻，跳过处理")
                continue  # 存在相同新闻哈希值，跳过处理

            # 将有内容的消息和媒体信息添加到消息列表中
            messages_content.append((msg_date, msg_text, msg_media))
            print(f"获取频道消息成功: {msg_date}, {msg_text[:30]}...")
            msg_count += 1
        logger.info(f"成功获取了有效频道消息{msg_count}条")
    except Exception as e:
        error_message = f"获取频道消息失败: {e}"
        await functions.handle_error_async(bot_thon, error_message)
        messages_content = None

    # 返回消息内容
    return messages_content

# 定义一个异步函数，翻译并处理频道消息格式
async def handel_channel_messages(bot_thon, message_content, channel_name):

    # 定义一个空列表，用于存储翻译后的消息内容
    translated_messages = []
    
    # 获取频道消息
    try:
        # message_content = await get_channel_messages(bot_thon, channel_name)
        for msg_date, msg_text, msg_media in message_content:
            if msg_text is None:
                logger.warning(f"消息内容为空，跳过处理")
                continue
            translate_text, status_code, translate_id = await translate.translate_text_to_Chinese(msg_text)
            if status_code != 200:
                logger.error(f"翻译失败: {translate_id}, {status_code}")
                continue

            # 提取标题（第一句话，假设它被**包裹）
            match = re.search(r'\*\*(.*?)\*\*', translate_text)
            news_title = match.group(1) if match else msg_text[:30]+"..."
            # 处理频道消息的格式为Markdown
            # escape_news_text = functions.escape_markdown(translate_text)
            # escape_news_time = functions.escape_markdown(msg_date.strftime('%Y-%m-%d %H:%M))
            publish_news = f"**{msg_date}**\n{translate_text}\n\n[From {channel_name}](https://t.me/{channel_name})"
            translated_messages.append((msg_date, msg_text, translate_text, publish_news, msg_media))
            print(f"{translate_text[:30]}...")
            logger.info(f"翻译和处理频道消息成功: {news_title}")
        
    except Exception as e:
        error_message = f"处理频道消息失败: {e}"
        await functions.handle_error_async(bot_thon, error_message)
        translated_messages = None

    return translated_messages

# 定义一个异步函数，上传翻译后的消息到频道
async def send_translated_messages_to_channel(bot_thon, channel_dest_name, translated_messages, channel_name):

    # 读取新闻上传日志进入哈希表
    news_log_hash = functions.get_news_log()
    # 获取本次拟发布的新闻数量
    news_count = len(translated_messages)

    # 遍历翻译后的消息内容
    for msg_date, msg_text, msg_translate, publish_news, msg_media in reversed(translated_messages): # 逆序遍历
        # 检查本地哈希表中是否存在重复的新闻哈希值
        compare_result = functions.compare_news_hash_and_news_log(news_log_hash, msg_text)
        if compare_result is False: # 如果存在相同新闻哈希值
            news_count -= 1 # 本次发布的新闻数量减1
            continue  # 存在相同新闻哈希值，跳过发布

        # 异步发布新闻内容到Telegram频道
        message_sent = await functions.send_message_with_retry(bot_thon, channel_dest_name, msg_media, publish_news)
        if message_sent:
            # 将新闻要素以哈希表的形式写入文件，以备后续查重
            functions.write_news_hash_to_log(news_log_hash, msg_text, msg_date)
            # 获取新闻发布间隔时间
            upload_interval = functions.get_news_interval_time()
            # 控制发送速率，等待一定时间
            await asyncio.sleep(upload_interval)
        else:
            await functions.handle_error_async(bot_thon, f"Failed to send message after retries: {msg_text}")
            news_count -= 1
    return news_count