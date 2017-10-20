# -*- coding: utf-8 -*-

import pandas as pd
from doubanbook.items import DogItem
from doubanbook.spiders.base import SpiderMixin, MyRedisSpider
import numpy as np
import scrapy
from scrapy.spiders import Spider


class BaiDuDogsSpider(Spider):
    """
    爬取百度Dogs比赛
    原生Scrapy.Spider使用collections.deque，不能多进程访问
    RedisSpider enables a spider to read the urls from redis
    """

    name = "dogs"

    custom_settings = {
        # 'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        # 'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",  # 查重组件
        'IMAGES_STORE': '/Users/wangdexun/Desktop/dogs/',
        'ITEM_PIPELINES': {
            'doubanbook.pipelines.BaiduDogImagePipeline': 1,
            # 'scrapy_redis.pipelines.RedisPipeline': 300
        },
        'ROBOTSTXT_OBEY': False,
        # 'REDIS_URL': 'redis://:605160@localhost:6379',
        # 'INTERVAL_TO_CLOSE': 10
    }

    def start_requests(self):
        df = pd.read_csv('/Users/wangdexun/Downloads/Baidu-dogs/data/train/data_train.txt', header=None, sep='\n')
        df['url'] = df[0].apply(lambda x: x.split(" ")[1])
        df['label'] = df[0].apply(lambda x: x.split(" ")[0]).astype(int)
        df.drop(0, axis=1, inplace=True)
        nb_count = pd.Series(index=np.unique(df['label']), data=0)

        def index_dog(label):
            index = nb_count[label]
            nb_count[label] = index + 1
            return str(label) + "_" + str(index)

        df['name'] = df['label'].apply(index_dog)
        for index, data in df[['url', 'name']][:1].iterrows():
            yield scrapy.Request(
                url=data['url'],
                meta={'name': 'train/' + data['name'], '_url': data['url']})

    # def start_requests(self):
    #     df = pd.read_csv('/Users/wangdexun/Downloads/Baidu-dogs/data/测试数据-1.txt', header=None, sep='\n')
    #     df.columns = ['url']
    #     for index, data in enumerate(df['url']):
    #         yield scrapy.Request(url=data, meta={'name': 'test/'+str(index), '_url': data})

    def parse(self, response):
        dog = DogItem()
        meta_data = response.request.meta
        dog['image_urls'] = [
            meta_data['_url'] if 'http:' or 'https:' in meta_data['_url'] else ('http:' + meta_data['_url'])]
        dog['image_paths'] = meta_data['name']
        yield dog


if __name__ == '__main__':
    # 整理一波未被爬取下来的图片集合
    import os
    import re

    train_df = pd.read_csv('/Users/wangdexun/Downloads/Baidu-dogs/data/train/data_train.txt', header=None, sep='\n')
    train_df['url'] = train_df[0].apply(lambda x: x.split(" ")[1])
    train_df['label'] = train_df[0].apply(lambda x: x.split(" ")[0]).astype(int)
    train_df['pos'] = 0
    train_df.drop(0, axis=1, inplace=True)
    train_crawled = os.listdir('/Users/wangdexun/Desktop/dogs/train')
    train_crawled = list(map(lambda x: re.split('\\.|_', x)[:2], train_crawled))
    train_crawled = pd.DataFrame(train_crawled[1:], dtype='int', columns=['label', 'index']).sort_values(
        ['label', 'index'])
    for label in np.unique(train_df['label']):
        train_index = train_df[train_df.label == label].index
        train_df.loc[train_index, 'pos'] = train_index - train_index[0]
        train_df.drop(train_index[0] + train_crawled[train_crawled.label == label]['index'], axis=0, inplace=True)

    test_df = pd.read_csv('/Users/wangdexun/Downloads/Baidu-dogs/data/测试数据-1.txt', header=None, sep='\n')
    test_df.columns = ['url']
    test_crawled = os.listdir('/Users/wangdexun/Desktop/dogs/test')
    test_crawled = pd.DataFrame(list(map(lambda x: re.split('\\.|_', x)[0], test_crawled)),
                                columns=['index'], dtype='int').sort_values('index')
    test_df.drop(test_crawled['index'], axis=0, inplace=True)
    test_df['pos'] = test_df.index

    train_df.to_csv('train_uncrawled.csv', index=False)
    test_df.to_csv('test_uncrawled.csv', index=False)
    print(train_df)
    print(test_df)
    pass
