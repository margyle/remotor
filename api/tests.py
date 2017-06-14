from django.test import TestCase
import pymongo

from django.conf import settings


class TestMongoDBJobs(TestCase):
    """Live test for the MongoDB database."""
    def setUp(self):
        jobsdb = settings.MONGO_DB['jobs']
        jobs_uri = '%s:%s/%s' % (jobsdb['HOST'], jobsdb['PORT'], jobsdb['NAME'])
        client = pymongo.MongoClient(
            jobs_uri,
            connectTimeoutMS=30000,
            socketTimeoutMS=None,
            socketKeepAlive=True
            )
        db = client.get_default_database()
        self.jobs_collection = db[jobsdb['COLLECTION']]

    def test_get_jobs(self):
        """Test we can get the online jobs collection directly."""
        n = self.jobs_collection.count()
        self.assertTrue(n > 100)


class TestJobsAPI(TestCase):
    """Test we can get results from our MongoDB using our API."""
    def test_get_jobs(self):
        response = self.client.get('/api/v1/jobs/')
        self.assertEqual(response.status_code, 200)

    def test_post_jobs(self):
        response = self.client.post('/api/v1/jobs/')
        self.assertEqual(response.status_code, 405)
