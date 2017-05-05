from scrapy import cmdline

# cmdline.execute("scrapy crawl photo -a category=咱们裸熊 -a number=20".split())  # 爬取花瓣网图片
# cmdline.execute("scrapy crawl dbbook".split())#爬取豆瓣书籍
# cmdline.execute("scrapy crawl girls -a number=30".split())  # 爬取豆瓣书籍
cmdline.execute("scrapy crawl index".split())  # 爬取百度指数
