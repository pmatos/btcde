#! /usr/bin/env python
"""This Module provides the functions from bitcoin.de Trading API"""

import requests
import time
import json
import hmac
import hashlib
import logging
import codecs

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

__version__ = '2.0'

# disable unsecure SSL warning
requests.packages.urllib3.disable_warnings()


def HandleRequestsException(e):
    """Handle Exception from request."""
    log.warning('{}: {}'.format(e[0][0], e[0][1]))


def HandleAPIErrors(r):
    """To handle Errors from BTCDE API."""
    valid_status_codes = [200, 201, 204]
    if r.status_code not in valid_status_codes:
        reader = codecs.getreader("utf-8")
        content = json.load(reader(r.raw))
        errors = content.get('errors')
        log.warning('API Error Code: {}'.format(str(errors[0]['code'])))
        log.warning('API Error Message: {}'.format(errors[0]['message']))
        log.warning('API Error URL: {}'.format(r.url))
        return False
    else:
        return True


class Connection:
    """To provide connection credentials to the trading API"""
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        # set initial self.nonce
        self.nonce = int(time.time())
        # Bitcoin.de API URI
        self.apihost = 'https://api.bitcoin.de'
        self.apiversion = 'v2'
        self.valid_trading_pair = ['btceur', 'bcheur', 'etheur']
        self.valid_order_type = ['buy', 'sell']
        self.valid_currency = ['btc', 'bch', 'eth']
        self.orderuri = self.apihost + '/' + self.apiversion + '/' + 'orders'
        self.tradeuri = self.apihost + '/' + self.apiversion + '/' + 'trades'
        self.accounturi = self.apihost + '/' + self.apiversion + '/' + 'account'

    def create_url(self, params, uri):
        encoded_string = ''
        for key, value in sorted(params.items()):
            encoded_string += str(key) + '=' + str(value) + '&'
        encoded_string = encoded_string[:-1]
        url = uri + '?' + encoded_string
        return url, encoded_string        

    def params_url(self, params, uri):
        if params:
            url, encoded_string = self.create_url(params, uri)
        else:
            encoded_string = ''
            url = uri
        return url, encoded_string

    def build_hmac_sign(self, md5string, method, url):
        hmac_data = '{method}#{url}#{key}#{nonce}#{md5}'\
                    .format(method=method, url=url,
                            key=self.api_key, nonce=str(self.nonce),
                            md5=md5string)
        hmac_signed = hmac.new(bytearray(self.api_secret.encode()), msg=hmac_data.encode(), digestmod=hashlib.sha256).hexdigest()
        return hmac_signed
        
    def set_header(self, url, method, encoded_string):
        # raise self.nonce before using
        self.nonce += 1
        if method == 'POST':
            md5_encoded_query_string = hashlib.md5(encoded_string.encode()).hexdigest()
        else:
            md5_encoded_query_string = hashlib.md5(b'').hexdigest()
        hmac_signed = self.build_hmac_sign(md5_encoded_query_string,
                                           method, url)
        # set header
        header = {'content-type':
                  'application/x-www-form-urlencoded; charset=utf-8',
                  'X-API-KEY': self.api_key,
                  'X-API-NONCE': str(self.nonce),
                  'X-API-SIGNATURE': hmac_signed }
        return header

    def send_request(self, url, method, header, encoded_string):
        if method == 'GET':
            r = requests.get(url, headers=(header),
                             stream=True, verify=False)
        elif method == 'POST':
            r = requests.post(url, headers=(header), data=encoded_string,
                              stream=True, verify=False)
        elif method == 'DELETE':
            r = requests.delete(url, headers=(header),
                                stream=True, verify=False)
        return r

    def APIConnect(self, method, params, uri):
        """Transform Parameters to URL"""
        url, encoded_string = self.params_url(params, uri)
        header = self.set_header(url, method, encoded_string)
        log.debug('Set Header: {}'.format(header))
        try:
            r = self.send_request(url, method, header, encoded_string)
            # Handle API Errors
            if HandleAPIErrors(r):
                # get results
                result = r.json()
            else:
                result = {}
        except requests.exceptions.RequestException as e:
            HandleRequestsException(e)
            result = {}
        return result


    def showOrderbook(self, OrderType, trading_pair, **args):
        """Search Orderbook for offers."""
        # Build parameters
        if OrderType in self.valid_order_type and trading_pair in self.valid_trading_pair:
            params = {'type': OrderType, 'trading_pair': trading_pair}
        else:
            print('problem')
        params.update(args)
        return self.APIConnect('GET', params, self.orderuri)


    def createOrder(self, OrderType, trading_pair, max_amount, price, **args):
        """Create a new Order."""
        # Build parameters
        params = {'type': OrderType, 'max_amount': max_amount, 'price': price, 'trading_pair': trading_pair}
        params.update(args)
        return self.APIConnect('POST', params, self.orderuri)


    def deleteOrder(self, order_id, trading_pair):
        """Delete an Order."""
        newuri = self.orderuri + "/" + order_id + "/" + trading_pair
        params = {}
        return self.APIConnect('DELETE', params, newuri)


    def showMyOrders(self, **args):
        """Query and Filter own Orders."""
        newuri = self.orderuri + '/my_own'
        return self.APIConnect('GET', args, newuri)


    def showMyOrderDetails(self, order_id):
        """Details to an own Order."""
        newuri = self.orderuri + '/' + order_id
        params = {}
        return self.APIConnect('GET', params, newuri)


    def executeTrade(self, order_id, OrderType, trading_pair, amount):
        """Buy/Sell on a specific Order."""
        newuri = self.tradeuri + '/' + order_id
        params = {'order_id': order_id, 'type': OrderType, 'trading_pair': trading_pair, 'amount': amount}
        return self.APIConnect('POST', params, newuri)


    def showMyTrades(self, **args):
        """Query and Filter on past Trades."""
        return self.APIConnect('GET', args, self.tradeuri)


    def showMyTradeDetails(self, trade_id):
        """Details to a specific Trade."""
        newuri = self.tradeuri + '/' + trade_id
        params = {}
        return self.APIConnect('GET', params, newuri)


    def showAccountInfo(self):
        """Query on Account Infos."""
        params = {}
        return self.APIConnect('GET', params, self.accounturi)


    def showOrderbookCompact(self, trading_pair):
        """Bids and Asks in compact format."""
        params = {'trading_pair': trading_pair}
        return self.APIConnect('GET', params, self.orderuri + '/compact')


    def showPublicTradeHistory(self, trading_pair, since_tid=None):
        """All successful trades of the las 7 days."""
        if since_tid is not None:
            params = {'trading_pair': trading_pair, 'since_tid': since_tid}
        else:
            params = {'trading_pair': trading_pair}
        return self.APIConnect('GET', params, self.tradeuri + '/history')


    def showRates(self, trading_pair):
        """Query of the average rate last 3 and 12 hours."""
        newuri = self.apihost + '/' + self.apiversion + '/rates'
        params = {'trading_pair': trading_pair}
        return self.APIConnect('GET', params, newuri)


    def showAccountLedger(self, currency, **args):
        """Query on Account statement."""
        params = {'currency': currency}
        params.update(args)
        args.update()
        return self.APIConnect('GET', params, self.accounturi + '/ledger')
