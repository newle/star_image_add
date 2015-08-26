# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import logging
#mysql -h"pic01.ss.mysql.db.sogou-op.org" -u chanpinyunying -pm6i1m2a3 --database="pic_tiny"

class StarCrawlPipeline(object):
    def __init__(self):
        self.m_dbconn = MySQLdb.connect("pic01.ss.mysql.db.sogou-op.org", "chanpinyunying","m6i1m2a3","pic_tiny", charset='utf8', use_unicode=False)
        self.m_dbcur = self.m_dbconn.cursor()
        self.m_insertQuery = "insert into test_recommend_image_(ori_pic_src, pic_title, page_url, page_title, publish_time, tag, category, pfrom, group_index, group_mark) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        self.m_testQuery = "select (1) from test_recommend_image_ where ori_pic_src = %s limit 1;"

    def varified(self, item):
        #if item['ori_pic_src'][idx].find(".gif") == -1 and item['ori_pic_src'][idx].find(".png") == -1:
        #    return False
        return True


    def process_item(self, item, spider):
        #insert into mysql db
        while True:
            try:
                 #test Variaty
                if not self.varified(item):
                    logging.debug(item['ori_pic_src'] + " is not varified!")
                    return None
            
                if self.m_dbcur.execute(self.m_testQuery, (item['ori_pic_src'], )):
                    logging.debug(item['ori_pic_src'] + " has in db before we insert!")
                else:
                    logging.debug("update to server " + item['page_url'])
                    self.m_dbcur.execute(self.m_insertQuery, (
                        item['ori_pic_src'],
                        item['pic_title'],
                        item['page_url'],
                        item['pic_title'],
                        item['publish_time'],
                        item['tag'],
                        item['category'],
                        item['pfrom'],
                        item['group_idx'],
                        item['group_mark']))
                    self.m_dbconn.commit()
                    logging.debug("update to server " + item['page_url'])
                break
            except Exception, e:
                logging.debug(e)
                self.m_dbconn = MySQLdb.connect("pic01.ss.mysql.db.sogou-op.org", "chanpinyunying","m6i1m2a3","pic_tiny", charset='utf8', use_unicode=False)
                self.m_dbcur = self.m_dbconn.cursor()

        #return item
        return None

