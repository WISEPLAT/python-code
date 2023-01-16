import time
from tinkoff.invest import Client, MoneyValue, Quotation, OrderDirection, OrderType

figi_usd = "BBG0013HGFT4"
figi_Microsoft = "BBG000BPH459"
figi_Tesla = "BBG000N9MNX3"

# confidential information

token = ""
account_id = ""

sandbox_token = token


# function converts MoneyValue into float
def convert_price(MoneyValue):
    price = MoneyValue.units + (MoneyValue.nano / 10**9)
    return price


# function converts float into MoneyValue
def convert_to_MoneyValue(price, currency='rub'):
    units = price // 1
    nano = (price % 1) * 10**9
    return MoneyValue(units=units, nano=nano, currency=currency)


# function gets info about current Limit Order Book
def get_LOB_data(figi_0=figi_usd):

    with Client(token) as client:
        LOB = client.market_data.get_order_book(figi=figi_0, depth=50)

        ask_price = convert_price(LOB.asks[0].price)
        bid_price = convert_price(LOB.bids[0].price)

        q_a = 0
        q_b = 0

        for line in LOB.asks:
            q_a += line.quantity
        for line in LOB.bids:
            q_b += line.quantity

        return ((q_b, q_a), (bid_price, ask_price))


# function converts float into Quotation
def convert_to_Quotation(price, currency='rub'):
    units = int(price // 1)
    nano = int((price % 1) * 10**9)
    return Quotation(units=units, nano=nano)


# class consists of two models: last+im and last+im+v strategy
class model_1:
    def __init__(self):
        self.cur_best_bid_price = 0
        self.cur_best_ask_price = 0

        self.last_best_bid_price = 0
        self.last_best_ask_price = 0

        self.bid_quantity = 0
        self.ask_quantity = 0

        self.ask_price = 0
        self.bid_price = 0

        self.increment = 0.1
        self.auto_increment_flag = 1
        self.parameter = 0.5 #default parameter value
        self.state = 0

        self.colors = dict()
        self.color_match = dict()

        self.colors["red"] = "\033[1;31m"
        self.colors["green"] = "\033[1;32m"
        self.colors["blue"] = "\033[1;34m"
        self.colors["clear"] = "\033[0;0;m"

        self.color_match[0] = self.colors["blue"]
        self.color_match[1] = self.colors["green"]
        self.color_match[-1] = self.colors["red"]

    def set_parameters(self, param=0.5, increm=0):
        self.parameter = param
        if increm != 0:
            self.auto_increment_flag = 0
            self.increment = increm

    def update_prices_b_a(self, bid_price, ask_price):

        self.last_best_bid_price = self.cur_best_bid_price
        self.last_best_ask_price = self.cur_best_ask_price

        self.cur_best_bid_price = bid_price
        self.cur_best_ask_price = ask_price

        if self.auto_increment_flag:
            self.increment = ask_price - bid_price

    def update_LOB_data_b_a(self, b_q, a_q):
        self.bid_quantity = b_q
        self.ask_quantity = a_q

    def last_im_strategy(self):
        value_1 = self.bid_quantity - self.ask_quantity
        value_2 = -value_1
        value_3 = self.ask_quantity + self.bid_quantity

        last_price = (self.cur_best_ask_price + self.cur_best_bid_price)/2

        if value_1/value_3 > self.parameter: #(qb -qs)/(qb +qs)>0.5
            self.ask_price = last_price + self.increment * 2
            self.bid_price = last_price
            self.state = 1

        elif value_2/value_3 > self.parameter: #(qs –qb)/(qb +qs) >0.5
            self.ask_price = last_price
            self.bid_price = last_price - self.increment * 2
            self.state = -1

        else:
            self.ask_price = last_price + self.increment
            self.bid_price = last_price - self.increment
            self.state = 0

        print(self.color_match[self.state], end="")
        print("last+im strategy")
        print("signals: ----", end=' ')
        print(self.bid_price, self.ask_price, sep=" : ", end='')
        print(self.colors["clear"])

        return (self.bid_price, self.ask_price)

    def last_im_v_strategy(self):
        value_1 = self.bid_quantity - self.ask_quantity
        value_2 = -value_1
        value_3 = self.ask_quantity + self.bid_quantity

        last_price = (self.cur_best_ask_price + self.cur_best_bid_price) / 2
        previous_price = (self.last_best_ask_price + self.last_best_bid_price) / 2

        price_change = abs(last_price - previous_price)

        if value_1 / value_3 > self.parameter:  # (qb -qs)/(qb +qs)>0.5
            self.ask_price = last_price + (price_change + 2) * self.increment
            self.bid_price = last_price - price_change * self.increment
            self.state = 1


        elif value_2 / value_3 > self.parameter:  # (qs –qb)/(qb +qs) >0.5
            self.ask_price = last_price + price_change * self.increment
            self.bid_price = last_price - (price_change + 2) * self.increment
            self.state = -1


        else:
            self.ask_price = last_price + (price_change + 1) * self.increment
            self.bid_price = last_price - (price_change + 1) * self.increment
            self.state = 0


        print(self.color_match[self.state], end="")
        print("last+im+v strategy")
        print("signals: ----", end=' ')
        print(self.bid_price, self.ask_price, sep=" : ", end='')
        print(self.colors["clear"])


        return (self.bid_price, self.ask_price)


# class simulates real time activity of the model, placing orders in the sandbox.
class SandboxTester:
    def __init__(self, account_id, token, figi, model=model_1(), model_type="last_im_strategy", limit_quantity=10000000, limit_percentage=100, iterations=1000):
        model_types = dict()

        model_types["last_im_strategy"] = 1
        model_types["last_im_v_strategy"] = 2

        if model_types[model_type] is None:
            raise Exception("Model type does not exist. Existing types: last_im_strategy, last_im_v_strategy")
        else:
            self.model_type = model_types[model_type]

        self.account_id = account_id
        self.token = token
        self.working_figi = figi
        self.limit_quantity = limit_quantity
        self.limit_percentage = limit_percentage
        self.model = model
        self.iterations = iterations

        from model_1_hft import get_LOB_data

        with Client(token=self.token) as client:
            client_sb = client.sandbox

            self.moneeey = client_sb.get_sandbox_portfolio(account_id=self.account_id).total_amount_currencies
            time.sleep(0.6)

            self.money_float = convert_price(self.moneeey)
            max_quantity = convert_price(self.moneeey)
            last_price = client.market_data.get_last_prices(figi=[self.working_figi]).last_prices[0].price
            time.sleep(0.6)

            self.last_price = convert_price(last_price)
            self.max_quantity = max_quantity // self.last_price

        self.cur_balance = self.money_float

    def model_run(self):
        if self.model_type == 1:
            return self.model.last_im_strategy()
        elif self.model_type == 2:
            return self.model.last_im_v_strategy()
        else:
            return None

    def update_balance(self):
        with Client(token=self.token) as client:
            client_sb = client.sandbox
            self.cur_balance = client_sb.get_sandbox_portfolio(account_id=self.account_id).total_amount_currencies
            self.cur_balance = convert_price(self.cur_balance)
            print(self.cur_balance)
            print("////////")
            time.sleep(0.6)
            # print(client_sb.get_sandbox_portfolio(account_id=self.account_id))

    def place_order_ask(self, price, quantity, time_c=0):
        if time_c > 3:
            return "ASK order was NOT EXECUTED"

        try:
            with Client(token=self.token) as client:
                r = client.sandbox.post_sandbox_order(
                    figi=self.working_figi,
                    price=price,
                    x_app_name="naketu.HFT",
                    quantity=quantity,
                    account_id=self.account_id,
                    order_id="sfkjhsf234897kjsdfh8has8dy3827gdslu[]" + str(time.localtime()),
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_LIMIT
                )

            time.sleep(0.6)
            return r

        except:
            time.sleep(0.6)
            time_c += 0.6

            print("ERROR OCCURED AT ASK POST ORDER, reposting...")

            r = self.place_order_bid(price, quantity, time_c)
            return r

    def place_order_bid(self, price, quantity, time_c=0):
        if time_c > 3:
            return "BID order was NOT EXECUTED"

        try:
            with Client(token=self.token) as client:

                r = client.sandbox.post_sandbox_order(
                    figi=self.working_figi,
                    price=price,
                    #appname="naketu.HFT",
                    quantity=quantity,
                    account_id=self.account_id,
                    order_id="sfkjhsf234897kjsdfh8has8dy3827gdslu[]" + str(time.localtime()),
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_LIMIT
                )

            time.sleep(0.6)
            return r

        except:
            time.sleep(0.6)
            time_c += 0.6

            print("ERROR OCCURED AT BID POST ORDER, reposting...")

            r = self.place_order_bid(price, quantity, time_c)
            return r

    def cancel_order(self, order_id):
        with Client(token=self.token) as client:
            try:
                r = client.sandbox.cancel_sandbox_order(
                    account_id=self.account_id,
                    order_id=order_id,
                )
                time.sleep(0.6)
            except:
                r = "ORDER IS NOT CANCELED"
            return r

    def check_orders(self, last_bid_price, bid_price, last_ask_price, ask_price):
        with Client(token=self.token) as client:
            orders = client.sandbox.get_sandbox_orders(account_id=self.account_id)
            time.sleep(0.6)

            if last_bid_price != bid_price and last_ask_price != ask_price:
                return orders.orders
            elif last_bid_price != bid_price:
                orders = [ord for ord in orders.orders if ord.direction == OrderDirection.ORDER_DIRECTION_BUY]
                return orders
            elif last_ask_price != ask_price:
                orders = [ord for ord in orders.orders if ord.direction == OrderDirection.ORDER_DIRECTION_SELL]
                return orders
            else:
                return []

    def test(self):
        time_c = 0

        last_bid_price = 0
        last_ask_price = 0

        try:
            old_LOB = get_LOB_data(self.working_figi)
            time.sleep(0.6)
        except:
            raise Exception("NO CONNECTION TO MARKET")

        for i in range(self.iterations):

            self.update_balance()

            try:
                LOB_data = get_LOB_data(self.working_figi)
            except:
                print("LOB does not responding")
                time.sleep(2)
                time_c += 2
                print("loading...", time_c)
                continue

            if old_LOB[0][0] == LOB_data[0][0] and old_LOB[0][1] == LOB_data[0][1]:
                continue
            else:
                self.model.update_LOB_data_b_a(LOB_data[0][0], LOB_data[0][1])
                self.model.update_prices_b_a(LOB_data[1][0], LOB_data[1][1])

                cur_price = (LOB_data[1][0] + LOB_data[1][1])/2

                response = self.model_run()

                bid_price = convert_to_Quotation(response[0])
                ask_price = convert_to_Quotation(response[1])

                orders = self.check_orders(last_bid_price, bid_price, last_ask_price, ask_price)

                if len(orders) != 0:
                    for order in orders:
                        self.cancel_order(order.order_id)

                quantity = int(min(self.limit_percentage/100 * self.money_float,
                                   self.limit_quantity, self.cur_balance // cur_price))

                self.place_order_ask(ask_price, quantity // 2),
                self.place_order_bid(bid_price, quantity // 2)

                # print(self.place_order_ask(ask_price, quantity // 2),
                #       self.place_order_bid(bid_price, quantity // 2))

                last_bid_price = bid_price
                last_ask_price = ask_price

                time.sleep(0.6)


""" 
The function simulates trading session and outputs order prices that are given out by the strategies states in model_1.
However, the function does not post any orders. Colored lines represent the results of the algorithm,
where blue, red and green represent steady state of the order book, greater amount of ask and bid orders respectively.
"""
def algo_trade(figi="BBG0013HGFT4"):

    BEST_MODEL_EVER = model_1()

    working_figi = figi

    try: old_LOB = get_LOB_data(working_figi)
    except:
        print("WARNING")
        print()

    time_c = 0

    print("start")

    for i in range(1000):

        try: LOB_data = get_LOB_data(working_figi)
        except:
            print("i am dead")
            print("Too many calls ERROR")
            time.sleep(2)
            time_c += 2
            print("loading...", time_c)
            continue

        if (old_LOB == None) or (old_LOB[0][0] == LOB_data[0][0] and old_LOB[0][1] == LOB_data[0][1]):
            time.sleep(0.6)
            time_c += 0.6
            print("loading...", time_c)

        else:
            time_c = 0
            print("///////////////////////////")

            print("quantity: ---", LOB_data[0][0], LOB_data[0][1])
            print("prices: -----", LOB_data[1][0], LOB_data[1][1])

            BEST_MODEL_EVER.update_LOB_data_b_a(LOB_data[0][0], LOB_data[0][1])
            BEST_MODEL_EVER.update_prices_b_a(LOB_data[1][0], LOB_data[1][1])

            response1 = BEST_MODEL_EVER.last_im_strategy()
            response2 = BEST_MODEL_EVER.last_im_v_strategy()

            print("///////////////////////////")

            time.sleep(0.6)
            time_c += 0.6

        old_LOB = LOB_data


def sandbox_quick_start(figi=figi_usd):
    model_1_test = model_1()
    tester_0 = SandboxTester(account_id, token, figi, model_1_test, "last_im_strategy", 1000, 10, 10000)
    tester_0.test()


def pay_in():
    with Client(token=token) as client:
        client_sb = client.sandbox
        client_sb.sandbox_pay_in(account_id=account_id, amount=MoneyValue(units=100000, nano=0, currency='rub'))


"""QUICK START:
  Comment out one of the functions below and input initial values for token and account_id at the beginning of the file
  If current trading balance is zero, you can add 100000 rub there by initiating pay_in() function """


# algo_trade(figi_Tesla)
# sandbox_quick_start(figi_Tesla)
