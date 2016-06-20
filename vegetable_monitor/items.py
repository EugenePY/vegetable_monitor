# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import json


class VegetableMonitorItem(scrapy.Item):
    # define the fields for your item here like:
    data = scrapy.Field()
    date = scrapy.Field()
    image = scrapy.Field()

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
