import unittest
from loki.helpers import type_sniffer

class TypeSnifferTestCase(unittest.TestCase):
    def testiSniffer(self):
        # unicode
        val = "u'test'"
        self.assertEqual(type_sniffer(val), unicode('test'))
        # strings
        val = "'test'"
        self.assertEqual(type_sniffer(val), 'test')
        val = '"test"'
        self.assertEqual(type_sniffer(val), 'test')
        # dict
        val = "{'test':'test'}"
        self.assertEqual(type_sniffer(val), {'test':'test'})
        # lists
        val = 'test1,test2,test3'
        self.assertEqual(type_sniffer(val), ['test1', 'test2' ,'test3'])
        val = "['test1', 'test2' ,'test3']"
        self.assertEqual(type_sniffer(val), ['test1', 'test2' ,'test3'])
        # int
        val = '121345'
        self.assertEqual(type_sniffer(val), 121345)
        # bool
        val = 'true'
        self.assertTrue(type_sniffer(val))
        val = 'false'
        self.assertFalse(type_sniffer(val))
        # None
        val = 'none'
        self.assertEqual(type_sniffer(val), None)
