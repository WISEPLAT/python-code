from knowledge_base.models import Strategy


# def get_strat(pk):
#     return Strategy.objects.get(pk=pk)


def get_all_strats():
    return Strategy.objects.all()