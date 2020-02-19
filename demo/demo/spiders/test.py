# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging
import json


class TestSpider(CrawlSpider):
    name = 'test'
    allowed_domains = ['httpbin.org']
    start_urls = ['http://httpbin.org/ip']

    rules = (
        #Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse_start_url(self, response):
        for _ in range(2):
            yield scrapy.Request('http://httpbin.org/ip', dont_filter = True, callback=self.parse_proxy)
            yield scrapy.Request('https://httpbin.org/ip', dont_filter = True, callback=self.parse_proxy)

    def parse_proxy(self, response):
        if not response.text:
            return
        self.logger.info('>>>>>>>>> {}'.format(json.loads(response.text)))