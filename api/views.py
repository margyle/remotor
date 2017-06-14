import json

from bson import json_util
from django.http.response import JsonResponse
from django.views.generic.base import View

import jobs


class JobsView(View):
    def get(self, request, *args, **kwargs):
        n = request.GET.get('n', 100)
        jobs_collection = jobs.jobs_collection
        jobs_list = list(
            jobs_collection.find().sort('date_added', -1).limit(int(n)))
        return JsonResponse(
            json.dumps(jobs_list, default=json_util.default),
            safe=False
            )
