from flask import Flask
from flask import request, jsonify
import json
import time

from orderbook import OrderBook
orderbook = OrderBook()

app = Flask(__name__)

@app.route('/submit',  methods = ['POST'])
def process_order():
    order = request.get_json(force=True)
    order["submit_timestamp"] = time.time()
    orderbook.receive_order(order)
    orderbook.print_orderbook()
    return jsonify({"status": "received"})
    
def main():
    app.run(host='localhost', port=8080, debug=True)
    
    
if __name__ == '__main__':
    main()