"""
爬取花瓣网图片
"""

__author__ = "wdx"

import scrapy
from doubanbook.items import ImageItem
import re


class PhotoSpider(scrapy.Spider):
    name = "photo"

    custom_settings = {
        'IMAGES_STORE': '/Users/wangdexun/Desktop/images/'
    }

    def start_requests(self):
        base_url = "http://huaban.com/search/?q=category&page=1&per_page=20&wfl=1".replace('category',
                                                                                           self.__category)
        for index in (i for i in range(1, self.__number + 1)):
            yield scrapy.Request(re.sub('&page=(.*?)&', '&page=' + str(index) + '&', base_url), self.parse)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__category = kwargs.get('category', '星球大战')
        self.__number = int(kwargs.get('number', 3))
        # store_path = self.custom_settings.get('IMAGES_STORE') + '星球大战'
        # self.custom_settings['IMAGES_STORE'] = store_path

    def parse(self, response):
        script_content = response.xpath('/html/body/script[1]').extract_first()
        """
        正则表达式中？表示非贪心，找对第一个就停下来
        也可以将Json字符串反序列化成对象进行查找
        """
        image_urls = re.findall('{"pin_id".*?"file":.*?"key":"(.*?)"', script_content, re.S)
        if image_urls:
            image = ImageItem()
            image['image_urls'] = map(lambda key: 'http://img.hb.aicdn.com/' + key + '_fw658', image_urls)  # _/fw/480
            yield image
