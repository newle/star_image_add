# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisMixin
from star_crawl.items import StarCrawlItem, StarCrawlLoader

#from Html2Text import html_to_text
import re
import logging

import json
from pypinyin import pinyin, lazy_pinyin

import hashlib
def getmd5(str):
  m = hashlib.md5()
  m.update(str)
  return m.hexdigest()

import time
def getstrtime(timestamp):
    x = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S',x)

currenttimestamp = int(time.time())
validrange = 3600*24 + 1000
def validtime(timestamp):
    return timestamp > (currenttimestamp - validrange)




def getpingyin(str):
    py = lazy_pinyin(str)
    return ''.join(py)

def getdetailurl(html_doc):
    html_doc = html_doc.encode("utf8")
    start = html_doc.find("jindun('")
    if start != -1:
        end = html_doc.find("');", start)
        if end != -1:
            return html_doc[start+8: end]

def fetchhtml(url):
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read().decode('gb18030')
    except:
        return ""




idol_detail_regex = re.compile("http://www.1010idol.com/\w+/shiti_id_")
def process_idol_url(value):
    if idol_detail_regex.search(value) is None:
        return None
    return value


#p=2&f=0
def getkv(url, key):
    values = url.split("&")
    for v in values:
        kv = v.split("=")
        if kv[0] == key :
            return kv[1]
    return ""


class idolSpider(RedisMixin, CrawlSpider):
    """Spider that reads urls from redis queue (idol:start_urls)."""
    name = "idoldaily"
    #start_urls = ["http://static.mobile.idol001.com/index/star_info_list.json", ]
    redis_key = "idoldaily:start_urls"
    #rules =  (
    #        Rule(LinkExtractor(process_value = process_idol_url), callback='parse_page', follow=False),
    #)
    
    idols_id = []
    idols_name = {}
    event_name = {}


    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.alowed_domains = filter(None, domain.split(','))
        super(idolSpider, self).__init__(*args, **kwargs)

    def _set_crawler(self, crawler):
        CrawlSpider._set_crawler(self, crawler)
        RedisMixin.setup_redis(self)

    def parse_event(self, response):
        r_json = json.loads(response.body)

        page_idx = getkv(response.url, "page")
        sid  = getkv(response.url, "starid")
        event_id  = getkv(response.url, "xcid")

        if page_idx == "1":
            #get suffix page
            eventnum = r_json['allcount']
            pages = ((eventnum - 1)/30) + 1
            if pages >= 2:
                for i in range(2, pages + 1):
                    eventurl = "http://data.android.idol001.com/api_moblie_idol.php?action=star_xingcheng_gaoqingtu_list&channelId=S002&starid=" + sid + "&page=" + str(i) + "&version=68&xcid=" + event_id
                    eventrequest = Request(eventurl, callback='parse_event', dont_filter=True, priority=1)
                    self.crawler.engine.schedule(eventrequest, spider=self.crawler.spider)

        #parse list
        #"http://data.android.idol001.com/api_moblie_idol.php?action=star_xingcheng_gaoqingtu_list&channelId=S002&starid=6846&page=1&version=68&xcid=55c8193acd4e706d728b462e"
        images = r_json['list']
        for i in range(len(images)):
            group_idx = (int(page_idx) - 1) * 30 + i + 1
            #group_mark = getmd5(response.url)  #单事件多组
            group_mark = event_id   #单事件单组

            image = images[i]
            imgitem = StarCrawlItem()
            imgitem['ori_pic_src'] = image['web_page']
            imgitem['publish_time'] = getstrtime(image['public_time']/1000)
            logging.debug(self.idols_name[int(sid)].encode('gb18030'))
            logging.debug(getpingyin(self.idols_name[int(sid)]))

            imgitem['page_url'] = "http://idol001.com/xingcheng/detail/images/star-" + getpingyin(self.idols_name[int(sid)]) + "-" + sid + "/" + event_id + "/" + page_idx
            imgitem['pic_title'] = self.event_name[event_id]
            imgitem['category'] = u'明星'
            imgitem['tag'] = self.idols_name[int(sid)]
            imgitem['group_mark'] = group_mark
            imgitem['group_idx'] = group_idx
            imgitem['pfrom'] = "51"
            yield imgitem


    def parse_idol_list(self, response):
        r_json = json.loads(response.body)

        page_idx = getkv(response.url, "page")
        sid  = getkv(response.url, "starid")
        #parse list
        #"http://data.android.idol001.com/api_moblie_idol.php?action=star_xingcheng_gaoqingtu_list&channelId=S002&starid=6846&page=1&version=68&xcid=55c8193acd4e706d728b462e"
        events = r_json['list']
        valid = True
        for i in range(len(events)):
            event = events[i]
            event_id = event['_id']
            event_time = event['image']['public_time']
            if validtime(event_time/1000) :
                self.event_name[event_id] = event['action']
                eventurl = "http://data.android.idol001.com/api_moblie_idol.php?action=star_xingcheng_gaoqingtu_list&channelId=S002&starid=" + sid + "&page=1&version=68&xcid=" + event_id
                eventrequest = Request(eventurl, callback='parse_event', dont_filter=True, priority=1)
                self.crawler.engine.schedule(eventrequest, spider=self.crawler.spider)
            else :
                #logging.debug("is event action instance unicode" + " yes" if isinstance(event['action'], unicode) else "no")
                logging.debug(unicode(event_id + u" " + event['action'] + u" is happened at " + getstrtime(event_time/1000) + u" , we will stop at this time").encode('gb18030'))
                valid = False
            #break

        eventnum = r_json['allcount']
        pages = ((eventnum - 1)/10) + 1
        if valid and int(page_idx) < pages:
            nextpageidx = int(page_idx)+1
            idolurl = "http://data.android.idol001.com/api_moblie_idol.php?action=star_tuji_list&starid=" + sid + "&page=" + str(nextpageidx)
            idolrequest = Request(idolurl, callback='parse_idol_list', dont_filter=True, priority=0)
            self.crawler.engine.schedule(idolrequest, spider=self.crawler.spider)




    def parse(self, response):
        #process to get star_id
        r_json = json.loads(response.body)
        #logging.debug(r_json);
        idolfile = open("idol.lst", "w")
        logging.debug("idol totalnum = " + str(len(r_json['list'])))
        for i in range(len(r_json['list'])):
            person = r_json['list'][i]
            self.idols_id.append(person['sid'])
            self.idols_name[person['sid']] = person['name']
            logging.debug(person['sid'])
            logging.debug(person['name'].encode('gb18030'))
            idolfile.write("%s\n" % (person['name'].encode('gb18030'),))
            idolurl = "http://data.android.idol001.com/api_moblie_idol.php?action=star_tuji_list&starid=" + str(person['sid']) + "&page=1"
            idolrequest = Request(idolurl, callback='parse_idol_list', dont_filter=True, priority=0)
            self.crawler.engine.schedule(idolrequest, spider=self.crawler.spider)
            #break
        

        idolfile.flush()

        #for i in range(len(self.idols_id)):
        #    print self.idols_id[i], self.idols_name[self.idols_id[i]].encode('gb18030')

