import Services.get_web_news as get_web_news
import Services.translate as translate


news_elements_list = get_web_news.extract_news_elements('https://www.rt.com/news/','https://www.rt.com/tags/feature/')
for news_elements in news_elements_list:
    title,code,id = translate.translate_text_to_Chinese(news_elements['news_title'])
    if code != 200:
            print(f"翻译失败，错误代码: {code}")
            break
    content,code,id = translate.translate_text_to_Chinese(news_elements['news_content'])
    if code != 200:
            print(f"翻译失败，错误代码: {code}")
            break
    
    authors = news_elements['news_authors']
    link = news_elements['news_link']
    newstime = news_elements['news_time']
    img = news_elements['news_img']
    print(f"新闻标题：{title}\n新闻作者：{authors}\n新闻时间：{newstime}\n新闻链接：{link}\n{img}\n新闻内容：\n{content}\n")
    print('-----------------')