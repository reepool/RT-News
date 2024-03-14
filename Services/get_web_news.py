from newspaper import fulltext
import newspaper
import tweepy
import logging
import Services.functions as functions


# 获取日志配置
functions.setup_logging()
logger = logging.getLogger()

# 定义一个使用newspaper3k提取新闻要素的函数，返回一个包含新闻要素的列表
def extract_news_elements(News_url, Excpeted_news_url): # 传入新闻网站的URL和要排除的新闻链接
    # 创建新闻网站对象实例
    paper = newspaper.build(News_url, memoize_articles=False)

    # 提取新闻链接
    news_urls = []
    for article in paper.articles:
        if len(news_urls) >= 3:  # 限制只提取前20条新闻链接
            break
        news_urls.append(article.url)

    # 逐个链接分析新闻，提取新闻要素
    news_elements_list = []  # 用于存储新闻要素的列表
    for news_url in news_urls:
        if news_url.strip() == Excpeted_news_url: # 跳过要排除的新闻链接
            continue
        article = newspaper.Article(news_url)
        article.download()
        article.parse()
        
        # 提取新闻要素
        title = article.title
        authors = article.authors
        publish_date = article.publish_date
        text = article.text
        link = article.url
        img = article.top_image
        # nlp = article.nlp() # 提取新闻内容的关键词，但是目前这个功能取出来的数据是None
        
        # 将新闻要素构造成一个字典
        news_element = {
            "news_title": title,
            "news_link": link,
            "news_authors": authors,
            "news_time": publish_date,
            "news_content": text,
            "news_img": img,
            # "news_nlp": nlp
        }
        # 将新闻要素添加到列表中
        news_elements_list.append(news_element)

    return news_elements_list  # 返回包含新闻要素的列表

# 定义一个函数，使用tweepy获取推文
def get_tweets(twitter_user_name):
    # 获取Twitter API的密钥
    consumer_key, consumer_secret, access_token, access_token_secret = functions.get_x_tokens_keys()
    # 使用密钥进行认证
    # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    # auth.set_access_token(access_token, access_token_secret)
    # 创建API实例
    api = tweepy.API(auth)
    # 获取推文
    tweets = api.user_timeline(screen_name=twitter_user_name, count=5)  # 获取最新的5条推文
    # 返回推文列表
    return tweets
