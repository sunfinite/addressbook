import os
import address_book
import unittest
import tempfile
import json
import logging

class AddressBookTests(unittest.TestCase):

    def setUp(self):
        self.db_fd, address_book.app.config['DATABASE'] = tempfile.mkstemp()
        address_book.app.testing = True
        self.app = address_book.app.test_client()
        # self.app.logger = logging.getLogger('address_book_tests')
        # handler = logging.StreamHandler()
        # self.app.logger.addHandler(handler)
        with address_book.app.app_context():
            address_book.init_db()

    def test_list(self):
        res = self.app.get('/contacts')
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(data['contacts'], [])

    def test_create(self):
        res = self.app.put('/contacts', data=json.dumps({'name': 'Test1'}),
            content_type='application/json')
        self.assertEqual(res.status_code, 500)

    def test_create_delete(self):
        res = self.app.put('/contacts', 
            data=json.dumps({'name': 'Test1', 'email': 'a@b.com'}),
            content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data['id'] > 0)
        res = self.app.delete('/contacts/%d' % data['id'])
        self.assertEqual(res.status_code, 200)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(address_book.app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
