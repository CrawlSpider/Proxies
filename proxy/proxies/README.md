# Proxies
![](https://img.shields.io/badge/python3-passing-brightgreen.svg)

- 学习通过免费网站获取免费代理信息
- 学习通过 httpbin 验证代理有效性
- 学习异常处理

### 运行
- scrapy crawl xcip -o proxies.json
    从 [西刺免费代理](https://www.xicidaili.com/)  获取高匿代理
- scrapy crawl ftip -o proxies.json
    从 [高可用全球免费代理IP库](https://www.freeip.top/?anonymity=2) 获取高匿代理（推荐）

### 说明
- 免费代理通常有效期比较短
- 免费代理提供网站会实时更新代理信息
- 由于以上原因一次过多获取原始代理信息毫无意义，因此代码里明确指定仅爬取前 5 页
- 免费代理网站通常会限制爬虫访问，我在 settings 中默认了一些参数来限制速度

