# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


# 豆瓣丛书Item
class DoubanbookItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    book_src = Field()
    book_title = Field()
    book_href = Field()
    book_rating_nums = Field()
    book_rating_counting = Field()
    book_author = Field()
    book_publisher = Field()
    book_publish_date = Field()
    pass


# 花瓣网图片Item
class ImageItem(scrapy.Item):
    # define the fields for your item here like:
    image_urls = Field()
    # images = Field()
    image_checksum = Field()
    pass


# 抓取指数
class IndexItem(scrapy.Item):
    index_name = Field()
    index_number = Field()
    pass


# 抓取百度Dogs
class DogItem(scrapy.Item):
    image_urls = Field()
    image_paths = Field()
    pass
