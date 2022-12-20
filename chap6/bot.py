import requests
from time import sleep
import random
import json

def generate_order():
    return {
  	"order_id": id(random.random()) + random.random(),
  	"order_type":random.choice(["market", "limit","limit","limit","limit","limit","limit","limit","limit","limit"]),
  	"order_size": random.randint(1, 100),
  	"order_price": random.randint(1, 100), # will be ignored if the order type is market
  	"order_direction": random.choice(["buy", "sell"]),
   }

for i in range(5000):
    order = generate_order()
    res = requests.post('http://localhost:8080/submit', 
                        data = json.dumps(order))
    # print(res.json())