# Proxies
![](https://img.shields.io/badge/python3-passing-brightgreen.svg)

- 学习给爬虫使用代理
- 学习使用多代理

### 运行
- scrapy crawl test

### 说明
scrapy 中使用代理的方法归纳来说有三种：
#### 1. 使用环境变量

    环境变量添加 http_proxy 或者 https_proxy    
    例如：exprot http_proxy='http://ip:prot'   

#### 2. 在 Request 时临时添加代理
``` py
    meta = {
        'proxy': proxy,
            .
            .
            .
    }
    yield scrapy.Request(url = url,
        callback = self.xxxxx,
        meta = meta,
        dont_filter = True)
```
请参考我的另一个 [代理爬取和验证](https://github.com/CrawlSpider/Proxies/blob/11fe655a9c96948968aab225d8e5d1dd648e8fbf/proxy/proxies/proxies/spiders/xcip.py#L54) 的学习代码片段

#### 3. 在 middlewares.py 文件中增加中间件
- 这种方式最为方便，一劳永逸
- 可以做到多个代理按策略启用    
1. 使用外部代理列表文件，文件格式如下：
```py
 [
    {"proxy": "http://188.56.194.202:8080", "scheme": "http"},
    {"proxy": "https://188.56.194.202:8080", "scheme": "https"},
    {"proxy": "https://user:passwd@188.56.194.202:8080", "scheme": "https"}
]
```
2. middlewares.py 文件中定义新的中间件，用于加载这个代理列表文件，并且请求时按策略选择一个代理并启用
```py
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
        # 暂时的策略时每次请求都随机挑选一个使用
        creds, proxy = random.choice(self.proxies)
        request.meta['proxy'] = proxy
        if creds:
            request.headers['Proxy-Authorization'] = b'Basic' + creds
```
    4. settings 中启用
```py
HTTPPROXY_PROXY_LIST_FILE = 'proxies.json'
DOWNLOADER_MIDDLEWARES = {
    'demo.middlewares.RandomHttpProxyMiddleware': 745,
}
```
### 4 遗留问题
1. 代理失效时如何自动重试 或者 更换代理再重试
1. 如何选择可靠的代理
1. 使用免费代理时，各种异常会比较多，面对每种异常如何针对性的可靠优雅的处理 以及 策略
