# -*- coding: utf-8 -*-
import couchdb
import logging
from scrapy.log import logger
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class VegetableMonitorPipeline(object):

    def __init__(self, db_name):
        self.db_name = db_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_name=crawler.settings.get('BOT_NAME')
        )

    def open_spider(self, spider):
        self.client = CloudantDB(self.db_name)
        self.db = self.client[self.db_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db.store(item)
        return item


class CloudantDB(couchdb.client.Database):
    def __init__(self, name):
        self.db_name = name
        couchdb.client.Database.__init__(self, None)

        self.init()

    def init(self):
        logger.debug("Initial the database")
        try:
            CREDIT = json.loads(os.environ.get("VCAP_SERVICES"))['cloudantNoSQLDB'][0]['credentials']
            couch = couchdb.Server("https://%s.cloudant.com" %
                                setting.CREDIT['username'])
            couch.resource.credentials = (setting.CREDIT['username'],
                                        setting.CREDIT['password'])
            try:
                db = couch.create(self.db_name)
                logger.debug("Create a new database " + self.db_name)
            except:
                db = couch.__getitem__(self.db_name)
                logger.debug("Use Data Base" + self.db_name)

            logger.debug("Create datadase successfully")
            self.__dict__.update(db.__dict__)
        except:
            logger.error('cannot find the credentials pls bind a CloudantDB Service')

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
