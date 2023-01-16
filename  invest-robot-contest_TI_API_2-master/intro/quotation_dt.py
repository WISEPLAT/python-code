import tinkoff.invest

def quotation_count(quot):
    return quot.units + quot.nano / 1e9

# В разработке
# def moneyvalue_count(quot):
#
#     if quot.currency == "rub":
#         return quot.units + quot.nano / 1e9
#     elif quot.currency == "usd":
#         return quot.units + quot.nano / 1e9
