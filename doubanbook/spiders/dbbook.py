# -*- coding: utf-8 -*-
import scrapy
from doubanbook.items import DoubanbookItem
import re


class DbbookSpider(scrapy.Spider):
    name = "dbbook"
    # allowed_domains = ["https://www.douban.com/doulist/1264675/"]
    start_urls = ['https://www.douban.com/doulist/1264675/']

    custom_settings = {
        'FEED_FORMAT': 'CSV',
        'FEED_URI': 'data/book.csv',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # import os
        # if os.path.exists(self.outputPath):
        #     os.remove(self.outputPath)

    def parse(self, response):
        book = DoubanbookItem()
        for book_selector in response.xpath('//div[@class="bd doulist-subject"]'):
            book['book_src'] = book_selector.xpath('div[@class="post"]/a/img/@src').extract_first()
            book['book_title'] = book_selector.xpath('div[@class="title"]/a/text()').extract_first().strip(' \n')
            book['book_href'] = book_selector.xpath('div[@class="title"]/a/@href').extract_first()
            book['book_rating_nums'] = book_selector.xpath('div[@class="rating"]/span[2]/text()').extract_first()
            book['book_rating_counting'] = book_selector.xpath(
                'div[@class="rating"]/span[3]/text()').extract_first().strip('()')
            book_abstract = book_selector.xpath('div[@class="abstract"]').xpath('string(.)').extract_first()
            book['book_author'] = self.__match("作者:(.*?)\n", book_abstract)
            book['book_publisher'] = self.__match("出版社:(.*?)\n", book_abstract)
            book['book_publish_date'] = self.__match("出版年:(.*?)\n", book_abstract)
            yield book

            next_page = response.xpath('//div[@class="paginator"]').xpath('span[@class="next"]/a/@href').extract_first()
            if next_page is not None:
                print(next_page)
                yield scrapy.Request(url=next_page, callback=self.parse)

    @staticmethod
    def __match(pattern, string):
        match = re.search(pattern, string, re.S)
        if match:
            return match.group(1).strip()
        else:
            return None
