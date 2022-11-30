# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BostonrealtyadvisorsscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    property_title = scrapy.Field()
    transaction_type = scrapy.Field()
    building_address = scrapy.Field()
    price = scrapy.Field()
    size = scrapy.Field()
    units = scrapy.Field()
    pass
