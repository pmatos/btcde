from unittest import TestCase 
from mock import patch
import btcde


class TestBtcdeApi(TestCase):
    """Test Api Functions."""
    
    def setUp(self):
        self.patcher = patch('btcde.APIConnect')
        self.mock_APIConnect = self.patcher.start()
    
    def tearDown(self):
        self.patcher.stop()
    
    def assertArguments(self, expected_arguments, mock_APIConnect):
        for idx, expected in enumerate(expected_arguments):
            actual = mock_APIConnect.call_args[0][idx]
            self.assertEqual(actual, expected,
                             'Argument {} with value {} '
                             'does not match expected {}'.format(idx,
                                                                 actual,
                                                                 expected))
    
    def test_showOrderbook_buy_and_sell(self):
        methods = 'buy', 'sell'
        for method in methods:
            result = btcde.showOrderbook('mock', method)
            expected_arguments = ['mock', 'GET', {'type': method}, btcde.orderuri]
            self.assertArguments(expected_arguments, self.mock_APIConnect)
    
    def test_createOrder(self):
        OrderType = 'now'
        max_amount = 5
        price = 10
        result = btcde.createOrder('mock', OrderType, max_amount, price)
        params = {'type': OrderType, 'max_amount': max_amount, 'price': price}
        expected_arguments = ['mock', 'POST', params, btcde.orderuri]
        self.assertArguments(expected_arguments, self.mock_APIConnect)

    def test_deleteOrder(self):
        order_id = '42'
        result = btcde.deleteOrder('mock', order_id)
        params = {'order_id': order_id}
        expected_arguments = ['mock', 'DELETE', params, btcde.orderuri + "/" + order_id]
        self.assertArguments(expected_arguments, self.mock_APIConnect)
                                                             
    def test_showMyOrders(self):
        result = btcde.showMyOrders('mock')
        expected_arguments = ['mock', 'GET', {}, btcde.orderuri + '/my_own']
        self.assertArguments(expected_arguments, self.mock_APIConnect)

    def test_showMyOrderDetails(self):
        order_id = '42'
        result = btcde.showMyOrderDetails('mock', order_id)
        params = {'order_id': order_id}
        expected_arguments = ['mock', 'GET', params, btcde.orderuri + '/' + order_id]
        self.assertArguments(expected_arguments, self.mock_APIConnect)
                                                             
    def test_executeTrade(self):
        order_id = '42'
        OrderType = 'foobar'
        amount = '73'
        result = btcde.executeTrade('mock', order_id, OrderType, amount)
        params = {'order_id': order_id, 'type': OrderType, 'amount': amount}
        expected_arguments = ['mock', 'POST', params, btcde.tradeuri + '/' + order_id]
        self.assertArguments(expected_arguments, self.mock_APIConnect)

    def test_showMyTrades(self):
        result = btcde.showMyTrades('mock')
        expected_arguments = ['mock', 'GET', {}, btcde.tradeuri]
        self.assertArguments(expected_arguments, self.mock_APIConnect)
        
    def test_showMyTradeDetails(self):
        trade_id = '42'
        result = btcde.showMyTradeDetails('mock', trade_id)
        params = {'trade_id': trade_id}
        expected_arguments = ['mock', 'GET', params, btcde.tradeuri + '/' + trade_id]
        self.assertArguments(expected_arguments, self.mock_APIConnect)

    def test_showAccountInfo(self):
        result = btcde.showAccountInfo('mock')
        params = {}
        expected_arguments = ['mock', 'GET', params, btcde.accounturi]
        self.assertArguments(expected_arguments, self.mock_APIConnect)

    def test_showOrderbookCompact(self):
        result = btcde.showOrderbookCompact('mock')
        params = {}
        expected_arguments = ['mock', 'GET', params, btcde.orderuri + '/compact']
        self.assertArguments(expected_arguments, self.mock_APIConnect)

    def test_showPublicTradeHistory(self):
        result1 = btcde.showPublicTradeHistory('mock')
        params = {}
        expected_arguments = ['mock', 'GET', params, btcde.tradeuri + '/history']
        self.assertArguments(expected_arguments, self.mock_APIConnect)
        self.tearDown()
        self.setUp()
        since_tid = '3'
        params = {'since_tid': since_tid}
        result2 = btcde.showPublicTradeHistory('mock', since_tid)
        expected_arguments = ['mock', 'GET', params, btcde.tradeuri + '/history']
        self.assertArguments(expected_arguments, self.mock_APIConnect) 

    def test_showRates(self):
        result = btcde.showRates('mock')
        params = {}
        expected_arguments = ['mock', 'GET', params, btcde.apihost + '/' + btcde.apiversion + '/rates']
        self.assertArguments(expected_arguments, self.mock_APIConnect)

    def test_showAccountLedger(self):
        result = btcde.showAccountLedger('mock')
        expected_arguments = ['mock', 'GET', {}, btcde.accounturi + '/ledger']
        self.assertArguments(expected_arguments, self.mock_APIConnect)

class TestSimpleFunctions(TestCase):
    
    def test_params_url(self):
        sample_params = { 'foo': 'bar', 'bar': 'foo'}
        result = btcde.params_url(sample_params, 'https://foo.bar')
        expected_result = 'https://foo.bar?bar=foo&foo=bar'
        self.assertEquals(result, expected_result)
    
    def test_params_url_wo_params(self):
        result = btcde.params_url({}, 'https://foo.bar')
        expected_result = 'https://foo.bar'
        self.assertEquals(result, expected_result)
        
        
class TestApiConnect(TestCase):
    
    def setUp(self):
        self.patcher = patch('requests')
        self.mock_APIConnect = self.patcher.start()
    
    def tearDown(self):
        self.patcher.stop()
    

