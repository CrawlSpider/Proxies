# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import json
import logging
import time

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError



class MtestSpider(CrawlSpider):
    name = 'mtest'
    allowed_domains = ['httpbin.org']
    start_urls = ['http://httpbin.org/ip']

    rules = (
        #Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse_start_url(self, response):
        with open('C:/Users/wlzqi/Desktop/proxies.json') as f:
            proxy_list = json.loads(f.read())
            for proxy in proxy_list:
                scheme = proxy['scheme']
                proxy = proxy['proxy']
                url = '{}://httpbin.org/ip'.format(scheme)
                meta = {
                    'proxy': proxy,
                    'dont_retry': True,
                    'download_timeout': 10,
                    #
                    # 多个字段是传递给 check_available 方法的信息，方便检测
                    'scheme': scheme,
                }
                yield scrapy.Request(url = url,
                    callback = self.check_available,
                    errback = self.errback_httpbin,
                    meta = meta,
                    dont_filter = True)
    
    def check_available(self, response):
        if not response.text:
            return
        origin = json.loads(response.text)['origin']
        proxy = response.meta['proxy']
        for ip in origin:
            if ip in proxy:
                self.logger.debug('Discover a valid anonymous proxy server: {}'.format(response.meta['proxy']))
                # 可以使用 -o 保存为文件，下面就是文件的 字段和值的定义
                yield {
	    		    'proxy': response.meta['proxy'],
                    'scheme': response.meta['scheme'],
	    	    }
                break
    #
    #
    #
    def errback_httpbin(self, failure):
        # log all failures
        self.logger.info(repr(failure))
        # in case you want to do something special for some errors,
        # you may need the failure's type:
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.info('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.info('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.info('TimeoutError on %s', request.url)
    


