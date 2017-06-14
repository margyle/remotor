from django.http.response import HttpResponse
from django.views.generic.base import View


class JobsView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('jobs list')
