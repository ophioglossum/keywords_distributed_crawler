# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class KeywordsDistributedCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BaiduItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    phone = scrapy.Field()
    platform = scrapy.Field()
    source_url = scrapy.Field()
