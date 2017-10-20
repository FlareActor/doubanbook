# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import pymysql
import os
import scrapy
import pandas as pd
import numpy as np


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


class BaiduDogImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        """(start_requests->parse)->(get_media_requests->file_path->item_completed)"""
        yield scrapy.Request(url=item['image_urls'][0], meta={'path': item['image_paths']})

    def file_path(self, request, response=None, info=None):
        """自定义文件名"""
        return '%s.jpg' % request.meta['path']

    def item_completed(self, results, item, info):
        return item


class BaiduSearchResultPipeline(object):
    """
    将爬取的Item存入Mysql
    """

    def __init__(self):
        """
        每一个进程都有自己的内存空间(系统分配资源的最小单位),静态变量不共享,具有不同的全局区内存地址
        """
        self.db = pymysql.connect(host='172.20.45.88', port=3306, user='medicalteam', passwd='medicalteam_2017',
                                  db='db_qiuyi', charset='utf8')
        self.cur = self.db.cursor()

    def process_item(self, item, spider):
        # print(item['index_name'], item['index_number'])
        """效率问题：主键？"""
        self.cur.execute("UPDATE db_qiuyi.tb_ill SET search_index_new = %d WHERE name = '%s';" % (
            int(item['index_number']), item['index_name']))
        return item

    def close_spider(self, spider):
        self.db.commit()
        self.cur.close()
        self.db.close()
        print("close spider ", spider)
