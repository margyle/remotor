from django.conf import settings
import pymongo


jobsdb = settings.MONGO_DB["jobs"]
jobs_uri = "%s:%s/%s" % (jobsdb["HOST"], jobsdb["PORT"], jobsdb["NAME"])
client = pymongo.MongoClient(
    jobs_uri, connectTimeoutMS=30000, socketTimeoutMS=None, socketKeepAlive=True
)
db = client.get_database()
jobs_collection = db[jobsdb["COLLECTION"]]
