import couchdb
import setting


class CloudantDB(couchdb.client.Database):
    def __init__(self, name):
        self.db_name = name
        couchdb.client.Database.__init__(self, None)
        self.init()

    def init(self):
        print "Initial the database"
        couch = couchdb.Server("https://%s.cloudant.com" %
                               setting.CREDIT['username'])
        couch.resource.credentials = (setting.CREDIT['username'],
                                      setting.CREDIT['password'])
        try:
            db = couch.create(self.db_name)
            print "Create a new database " + self.db_name
        except:
            db = couch.__getitem__(self.db_name)
            print "Use Data Base" + self.db_name

        print "Create datadase successfully"
        self.__dict__.update(db.__dict__)
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
