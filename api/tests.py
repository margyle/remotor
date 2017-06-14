import json

from django.test import TestCase

from .jobs import jobs_collection


class TestMongoDBJobs(TestCase):
    """Live test for the MongoDB database."""
    def setUp(self):
        self.jobs_collection = jobs_collection

    def test_get_jobs(self):
        """Test we can get the online jobs collection directly."""
        n = self.jobs_collection.count()
        self.assertTrue(n > 100)


class TestJobsAPI(TestCase):
    """Test we can get results from our MongoDB using our API."""
    def test_get_jobs(self):
        """Test that GET is allowed."""
        response = self.client.get('/api/v1/jobs/')
        jobs = json.loads(response.json())
        self.assertTrue('title' in jobs[0])
        self.assertEqual(len(jobs), 100)

    def test_post_jobs(self):
        """Test that POST is not allowed."""
        response = self.client.post('/api/v1/jobs/')
        self.assertEqual(response.status_code, 405)

    def test_get_n_jobs(self):
        """Test that GET returns expected number of results."""
        response = self.client.get('/api/v1/jobs/?n=10')
        jobs = json.loads(response.json())
        self.assertEqual(len(jobs), 10)
