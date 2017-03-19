"""
爬取花瓣网图片
"""

__author__ = "wdx"

import scrapy
from doubanbook.items import ImageItem
import re


class PhotoSpider(scrapy.Spider):
    name = "girls"

    custom_settings = {
        'IMAGES_STORE': '/Users/wangdexun/Desktop/images/girls'
    }

    base_url = 'http://huaban.com/favorite/beauty'

    # 'http://huaban.com/favorite/beauty?max=1062927196&limit=20&wfl=1'
    start_urls = [base_url]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__number = int(kwargs.get('number', 3))
        self.__index = 0

    def parse(self, response):
        """
        正则表达式中？表示非贪心，找对第一个就停下来
        也可以将Json字符串反序列化成对象进行查找
        """
        script_content = response.xpath('/html/body/script[1]').extract_first()
        match = re.search('app.page\\["pins"\\](.*?)\n', script_content)
        if match:
            pins_content = match.group(1)
            image_urls = re.findall('{"pin_id".*?"file":.*?"key":"(.*?)"', pins_content, re.S)
            if image_urls:
                image = ImageItem()
                image['image_urls'] = map(lambda key: 'http://img.hb.aicdn.com/' + key + '_/fw/480', image_urls)
                yield image
            if self.__index < self.__number:
                last_pin_id = re.search('.*\\{"pin_id":(.*?), "user_id', pins_content, re.S)
                if last_pin_id:
                    next_page = self.base_url + "?max=" + last_pin_id.group(1) + "&limit=20&wfl=1"
                    self.__index += 1
                    yield scrapy.Request(next_page, self.parse)
