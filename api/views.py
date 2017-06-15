import json

from bson import json_util
from django.http.response import JsonResponse
from django.views.generic.base import View

import jobs


class JobsView(View):
    def get(self, request, *args, **kwargs):
        n = request.GET.get('n', 10)
        p = request.GET.get('p', 1)
        techs = request.GET.get('techs', [])
        exclude = request.GET.get('exclude', [])
        if techs or exclude:
            search = {'technologies': {}}
            if techs:
                search['technologies'].update({'$in': techs.split(',')})
            if exclude:
                search['technologies'].update({'$nin': exclude.split(',')})
        else:
            search = None
        skip = int(n) * int(p) - int(n)
        jobs_collection = jobs.jobs_collection
        found_jobs = jobs_collection.find(
                skip=skip,
                filter=search,
                ).sort('date_added', -1)
        response = {'count': found_jobs.count()}
        response['pages'] = found_jobs.count() // n + 1
        found_jobs = list(found_jobs.limit(int(n)))
        response['jobs'] = found_jobs
        return JsonResponse(
            json.dumps(response, default=json_util.default),
            safe=False
            )
