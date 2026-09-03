"""
Unit and Integration Tests for Aro Bastin Portfolio Contact API
Run with: python -m unittest discover tests
"""
import sys
from pathlib import Path
from unittest.mock import patch
import unittest
import json

# Add parent directory to path so app can be imported directly
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import app, limiter

class ContactApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        limiter.enabled = False  # Disabled for functional validation tests

    def tearDown(self):
        limiter.enabled = True

    def test_health_check(self):
        """Test GET /api/health returns 200 and ok status"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('status'), 'ok')

    @patch('app.send_email_notification')
    def test_valid_submission(self, mock_send_email):
        """Test POST /api/contact succeeds with valid inputs and mocked email sending"""
        mock_send_email.return_value = True
        payload = {
            'name': 'Sarah Recruiter',
            'email': 'sarah@techcompany.com',
            'message': 'Hello Aro, we are impressed by your Full Stack portfolio and would like to discuss opportunities.'
        }
        response = self.client.post('/api/contact', json=payload)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('message'), 'Message sent successfully.')
        mock_send_email.assert_called_once()

    def test_missing_name(self):
        """Test POST /api/contact fails when name is missing"""
        payload = {
            'email': 'recruiter@techcompany.com',
            'message': 'We are hiring for Full Stack Developer roles.'
        }
        response = self.client.post('/api/contact', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get('success'))
        self.assertIn('name', data.get('message', '').lower())

    def test_missing_email(self):
        """Test POST /api/contact fails when email is missing"""
        payload = {
            'name': 'Sarah Recruiter',
            'message': 'We are hiring for Full Stack Developer roles.'
        }
        response = self.client.post('/api/contact', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get('success'))
        self.assertIn('email', data.get('message', '').lower())

    def test_invalid_email_format(self):
        """Test POST /api/contact fails when email format is invalid"""
        payload = {
            'name': 'Sarah Recruiter',
            'email': 'not-a-valid-email',
            'message': 'We are hiring for Full Stack Developer roles.'
        }
        response = self.client.post('/api/contact', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get('success'))
        self.assertIn('email', data.get('message', '').lower())

    def test_missing_message(self):
        """Test POST /api/contact fails when message is missing"""
        payload = {
            'name': 'Sarah Recruiter',
            'email': 'sarah@company.com'
        }
        response = self.client.post('/api/contact', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get('success'))
        self.assertIn('message', data.get('message', '').lower())

    def test_short_message(self):
        """Test POST /api/contact fails when message is under minimum length"""
        payload = {
            'name': 'Sarah Recruiter',
            'email': 'sarah@company.com',
            'message': 'Hi'
        }
        response = self.client.post('/api/contact', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get('success'))
        self.assertIn('5 characters', data.get('message', ''))

    def test_excessively_long_message(self):
        """Test POST /api/contact fails when message exceeds 5000 characters"""
        payload = {
            'name': 'Sarah Recruiter',
            'email': 'sarah@company.com',
            'message': 'A' * 5001
        }
        response = self.client.post('/api/contact', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get('success'))
        self.assertIn('5000 characters', data.get('message', ''))

    def test_invalid_json(self):
        """Test rejection of non-JSON requests"""
        response = self.client.post('/api/contact', data='not json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get('success'))

    def test_honeypot_spam_trap(self):
        """Test honeypot returns silent 200 without sending email to trap bots"""
        payload = {
            'name': 'Spam Bot',
            'email': 'bot@spammer.org',
            'message': 'Buy cheap crypto ranking boost.',
            '_honeypot': 'I am a bot'
        }
        response = self.client.post('/api/contact', json=payload)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))

    @patch('app.send_email_notification')
    def test_rate_limiting_active(self, mock_send_email):
        """Test that rate limiter triggers 429 when limit is exceeded with mocked email sending"""
        mock_send_email.return_value = True
        limiter.enabled = True
        payload = {
            'name': 'Sarah',
            'email': 'sarah@company.com',
            'message': 'Testing rate limit threshold.'
        }
        status_codes = []
        for _ in range(6):
            res = self.client.post('/api/contact', json=payload)
            status_codes.append(res.status_code)
        
        self.assertIn(429, status_codes)

if __name__ == '__main__':
    unittest.main()
