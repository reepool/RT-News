import Services.functions as functions

logger = functions.setup_logging()

def clean_news_log():
    logger.info('开始清理新闻日志')
    # 读取新闻记录文件
    news_log = functions.get_news_log()
    news_count = len(news_log)

    # 读取最早记录的时间和最晚记录的时间
    earliest_time_record = min(news_log.values(), key=lambda x: x['date'])['date']
    latest_time_record = max(news_log.values(), key=lambda x: x['date'])['date']

    logger.info(f'日志中最早的记录为{earliest_time_record}，最晚的记录为{latest_time_record}')

    # 检查记录数量是否超过500
    if news_count > 500:
        logger.info(f'新闻日志数量为{news_count}条，超过300条的老日志将被清理...')
        # 保留最新的300条记录
        sorted_news_log = sorted(news_log.items(), key=lambda x: x[1]['date'], reverse=True)
        news_log = dict(sorted_news_log[:300])

        # 保存更新后的新闻记录文件
        functions.write_news_log(news_log)
        logger.info('新闻日志清理完成')
        print('新闻日志清理完成')
    else:
        logger.info(f"新闻日志数量为{news_count}条，未超过500条，无需清理")
        print(f'新闻日志数量为{news_count}条，无需清理，进程结束')

if __name__ == "__main__":
    clean_news_log()
# The clean.py script is used to clean up the news log. The news log is a dictionary that contains news items and their publication dates. The script reads the news log from a file, checks the number of records, and removes the oldest records if the number of records exceeds 300. The script then saves the updated news log to the file. The script uses the setup_logging function from the functions module to set up logging. The script also prints messages to the console. The script is executed when the __name__ variable is set to "__main__". The script is not tested.