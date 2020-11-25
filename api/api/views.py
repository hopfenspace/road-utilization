from django.http import HttpResponse
from django.views.generic.base import View


class PutView(View):

    def get(self, request, *args, **kwargs):
        print(request.GET)
        return HttpResponse("", status=200)

    def post(self, request):
        print(request.POST)
        return HttpResponse("OK", status=200)
