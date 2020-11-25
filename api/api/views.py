from django.http import HttpResponse
from django.views.generic import TemplateView


class PutView(TemplateView):

    def post(self, request):
        print(request.POST.__dict__)
        return HttpResponse("OK", status=200)
