# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class StarCrawlItem(Item):
    # define the fields for your item here like:
    # name = Field()
    #question_txt = Field()
    ori_pic_src = Field()
    publish_time = Field()
    page_url = Field()
    pic_title = Field()
    category = Field()
    tag = Field()
    group_mark = Field()
    group_idx = Field()
    pfrom = Field()
    pass

class StarCrawlLoader(ItemLoader):
    default_item_class = StarCrawlItem
    default_input_processor = MapCompose(lambda s: s.strip())
    default_output_processor = TakeFirst()
    tag_out = Join("；")
