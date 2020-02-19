# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class DemoSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class DemoDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)



from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
import json
import random
import re
class RandomHttpProxyMiddleware(HttpProxyMiddleware):
    #
    # refer to "scrapy\downloadermiddlewares\httpproxy.py"
    def __init__(self, auth_encoding = 'latin-1', proxy_list_file = None):
        if not proxy_list_file:
            raise NotConfigured

        self.auth_encoding = auth_encoding
        self.proxies = []
        '''
        This is the json file format to be loaded
        [
            {"scheme":"https","proxy":"https://xx.xx.xx.xx:port"},
            ...
            {"scheme":"https","proxy":"http://user:passwd@xx.xx.xx.xx:port"},
            {"scheme":"http","proxy":"http://xx.xx.xx.xx:port"}
        ]
        '''
        with open(proxy_list_file) as f:
            proxy_list = json.loads(f.read())
            for proxy in proxy_list:
                scheme = proxy['scheme']
                url = proxy['proxy']
                self.proxies.append(self._get_proxy(url, scheme))

    #
    #
    @classmethod
    def from_crawler(cls, crawler):
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING', 'latin-1')
        # HTTPPROXY_PROXY_LIST_FILE is defined in the settings.py file
        proxy_list_file = crawler.settings.get("HTTPPROXY_PROXY_LIST_FILE")
        return cls(auth_encoding, proxy_list_file)
    #
    #
    def process_request(self, request, spider):
        #
        # ignore if proxy is already set
        if 'proxy' in request.meta:
            if request.meta['proxy'] is None:
                return
            # extract credentials if present
            
            creds, proxy_url = self._get_proxy(request.meta['proxy'], '')
            request.meta['proxy'] = proxy_url
            if creds and not request.headers.get('Proxy-Authorization'):
                request.headers['Proxy-Authorization'] = b'Basic ' + creds
            return
        elif not self.proxies:
            return
        #
        # the second parameter is not used
        if len(self.proxies):
            self._set_proxy(request, 'http')
        else:
            return
    #
    #
    def _set_proxy(self, request, scheme):
        #
        creds, proxy = random.choice(self.proxies)
        request.meta['proxy'] = proxy
        if creds:
            request.headers['Proxy-Authorization'] = b'Basic' + creds


#
#
from twisted.internet import defer
from twisted.web.client import ResponseFailed
from twisted.internet.error import TimeoutError, DNSLookupError,\
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from scrapy.http import HtmlResponse
from scrapy.core.downloader.handlers.http11 import TunnelError
class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
        ConnectionRefusedError, ConnectionDone, ConnectError,
        ConnectionLost, TCPTimedOutError, ResponseFailed,
        IOError, TunnelError)
    def process_exception(self,request,exception,spider):
        
        if isinstance(exception, self.ALL_EXCEPTIONS):
            spider.logger.error('Got Exception: {}'.format(exception))
            
            response = HtmlResponse(url='exception')
            return response
        spider.logger.error('Not contained exception: {}'.format(exception))

#
#
#
from fake_useragent import UserAgent
class RandomUserAgentMiddlware(object):
    # random user-agent
    def __init__(self,crawler):
        super(RandomUserAgentMiddlware,self).__init__()
        self.ua = UserAgent()

    @classmethod
    def from_crawler(cls,crawler):
        return cls(crawler)

    def process_request(self,request,spider):
        request.headers.setdefault('User-Agent', self.ua.random)