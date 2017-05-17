# -*- coding: utf-8 -*-
import os
import re
import time

import pandas as pd
import redis
import scrapy
from scrapy.exceptions import DontCloseSpider
from scrapy_redis.spiders import RedisSpider
from pprint import pprint

from doubanbook.items import IndexItem


class SpiderMixin(object):
    @classmethod
    def clear_store_file(cls):
        # 删除存储文件
        if "FEED_URI" in cls.custom_settings and os.path.exists(cls.custom_settings["FEED_URI"]):
            os.remove(cls.custom_settings["FEED_URI"])


class IndexSpider(scrapy.Spider, SpiderMixin):
    """
    爬取搜索指数
    """
    name = "index"

    illname_pattern = re.compile("kw:'(.*?)'")

    illindex_pattern = re.compile(",index:'(.*?)'")

    custom_settings = {
        'FEED_FORMAT': 'CSV',
        'FEED_URI': 'data/index.csv',
        'ITEM_PIPELINES': {}
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clear_store_file()

    def start_requests(self):
        illnames = pd.read_csv('data/ill_name.csv')
        for illname in illnames.name:
            yield scrapy.Request(url='http://rank.chinaz.com/ajaxsync.aspx?at=index&kw=%s' % illname)

    def parse(self, response):
        index = IndexItem()
        result_body = response.body.decode("utf8")  # 将utf8编码的字节数组解码
        index['index_name'] = self.illname_pattern.search(result_body).group(1)
        index['index_number'] = self.illindex_pattern.search(result_body).group(1)
        yield index


class BaiDuSearchResultSpider(RedisSpider, SpiderMixin):
    """
    爬取百度搜索结果数
    RedisSpider enables a spider to read the urls from redis
    """

    name = "BaiDuSearchResult"

    def __init__(self, **kwargs):
        """RedisSpider->RedisMixin->Spider.__init__"""
        super().__init__(**kwargs)
        # Spider停止之前的最大等待时间
        self.interval_to_close = self.custom_settings['INTERVAL_TO_CLOSE'] \
            if 'INTERVAL_TO_CLOSE' in self.custom_settings else 30
        self.start_time = time.time()

    custom_settings = {
        'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",  # 查重组件
        'FEED_FORMAT': 'CSV',
        'FEED_URI': 'data/search_nums.csv',
        # 'ITEM_PIPELINES': {
        #     'doubanbook.pipelines.BaiduSearchResultPipeline': 1,
        #     'scrapy_redis.pipelines.RedisPipeline': 300
        # },
        'ROBOTSTXT_OBEY': False,
        'REDIS_URL': 'redis://:605160@localhost:6379',
        'INTERVAL_TO_CLOSE': 10
    }

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

    def parse(self, response):
        index = IndexItem()
        search_key = response.xpath("head/title/text()").extract_first()
        search_value = response.xpath("//div[@class='nums']/text()").extract_first()
        # print(search_key, search_value)
        index['index_name'] = search_key.split("_")[0]
        index['index_number'] = re.search("约(.*?)个", search_value).group(1).replace(",", "")
        yield index


if __name__ == "__main__":
    """查看继承关系图MRO"""
    pprint(BaiDuSearchResultSpider.mro())
    BaiDuSearchResultSpider.clear_store_file()
    # 分块读取
    df = pd.read_csv("data/ill_name.csv", iterator=True, chunksize=1000)
    chunks = []
    for index, chunk in enumerate(df):
        chunks.append(chunk)
    ill_names = pd.concat(chunks, ignore_index=True)

    r = redis.StrictRedis(password='605160')
    r.flushdb()
    for ill_name in ill_names['name'][:90]:
        r.lpush('BaiDuSearchResult:start_urls',
                "https://www.baidu.com/s?ie=utf-8&newi=1&mod=1&isbd=1&isid=add9cb6c00066215&wd=" + ill_name + "&rsv_spt=1&rsv_iqid=0xeb33c87a0006c47e&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=baiduhome_pg&rsv_enter=0&oq=scrapy.downloadermiddlewares.robotstxt%255D%2520D%2526gt%253BBUG%253A%2520Forbidden%2520by%2520robots.txt%253A&inputT=2351&rsv_t=3c61r9Uo61MB9dpGdePu0o83c95y9eBekyaWatUY9wMAP%2BQqBa0Kkpm2FZVSMKmGmgKr&rsv_pq=f8f6c48c0004fdc0&gpc=stf%3D1463320784%2C1494856784%7Cstftype%3D1&tfflag=1&bs=%E4%B8%8B%E6%B6%88&rsv_sid=1457_21127_22749_22917_20929&_ss=1&clist=35b8fd07764ead12%0935b8fd07764ead12%0935b8fd07764ead12%0950a0f2ad5843fdcd&hsug=&f4s=1&csor=2&_cr1=49602")
