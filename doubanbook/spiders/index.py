# -*- coding: utf-8 -*-

import re
import pandas as pd
import redis
import scrapy
from pprint import pprint

from doubanbook.items import IndexItem
from doubanbook.spiders.base import SpiderMixin, MyRedisSpider


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


class BaiDuSearchResultSpider(MyRedisSpider, SpiderMixin):
    """
    爬取百度搜索结果数
    原生Scrapy.Spider使用collections.deque，不能多进程访问
    RedisSpider enables a spider to read the urls from redis
    """

    name = "BaiDuSearchResult"

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
