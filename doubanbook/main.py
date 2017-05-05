from scrapy import cmdline

cmdline.execute("scrapy crawl photo -a category=R2D2 -a number=10".split())  # 爬取花瓣网图片
# cmdline.execute("scrapy crawl dbbook".split())#爬取豆瓣书籍
# cmdline.execute("scrapy crawl girls -a number=30".split())  # 爬取豆瓣书籍
