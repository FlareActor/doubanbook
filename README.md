# Scrapy For Images

标签（空格分隔）： Scrapy ImagePipeline

---

## Features ##

1.避免重复下载最近已经下载过的媒体资源（File、Image）
2.指定资源的存储路径（本地文件系统、Amazon S3）

Images Pipeline额外的特点：
1.将下载的图片转换成通用格式（JPG）
2.生成缩略图
3.检查图片的宽高，确定它们满足最小限制

## 使用Images Pipeline ##

在item中使用`image_urls`属性指定图片地址，下载的图片使用`images`属性保存信息

使用Image Pipeline的好处是你能通过配置一些额外的函数实现一些功能：

 - 生成缩略图  
 - 通过图片大小进行筛选

Image Pipeline使用`Pillow`库进行一些图片操作，要提前下载安装
 
当`item`进入`Pipeline`中进行下载时，下载任务仍然使用标准的Scrapy`调度器`和`下载器`，只不过这些图片下载任务具有`higher priority`

所以为了确保pipeline具有更高优先级以及开启，在配置文件中加入：

    ITEM_PIPELINES = {'scrapy.pipelines.images.ImagesPipeline': 1}

接下来指定存储路径（如果不指定，image pipeline不会生效！）：

    IMAGES_STORE = '/path/to/valid/dir'

## 存储系统 ##

目前只支持文件系统`FS`，和`Amazon S3`

### FS ###

文件使用`URL`的`SHA1 hash`值作为文件名存储，like：

    <IMAGES_STORE>/full/3afec3b4765f8f0a07b78f98c07b83f013567a0a.jpg
    
## 使用pipeline ##

将URLs放在 `file_urls` or `image_urls` Field属性中，下载的结果会对应放在 `files` or `images` 中：

    class MyItem(scrapy.Item):
    
        # ... other item fields ...
        image_urls = scrapy.Field()
        images = scrapy.Field()
    
当然也能通过一定设置使用自己的关键字保存url和result，在setting中加入：

    IMAGES_URLS_FIELD = 'field_name_for_your_images_urls'
    IMAGES_RESULT_FIELD = 'field_name_for_your_processed_images'
    
## 额外的配置 ##

#### 设置超时时间 ####

ImagePipeline避免重新下载最近下载过的图片，设置截止时间：

    # 120 days of delay for files expiration
    FILES_EXPIRES = 120
    
    # 30 days of delay for images expiration
    IMAGES_EXPIRES = 30

默认时间是`90天`

#### [Thumbnail generation for images][1] ####
 

#### [设置超时时间][2] ####

## 可覆盖的方法 ##

    get_media_requests(item, info)

针对每一个image URL必须返回一个`Request`进行下载

    item_completed(results, item, info)

一个item中的`所有`图片下载完成or失败后回调

### 示例 ###

    import scrapy
    from scrapy.pipelines.images import ImagesPipeline
    from scrapy.exceptions import DropItem
    
    class MyImagesPipeline(ImagesPipeline):
    
        def get_media_requests(self, item, info):
            for image_url in item['image_urls']:
                yield scrapy.Request(image_url)
    
        def item_completed(self, results, item, info):
            image_paths = [x['path'] for ok, x in results if ok]
            if not image_paths:
                raise DropItem("Item contains no images")
            item['image_paths'] = image_paths
            return item
            
## 参考 ##
[1.Scrapy官网][3]


  [1]: https://doc.scrapy.org/en/1.3/topics/media-pipeline.html#thumbnail-generation-for-images
  [2]: https://doc.scrapy.org/en/1.3/topics/media-pipeline.html#filtering-out-small-images
  [3]: https://doc.scrapy.org/en/1.3/topics/media-pipeline.html