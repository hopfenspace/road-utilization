import json

from django.http import HttpResponse
from django.views.generic.base import View


class PutView(View):

    def post(self, request):
        print(json.loads(request.body))
        return HttpResponse("OK", status=200)
