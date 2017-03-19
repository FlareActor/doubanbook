# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem


class DoubanbookPipeline(object):
    def process_item(self, item, spider):
        print('DoubanbookPipeline')
        return item


class MyImagePipeline(ImagesPipeline):
    # def get_media_requests(self, item, info):
    #     for image_url in item['image_urls']:
    #         yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_checksum = [x['checksum'] for ok, x in results if ok]
        if not image_checksum:
            raise DropItem("Item contains no images")
        item['image_checksum'] = image_checksum
        return item
