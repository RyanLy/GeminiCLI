#!/usr/bin/python3

# python3 gemini.py status | jq

import base64
import datetime
import hashlib
import hmac
import json
import os
import time
import argparse

import requests

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY').encode()
GEMINI_API_SECRET = os.getenv('GEMINI_API_SECRET').encode()
CLIENT_ORDER_ID = 'Python V1'

ETH_USD_SYMBOL = 'ethusd'
BTC_USD_SYMBOL = 'btcusd'

APPROVED_SYMBOL_PAIRS = [ETH_USD_SYMBOL, BTC_USD_SYMBOL]

# Helpers
def print_json(response):
    print(json.dumps(response.json(), indent=2))

def generate_nonce():
    t = datetime.datetime.now()
    return str(int(time.mktime(t.timetuple()) * 1000))

def post_request(url, payload):
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(GEMINI_API_SECRET, b64, hashlib.sha384).hexdigest()
    request_headers = {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'X-GEMINI-APIKEY': GEMINI_API_KEY,
        'X-GEMINI-PAYLOAD': b64,
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': "no-cache"
    }

    return requests.post(url, headers=request_headers)

# APIs
def get_orders():
    url = "https://api.gemini.com/v1/orders"
    payload = {
        "request": "/v1/orders",
        "nonce": generate_nonce()
    }

    response = post_request(url, payload)
    print_json(response)

# new_order(symbol = ETH_USD_SYMBOL, amount = 1, price = 500, side = 'buy')
# python3 gemini.py buy ethusd 4 1100
# python3 gemini.py buy btcusd 0.1 10000
def new_order(symbol, amount, price, side, stop=False):
    request_endpoint = "/v1/order/new"
    url = "https://api.gemini.com" + request_endpoint
    payload = {
        "request": request_endpoint,
        "nonce": generate_nonce(),
        "client_order_id": CLIENT_ORDER_ID,
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "side": side,
        "type": "exchange stop limit" if stop else "exchange limit"
    }

    if stop:
        payload["stop"] = price

    response = post_request(url, payload)
    print_json(response)


def cancel_order(order_id):
    request_endpoint = "/v1/order/cancel"
    url = "https://api.gemini.com" + request_endpoint
    payload = {
        "request": request_endpoint,
        "order_id": order_id,
        "nonce": generate_nonce(),
    }

    response = post_request(url, payload)
    print_json(response)


def cancel_all():
    request_endpoint = "/v1/order/cancel/all"
    url = "https://api.gemini.com" + request_endpoint
    payload = {
        "request": request_endpoint,
        "nonce": generate_nonce()
    }

    response = post_request(url, payload)
    print_json(response)

def past_trades(symbol_pair, limit=5):
    request_endpoint = "/v1/mytrades"
    url = "https://api.gemini.com" + request_endpoint
    payload = {
        "request": request_endpoint,
        "nonce": generate_nonce(),
        "symbol": symbol_pair,
        "limit_trades": limit
    }

    response = post_request(url, payload)
    print_json(response)

def main():
    parser = argparse.ArgumentParser(description='Gemini command line tool')

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    subparsers.add_parser(
        'status', help='Get status of active orders')

    buy_parser = subparsers.add_parser('buy', help='Create a new buy order')
    buy_parser.add_argument('symbol_pair', type=str,
                            help='symbol pair', choices=APPROVED_SYMBOL_PAIRS)
    buy_parser.add_argument('amount', type=float)
    buy_parser.add_argument('price', type=float)
    buy_parser.add_argument('--stop', action='store_true',
                            help='whether this is a stop limit')


    sell_parser = subparsers.add_parser('sell', help='Create a new sell order')
    sell_parser.add_argument('symbol_pair', type=str,
                            help='symbol pair', choices=APPROVED_SYMBOL_PAIRS)
    sell_parser.add_argument('amount', type=float)
    sell_parser.add_argument('price', type=float)
    sell_parser.add_argument('--stop', action='store_true',
                            help='whether this is a stop limit')


    cancel_parser = subparsers.add_parser('cancel', help='Cancel orders')
    group = cancel_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('order_id', nargs='?', type=str, default=None)
    group.add_argument(
        '--all', action='store_true', help='whether to cancel all orders')

    past_trades_parser = subparsers.add_parser('past', help='Past trades')
    past_trades_parser.add_argument('symbol_pair', type=str,
                        help='symbol pair', choices=APPROVED_SYMBOL_PAIRS)

    args = parser.parse_args()

    command = args.command

    if command == 'status':
        get_orders()
    elif command == 'cancel':
        if args.order_id:
            cancel_order(args.order_id)
        elif args.all:
            cancel_all()
    elif command == 'buy' or command == 'sell':
        prompt = '[{command}] {amount} {symbol_pair} @ ${price}. Total= ${total}. Stop limit = {stop}. Are you sure? (y/n)\n'.format(
            command=command, amount=args.amount, symbol_pair=args.symbol_pair, price=args.price, total=args.amount * args.price, stop=args.stop)
        if input(prompt) == 'y':
            new_order(symbol=args.symbol_pair, amount=args.amount,
                    price=args.price, side=command, stop=args.stop)
    elif command == 'past':
        past_trades(args.symbol_pair)

if __name__=="__main__":
    main()
