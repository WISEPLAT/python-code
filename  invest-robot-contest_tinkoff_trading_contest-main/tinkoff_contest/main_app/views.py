from django.shortcuts import render
from django.views import View


# Create your views here.
class MainPage(View):

    @staticmethod
    def get(request):
        return render(request, "main_app/main.html")