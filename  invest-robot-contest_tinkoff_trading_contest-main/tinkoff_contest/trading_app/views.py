from django.shortcuts import render, redirect
from django.views import View


# Create your views here.


class Welcome(View):

    @staticmethod
    def get(request):
        return render(request, "trading_app/welcome.html")


class Trading(View):

    @staticmethod
    def get(request):
        context = {}
        return render(request, "trading_app/main.html")


class SandBox(View):

    @staticmethod
    def get(request):
        context = {}
        return render(request, "trading_app/main_paper.html")