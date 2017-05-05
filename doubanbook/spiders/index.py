# -*- coding: utf-8 -*-
import scrapy
from doubanbook.items import IndexItem
import re
import pandas as pd
import os


class IndexSpider(scrapy.Spider):
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
        if os.path.exists(self.custom_settings["FEED_URI"]):
            os.remove(self.custom_settings["FEED_URI"])

    def start_requests(self):
        illnames = pd.read_csv('data/illname.csv')
        for illname in illnames.name:
            yield scrapy.Request(url='http://rank.chinaz.com/ajaxsync.aspx?at=index&kw=%s' % illname)

    def parse(self, response):
        index = IndexItem()
        result_body = response.body.decode("utf8")  # 将utf8编码的字节数组解码
        index['index_name'] = self.illname_pattern.search(result_body).group(1)
        index['index_number'] = self.illindex_pattern.search(result_body).group(1)
        yield index
