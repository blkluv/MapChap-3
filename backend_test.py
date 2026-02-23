#!/usr/bin/env python3
"""
MapChap Backend API Testing Suite
Tests all critical API endpoints for the Telegram Mini App
"""

import requests
import json
import sys
from datetime import datetime

class MapChapAPITester:
    def __init__(self, base_url="https://d5djdb4t6ohnfrpfaaic.ql6wied2.apigw.yandexcloud.net/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_id = 987654321  # Test Telegram ID
        self.created_offer_id = None

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, params=params, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"   Error: {error_data}")
                except:
                    self.log(f"   Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        return self.run_test("Health Check", "GET", "/health", 200)

    def test_categories(self):
        """Test categories endpoint"""
        success, data = self.run_test("Categories", "GET", "/categories", 200)
        if success and data.get('categories'):
            self.log(f"   Found {len(data['categories'])} categories")
        return success, data

    def test_telegram_auth(self):
        """Test Telegram authentication"""
        auth_data = {
            "id": self.test_user_id,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "photo_url": "",
            "language_code": "ru"
        }
        success, data = self.run_test("Telegram Auth", "POST", "/auth/telegram", 200, auth_data)
        if success and data.get('user'):
            self.log(f"   User created/updated: {data['user'].get('first_name')}")
        return success, data

    def test_manual_verification(self):
        """Test manual business verification"""
        verification_data = {
            "company_name": "Test Business",
            "phone": "+79991234567",
            "email": "test@business.com",
            "social_type": "telegram",
            "social_username": "@testbusiness"
        }
        params = {"telegram_id": self.test_user_id}
        success, data = self.run_test("Manual Verification", "POST", "/verification/manual", 200, 
                                    verification_data, params)
        if success:
            self.log(f"   Business verification successful")
        return success, data

    def test_create_offer(self):
        """Test creating a business offer"""
        offer_data = {
            "title": "Test Restaurant",
            "description": "A great test restaurant",
            "full_description": "Full description of our test restaurant with all amenities",
            "category": "food",
            "address": "Москва, Красная площадь, 1",
            "phone": "+79991234567",
            "email": "info@testrestaurant.com",
            "website": "https://testrestaurant.com",
            "working_hours": "9:00-22:00",
            "coordinates": [55.7558, 37.6176],  # Red Square coordinates
            "amenities": ["wifi", "parking", "card_payment"]
        }
        params = {"telegram_id": self.test_user_id}
        success, data = self.run_test("Create Offer", "POST", "/offers", 200, offer_data, params)
        if success and data.get('id'):
            self.created_offer_id = data['id']
            self.log(f"   Offer created with ID: {self.created_offer_id}")
            # Verify coordinates are saved correctly
            coords = data.get('coordinates')
            if coords and len(coords) == 2:
                self.log(f"   Coordinates saved: [{coords[0]}, {coords[1]}]")
            else:
                self.log(f"   ⚠️ Coordinates format issue: {coords}")
        return success, data

    def test_get_offers(self):
        """Test getting all offers"""
        success, data = self.run_test("Get All Offers", "GET", "/offers", 200)
        if success:
            offers = data.get('offers', [])
            self.log(f"   Found {len(offers)} offers")
            # Check if our created offer is in the list
            if self.created_offer_id:
                found = any(o.get('id') == self.created_offer_id for o in offers)
                if found:
                    self.log(f"   ✅ Created offer found in list")
                else:
                    self.log(f"   ⚠️ Created offer not found in list")
            
            # Check coordinates format for all offers
            for offer in offers[:3]:  # Check first 3 offers
                coords = offer.get('coordinates')
                if coords and isinstance(coords, list) and len(coords) == 2:
                    self.log(f"   Offer '{offer.get('title')}' coordinates: [{coords[0]}, {coords[1]}]")
                else:
                    self.log(f"   ⚠️ Offer '{offer.get('title')}' has invalid coordinates: {coords}")
        return success, data

    def test_get_user_offers(self):
        """Test getting user's offers"""
        success, data = self.run_test("Get User Offers", "GET", f"/offers/user/{self.test_user_id}", 200)
        if success:
            offers = data.get('offers', [])
            self.log(f"   User has {len(offers)} offers")
        return success, data

    def test_get_single_offer(self):
        """Test getting a single offer by ID"""
        if not self.created_offer_id:
            self.log("⚠️ Skipping single offer test - no offer ID available")
            return True, {}
        
        params = {"telegram_id": self.test_user_id}
        success, data = self.run_test("Get Single Offer", "GET", f"/offers/{self.created_offer_id}", 200, params=params)
        if success:
            self.log(f"   Offer title: {data.get('title')}")
            self.log(f"   Views: {data.get('views', 0)}")
        return success, data

    def test_telegram_webhook(self):
        """Test Telegram webhook endpoint"""
        webhook_data = {
            "message": {
                "chat": {"id": self.test_user_id},
                "from": {"id": self.test_user_id, "first_name": "Test"},
                "text": "/start"
            }
        }
        success, data = self.run_test("Telegram Webhook", "POST", "/telegram/webhook", 200, webhook_data)
        return success, data

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("🚀 Starting MapChap Backend API Tests")
        self.log(f"📡 Testing API: {self.base_url}")
        
        # Basic functionality tests
        self.test_health_check()
        self.test_categories()
        
        # Authentication and user management
        self.test_telegram_auth()
        self.test_manual_verification()
        
        # Offer management (core business logic)
        self.test_create_offer()
        self.test_get_offers()
        self.test_get_user_offers()
        self.test_get_single_offer()
        
        # Telegram integration
        self.test_telegram_webhook()
        
        # Print results
        self.log(f"\n📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            self.log("🎉 All tests passed!")
            return 0
        else:
            self.log("❌ Some tests failed")
            return 1

def main():
    tester = MapChapAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())