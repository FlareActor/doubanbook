from scrapy import cmdline

# cmdline.execute("scrapy crawl photo -a category=黄瓜 -a number=3".split())  # 爬取花瓣网图片
# cmdline.execute("scrapy crawl dbbook".split())#爬取豆瓣书籍
# cmdline.execute("scrapy crawl girls -a number=30".split())  # 爬取豆瓣书籍
# cmdline.execute("scrapy crawl BaiDuSearchResult".split())  # 爬取百度指数
cmdline.execute("scrapy crawl dogs".split())  # 爬取百度dogs
