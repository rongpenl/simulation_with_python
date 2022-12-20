from collections import defaultdict
import numpy as np

class OrderBook:
    def __init__(self):
        self.buy_orders = defaultdict(list)
        self.sell_orders = defaultdict(list)
        self.latest_ordr = None
    
    def receive_order(self, order):
        if order["order_type"] == "market":
            order["order_price"] = np.inf if order["order_direction"] == "buy" else -np.inf
                # willing to buy at extreme high price
        if order["order_direction"] == "buy":
            self.buy_orders[order["order_price"]].append(
                order)
        else:
            self.sell_orders[order["order_price"]].append(
                order)
        
        self.latest_order = order
        self.fulfill_orders()
        
    def fulfill_orders(self):
            """
            # When this method runs, there should be only one of the following three cases possible.
            1. There is one and only one market order that can be executed with the tip of the opposite side
            2. There is no market order
                2.1 There is no matching opposite orders
                2.2 The latest limited order can be executed by fulfilling the orders 
                    on the opposite side one by one

            The three cases are mutually exclusive so we will handle that one by one.
            """
            latest_order = self.latest_order.copy()
            
            opposite_orderbook = self.buy_orders if latest_order[
                "order_direction"] == "sell" else self.sell_orders

            if latest_order["order_direction"] == "buy":
                opposite_prices = sorted(opposite_orderbook.keys())
            else:
                opposite_prices = sorted(opposite_orderbook.keys(), reverse=True)
            
            for opposite_price in opposite_prices:
                
                valid_buy = latest_order["order_direction"] == "buy" and opposite_price <= latest_order["order_price"]
                
                valid_sell = latest_order["order_direction"] == "sell" and opposite_price >= latest_order["order_price"]
                
                valid = (valid_buy or valid_sell) and latest_order["order_size"] > 0
                
                if not valid:
                    break

                for queued_order in opposite_orderbook[opposite_price]:            
                    if queued_order["order_size"] <= latest_order["order_size"]:
                        latest_order["order_size"] -= queued_order["order_size"]
                        
                        if latest_order["order_direction"] == "buy":
                            self.buy_orders[latest_order["order_price"]][-1]["order_size"] -= queued_order["order_size"]
                        else:
                            self.sell_orders[latest_order["order_price"]][-1]["order_size"] -= queued_order["order_size"]                   

                        fill_size = queued_order["order_size"]
                        queued_order["order_size"] = 0

                    elif latest_order["order_size"] > 0:
                        # print("the latest order is not big enough to eat the current queued order")
                        queued_order["order_size"] -= latest_order["order_size"]
                        
                        fill_size = latest_order["order_size"]
                        # mark the latest_order completely fulfilled.
                        latest_order["order_size"] = 0 
                        # the latest order will always be the last one. Set its size to 0 since it is depleted now.
                        if latest_order["order_direction"] == "buy":
                            self.buy_orders[latest_order["order_price"]][-1]["order_size"] = 0 
                        else:
                            self.sell_orders[latest_order["order_price"]][-1]["order_size"] = 0
    
                        # at this moment, the latest order size should be 0.
                    
                    else:
                        break    
            self.clean_limit_orderbook()
    
    def clean_limit_orderbook(self):
        """
        Remove useless keys in the limit orderbook
        """
        for orderbook in [self.buy_orders, self.sell_orders]:
            empty_prices = []
            for price in orderbook.keys():
                new_orders = list(filter(lambda order: order["order_size"] > 0, orderbook[price]))
                if len(new_orders) == 0:
                    empty_prices.append(price)
                else:
                    orderbook[price] = new_orders
            
            for price in empty_prices:
                del orderbook[price]
    
    def print_orderbook(self):
        print("-------------------Orderbook-------------------")
        for price in sorted(self.sell_orders.keys(), reverse= True):
            depth = sum(map(lambda order: order["order_size"], self.sell_orders[price]))
            print("sell side price: {}, depth: {}".format(price, depth))
        print("-----------------------------------------------")
        for price in sorted(self.buy_orders.keys(),reverse= True):
            depth = sum(map(lambda order: order["order_size"], self.buy_orders[price]))
            print("buy side price: {}, depth: {}".format(price, depth))
        print("\n")

