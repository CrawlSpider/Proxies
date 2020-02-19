# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging
import json


class XcipSpider(CrawlSpider):
    name = 'xcip'
    allowed_domains = ['xicidaili.com']
    start_urls = [
        'https://www.xicidaili.com/nn',
        'https://www.xicidaili.com/nn/2',
        'https://www.xicidaili.com/nn/3',
        'https://www.xicidaili.com/nn/4',
        'https://www.xicidaili.com/nn/5',
        ]

    rules = (
        #Rule(LinkExtractor(restrict_xpaths='//a[contains(@class, "next_page")]'), callback='parse_items', follow=True),
    )

    def parse_start_url(self, response):
        return self.parse_item(response)

    '''
    def parse_items(self, response):
        return self.parse_item(response)
    '''
    
    def parse_item(self, response):
        # item = {}
        # return item
        #
        #
        node_list = response.xpath(u'//table[@id="ip_list"]/tr[position() > 1]')
        for node in node_list:
            ip = node.xpath(u'td[2]/text()').get()
            port = node.xpath(u'td[3]/text()').get()
            scheme = node.xpath(u'td[6]/text()').get().lower()
            #
            #
            url = '{}://httpbin.org/ip'.format(scheme)
            proxy = '{}://{}:{}'.format(scheme, ip, port)
            meta = {
                'proxy': proxy,
                'dont_retry': True,
                'download_timeout': 10,
                #
                # 多个字段是传递给 check_available 方法的信息，方便检测
                'ip': ip,
                'scheme': scheme,
            }
            yield scrapy.Request(url = url,
                callback = self.check_available,
                meta = meta,
                dont_filter = True)

    def check_available(self, response):
        if not response.text:
            return
        proxy_ip = response.meta['ip']
        # 判断代理是否具有隐藏ip功能
        origin = json.loads(response.text)['origin']
        # self.logger.debug(">>>>>>>>>>>>>>> httpbin response origin = {}".format(origin))
        if proxy_ip in origin:
            # 都是爬虫需要的高匿代理了
            self.logger.debug('Discover a valid anonymous proxy server: {}'.format(response.meta['proxy']))
            
            # 可以使用 -o 保存为文件，下面就是文件的 字段和值的定义
            yield {
	    		'proxy': response.meta['proxy'],
                'scheme': response.meta['scheme'],
	    	}
    