#!/usr/bin/env python
# encoding: utf-8

import unittest

import mock

from zabbixapi import zabbix_session

CHECKS_RESPONSE = (
    'ZBXD\x01S\x00\x00\x00\x00\x00\x00\x00'
    '{"response":"success","data":[{"key":"test","delay":30,"lastlogsize":0,"mtime":0}]}'
)
SENDER_REQUEST_HEADER = b'ZBXD\x01\x86\x00\x00\x00\x00\x00\x00\x00'
SENDER_DATA = {
    "data": [{"host": "lyc_test", "value": 33136016, "key": "test", "clock": 1486631773}],
    "request": "sender data", "clock": 1486631777,
}
SENDER_RESPONSE = (
    'ZBXD\x01Z\x00\x00\x00\x00\x00\x00\x00'
    '{"response":"success",'
    '"info":"processed: 1; failed: 0; total: 1; seconds spent: 0.000055"}'
)


class TestZabbixSession(unittest.TestCase):
    def test_pack_json(self):
        session = zabbix_session.ZabbixSession("127.0.0.1")
        self.assertEqual(session.pack_json(SENDER_DATA)[:13], SENDER_REQUEST_HEADER)

    def test_get_active_checks(self):
        mock_socket = mock.MagicMock()
        with mock.patch("socket.socket", return_value=mock_socket):
            mock_socket.recv.return_value = CHECKS_RESPONSE
            session = zabbix_session.ZabbixSession("127.0.0.1")
            session.connect()
            result = session.get_active_checks("host_name")
            self.assertEqual(result.response, "success")
            item = result.items[0]
            self.assertEqual(item.key, "test")
            self.assertEqual(item.delay, 30)
            self.assertEqual(item.lastlogsize, 0)
            self.assertEqual(item.mtime, 0)

    def test_send_data(self):
        mock_socket = mock.MagicMock()
        with mock.patch("socket.socket", return_value=mock_socket):
            mock_socket.recv.return_value = SENDER_RESPONSE
            session = zabbix_session.ZabbixSession("127.0.0.1")
            session.connect()
            result = session.send_data(SENDER_DATA)
            self.assertEqual(result.response, "success")
            self.assertEqual(result.processed, "1")
            self.assertEqual(result.failed, "0")
            self.assertEqual(result.total, "1")
            self.assertEqual(result.seconds_spent, "0.000055")
