# -*- coding: utf-8 -*-
import scrapy
from news.items import NewsItem
from news.dealstr import cleanStr,getStr
from news.dealurl import getUrl,filterUrl,textUrl
import time

class XinhuaSpider(scrapy.Spider):
    name = "xinhua"
    allowed_domains = ["xinhuanet.com"]
    start_urls = (
        'http://www.xinhuanet.com/',
    )
    filter = []

    def parse(self, response):
        suffix = ['htm']
        urls = textUrl(response,suffix)
        urls = filterUrl(urls,self.filter)
        for url in urls:
            yield scrapy.Request(url, callback=self.parse3)

    def parse3(self,response):
        item = NewsItem()
        #url
        item['news_url'] = response.url
        #title
        title = response.xpath('//title/text()').extract()
        if title != []:
            title = title[0].replace(',','').replace(' ','').replace('\n','')
            #标题过滤
            title = title.split('_')[0].split('-')[0].split('|')[0]
            item['news_title'] = title
        else:
            item['news_title'] = ''
        #abstract & body
        abstract = response.xpath('//p/text()').extract()
        if abstract != []:
            x = [cleanStr(i) for i in abstract if len(i.replace(' ','')) > 20]
            if x != []:
                text = getStr(x)
                if u'\u3011' in text:
                    item['news_abstract'] = text.split(u'\u3011')[-1]
                else:
                    item['news_abstract'] = text
                #新闻正文
                s = ''
                for i in x:
                    s += i
                item['news_body'] = s.replace(' ','').replace('\n','').replace('\t','')
            else:
                item['news_abstract'] = title
                item['news_body'] = title
        else:
            item['news_abstract'] = title
            item['news_body'] = title
        #time
        item['news_time'] = time.time()
        yield item
