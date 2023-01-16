import json
from django.shortcuts import render
from django.views import View

from knowledge_base.services.get_strat import get_all_strats


# Create your views here.
class KnowledgeBase(View):

    @staticmethod
    def get(request):
        context = {'Strategies': get_all_strats()}

        return render(request, "knowledge_base/info.html", context)


class Strategies(View):

    @staticmethod
    def get(request, pk=1):
        strategies = get_all_strats()
        strategy = strategies.get(pk=pk)
        context = {
            'Strategy': {
                'Name': strategy.name,
                'Description': strategy.description,
                'Best_stock': strategy.best_stock,
                'Best_profit': strategy.best_profit,
                'ID': pk,
            },
            'Strategies': strategies,
        }
        return render(request, "knowledge_base/strategies.html", context)


class About(View):

    @staticmethod
    def get(request):
        context = {'Strategies': get_all_strats()}
        return render(request, "knowledge_base/about.html", context)


class Contacts(View):

    @staticmethod
    def get(request):
        context = {'Strategies': get_all_strats()}
        return render(request, "knowledge_base/contacts.html", context)