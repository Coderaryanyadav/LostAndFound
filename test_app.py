"""
Unit & Integration Test Suite for SBMP Lost & Found Application
Runs in-memory using Flask test client.
"""

import os
import unittest
import json
from app import app, init_db, DB_NAME


class LostAndFoundWebTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        init_db()

    def test_01_index_page(self):
        """Verify homepage renders HTML properly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Lost & Found', response.data)

    def test_02_stats_api(self):
        """Verify stats endpoint returns JSON with expected metrics"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('lost_count', data)
        self.assertIn('found_count', data)
        self.assertIn('match_count', data)
        self.assertIn('matches', data)

    def test_03_report_lost_item(self):
        """Test reporting a new lost item via POST /api/lost"""
        payload = {
            'name': 'Test Student',
            'roll': 'CS101',
            'item': 'Scientific Calculator',
            'room': 'Lab 3',
            'category': 'Electronics'
        }
        res = self.client.post('/api/lost', json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json().get('success'))

        # Fetch lost items list
        get_res = self.client.get('/api/lost')
        self.assertEqual(get_res.status_code, 200)
        items = get_res.get_json()
        self.assertGreaterEqual(len(items), 1)
        self.assertEqual(items[0]['item'], 'Scientific Calculator')

    def test_04_report_found_item(self):
        """Test logging a found item via POST /api/found"""
        payload = {
            'finder': 'Campus Security',
            'item': 'Scientific Calculator',
            'room': 'Lab 3',
            'category': 'Electronics'
        }
        res = self.client.post('/api/found', json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json().get('success'))

        # Fetch found items list
        get_res = self.client.get('/api/found')
        self.assertEqual(get_res.status_code, 200)
        items = get_res.get_json()
        self.assertGreaterEqual(len(items), 1)

    def test_05_smart_room_matching(self):
        """Verify room match is detected when room numbers coincide"""
        stats_res = self.client.get('/api/stats')
        data = stats_res.get_json()
        self.assertTrue(data.get('success'))
        self.assertGreaterEqual(data.get('match_count'), 1)

    def test_06_manage_item_resolve_and_delete(self):
        """Verify resolving and deleting an item"""
        # Get latest lost item id
        items = self.client.get('/api/lost').get_json()
        target_id = items[0]['id']

        # Resolve
        put_res = self.client.put(f'/api/item/lost/{target_id}')
        self.assertEqual(put_res.status_code, 200)
        self.assertTrue(put_res.get_json().get('success'))

        # Delete
        del_res = self.client.delete(f'/api/item/lost/{target_id}')
        self.assertEqual(del_res.status_code, 200)
        self.assertTrue(del_res.get_json().get('success'))

    def test_07_export_csv(self):
        """Verify CSV export endpoint returns valid CSV file"""
        response = self.client.get('/api/export')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/csv')
        self.assertIn(b'=== LOST ITEMS ===', response.data)


if __name__ == '__main__':
    unittest.main()
