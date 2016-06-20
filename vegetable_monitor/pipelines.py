# -*- coding: utf-8 -*-
import couchdb
from scrapy.log import logger
import json
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class VegetableMonitorPipeline(object):

    def open_spider(self, spider):
        self.db_name = spider.name
        self.db = CloudantDB(self.db_name)
        self.client = self.db.server

    def close_spider(self, spider):
        # the database connection do not need to close
        pass

    def process_item(self, item, spider):
        if spider.name == "sattellite":
            doc = {'date': item['date']}
            self.db.save(doc)
            self.db.put_attachment(doc, item['image'], filename='image.jpg')
        else:
            self.db.store(dict(item))
        return item


class CloudantDB(couchdb.client.Database):
    def __init__(self, name):
        self.db_name = name
        couchdb.client.Database.__init__(self, None)
        self.init()

    def init(self):
        logger.debug("Initial the database")

        try:
            CREDIT = json.load(open('./vegetable_monitor/vcap.json'))[
                'cloudantDB']['credentials']
            self.server = couchdb.Server(CREDIT['url'])
            self.server.resource.credentials = (CREDIT['username'],
                                                CREDIT['password'])
            try:
                db = self.server.create(self.db_name)
                logger.debug("Create a new database " + self.db_name)
            except:
                db = self.server.__getitem__(self.db_name)
                logger.debug("Use Data Base" + self.db_name)

            logger.debug("Create datadase successfully")
            self.__dict__.update(db.__dict__)
        except:
            print('cannot find the credentials pls bind a CloudantDB Service')

        return self
        # Query results are treated as iterators, like this:
        # print all docs in the database

    def query_massage(self, params):
        params = ''
        # params should fit this format
        # this is a wrapper of the cochdb map function
        # ref: http://www.slideshare.net/okurow/couchdb-mapreduce-13321353
        map_fun = '''
        function(doc) {
        if (doc.id == "message_count") {
            if (doc.message_count.push >= %s ) {
                emit(doc)
                }
            }
        }
        '''.format(str(params['push']))
        return self.query(map_fun)

    def store(self, data):
        self.save(data)

if __name__ == '__main__':
    pass
