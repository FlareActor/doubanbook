import os
from scrapy_redis.spiders import RedisSpider
from scrapy.exceptions import DontCloseSpider
import time


class SpiderMixin(object):
    """like interface in Java"""

    @classmethod
    def clear_store_file(cls):
        # 删除存储文件
        if "FEED_URI" in cls.custom_settings and os.path.exists(cls.custom_settings["FEED_URI"]):
            os.remove(cls.custom_settings["FEED_URI"])


class MyRedisSpider(RedisSpider):
    """当没有url可爬时,定时关闭的RedisSpider"""

    def __init__(self, **kwargs):
        """RedisSpider->RedisMixin->Spider.__init__"""
        super().__init__(**kwargs)
        # Spider停止之前的最大等待时间
        self.interval_to_close = self.custom_settings['INTERVAL_TO_CLOSE'] \
            if 'INTERVAL_TO_CLOSE' in self.custom_settings else 30
        self.start_time = time.time()

    def schedule_next_requests(self):
        """
        不断从redis中取url来爬取
        :return:
        """
        for req in self.next_requests():
            # req.dont_filter = False  # 开启查重筛选
            self.crawler.engine.crawl(req, spider=self)
            self.start_time = time.time()

    def spider_idle(self):
        """
        当全部爬取后，周期性查询redis中有没有新的url，默认5秒
        超过时间自动关闭爬虫
        :return:
        """
        self.schedule_next_requests()
        if time.time() - self.start_time < self.interval_to_close:
            raise DontCloseSpider
