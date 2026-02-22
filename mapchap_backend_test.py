#!/usr/bin/env python3
"""
MapChap Backend API Testing Suite
Tests the specific issues mentioned in the review request:
1. Telegram authorization API
2. INN verification API  
3. Manual verification API
4. Offer creation and retrieval APIs
5. Map coordinates functionality
"""

import requests
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

class MapChapAPITester:
    def __init__(self, base_url: str = "https://d5djdb4t6ohnfrpfaaic.ql6wied2.apigw.yandexcloud.net"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.test_user_id = None
        self.created_offers = []
        
        print(f"🚀 Starting MapChap Backend API Tests")
        print(f"📡 Base URL: {base_url}")
        print("=" * 60)

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "response_data": response_data
        })

    def test_health_check(self) -> bool:
        """Test basic API health"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status')}, Version: {data.get('version')}"
            else:
                details = f"Status code: {response.status_code}"
            
            self.log_test("Health Check", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_telegram_auth(self) -> bool:
        """Test Telegram authentication API - POST /api/auth/telegram"""
        try:
            # Generate a unique test user
            test_id = int(str(uuid.uuid4().int)[:9])  # 9-digit ID
            self.test_user_id = test_id
            
            auth_data = {
                "id": test_id,
                "first_name": "Test",
                "last_name": "User",
                "username": "test_user",
                "photo_url": "",
                "language_code": "ru"
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/telegram",
                json=auth_data,
                timeout=15
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if data.get('success') and data.get('user'):
                    user = data['user']
                    details = f"User created: {user.get('first_name')} (ID: {user.get('telegram_id')})"
                    # Verify user structure
                    required_fields = ['id', 'telegram_id', 'first_name', 'role', 'is_verified']
                    missing_fields = [field for field in required_fields if field not in user]
                    if missing_fields:
                        success = False
                        details = f"Missing user fields: {missing_fields}"
                else:
                    success = False
                    details = "Invalid response structure"
            else:
                details = f"Status: {response.status_code}"
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('error', 'Unknown')}"
                except:
                    pass
            
            self.log_test("Telegram Auth API", success, details, response.json() if success else None)
            return success
            
        except Exception as e:
            self.log_test("Telegram Auth API", False, f"Exception: {str(e)}")
            return False

    def test_inn_verification(self) -> bool:
        """Test INN verification API - POST /api/verification/inn"""
        if not self.test_user_id:
            self.log_test("INN Verification API", False, "No test user available")
            return False
            
        try:
            # Test with valid Russian INN format
            test_inn = "7707083893"  # Valid format INN
            
            response = requests.post(
                f"{self.base_url}/api/verification/inn?telegram_id={self.test_user_id}",
                json={"inn": test_inn},
                timeout=15
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if data.get('success') and data.get('verification'):
                    verification = data['verification']
                    details = f"Company: {verification.get('name')}, INN: {verification.get('inn')}"
                    
                    # Check verification structure
                    required_fields = ['inn', 'name']
                    missing_fields = [field for field in required_fields if field not in verification]
                    if missing_fields:
                        success = False
                        details = f"Missing verification fields: {missing_fields}"
                else:
                    success = False
                    details = "Invalid response structure"
            else:
                details = f"Status: {response.status_code}"
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('error', 'Unknown')}"
                except:
                    pass
            
            self.log_test("INN Verification API", success, details, response.json() if success else None)
            return success
            
        except Exception as e:
            self.log_test("INN Verification API", False, f"Exception: {str(e)}")
            return False

    def test_manual_verification(self) -> bool:
        """Test manual verification API - POST /api/verification/manual"""
        if not self.test_user_id:
            self.log_test("Manual Verification API", False, "No test user available")
            return False
            
        try:
            verification_data = {
                "company_name": "Test Company LLC",
                "phone": "+7 999 123 45 67",
                "email": "test@company.com",
                "social_type": "telegram",
                "social_username": "@test_company"
            }
            
            response = requests.post(
                f"{self.base_url}/api/verification/manual?telegram_id={self.test_user_id}",
                json=verification_data,
                timeout=15
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if data.get('success'):
                    details = f"Manual verification successful: {data.get('message', 'OK')}"
                else:
                    success = False
                    details = "Verification failed"
            else:
                details = f"Status: {response.status_code}"
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('error', 'Unknown')}"
                except:
                    pass
            
            self.log_test("Manual Verification API", success, details, response.json() if success else None)
            return success
            
        except Exception as e:
            self.log_test("Manual Verification API", False, f"Exception: {str(e)}")
            return False

    def test_create_offer(self) -> bool:
        """Test offer creation API - POST /api/offers"""
        if not self.test_user_id:
            self.log_test("Create Offer API", False, "No test user available")
            return False
            
        try:
            # Test coordinates in [lat, lng] format as mentioned in the context
            offer_data = {
                "title": "Test Coffee Shop",
                "description": "Best coffee in town for testing",
                "full_description": "A comprehensive description of our test coffee shop with all amenities",
                "category": "food",
                "address": "Тестовая улица, 123, Москва",
                "phone": "+7 999 123 45 67",
                "email": "test@coffeeshop.com",
                "website": "https://testcoffee.com",
                "working_hours": "9:00-21:00",
                "coordinates": [55.751244, 37.618423],  # [lat, lng] format
                "amenities": ["wifi", "parking", "card_payment"],
                "tags": ["coffee", "breakfast", "cozy"]
            }
            
            response = requests.post(
                f"{self.base_url}/api/offers?telegram_id={self.test_user_id}",
                json=offer_data,
                timeout=15
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if data.get('id'):
                    self.created_offers.append(data['id'])
                    details = f"Offer created: {data.get('title')} (ID: {data.get('id')})"
                    
                    # Verify coordinates are stored correctly
                    coords = data.get('coordinates')
                    if coords and len(coords) == 2:
                        details += f", Coordinates: [{coords[0]}, {coords[1]}]"
                    else:
                        print(f"⚠️  Warning: Coordinates format issue: {coords}")
                        
                    # Check required fields
                    required_fields = ['id', 'title', 'description', 'category', 'address', 'coordinates']
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        success = False
                        details = f"Missing offer fields: {missing_fields}"
                else:
                    success = False
                    details = "No offer ID returned"
            else:
                details = f"Status: {response.status_code}"
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('error', 'Unknown')}"
                except:
                    pass
            
            self.log_test("Create Offer API", success, details, response.json() if success else None)
            return success
            
        except Exception as e:
            self.log_test("Create Offer API", False, f"Exception: {str(e)}")
            return False

    def test_get_user_offers(self) -> bool:
        """Test get user offers API - GET /api/offers/user/{telegram_id}"""
        if not self.test_user_id:
            self.log_test("Get User Offers API", False, "No test user available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/api/offers/user/{self.test_user_id}",
                timeout=15
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if 'offers' in data:
                    offers = data['offers']
                    details = f"Found {len(offers)} offers for user"
                    
                    # If we created offers, verify they're returned
                    if self.created_offers:
                        found_offers = [o['id'] for o in offers if o.get('id') in self.created_offers]
                        details += f", {len(found_offers)} created offers found"
                        
                        # Check coordinates format in returned offers
                        for offer in offers:
                            coords = offer.get('coordinates')
                            if coords and isinstance(coords, list) and len(coords) == 2:
                                continue  # Good format
                            else:
                                print(f"⚠️  Warning: Offer {offer.get('id')} has invalid coordinates: {coords}")
                else:
                    success = False
                    details = "Missing offers field in response"
            else:
                details = f"Status: {response.status_code}"
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('error', 'Unknown')}"
                except:
                    pass
            
            self.log_test("Get User Offers API", success, details, response.json() if success else None)
            return success
            
        except Exception as e:
            self.log_test("Get User Offers API", False, f"Exception: {str(e)}")
            return False

    def test_get_all_offers(self) -> bool:
        """Test get all offers API - GET /api/offers"""
        try:
            response = requests.get(
                f"{self.base_url}/api/offers",
                timeout=15
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if 'offers' in data:
                    offers = data['offers']
                    total = data.get('total', len(offers))
                    details = f"Found {len(offers)} offers (total: {total})"
                    
                    # Check if offers have coordinates for map display
                    offers_with_coords = 0
                    for offer in offers:
                        coords = offer.get('coordinates')
                        if coords and isinstance(coords, list) and len(coords) == 2:
                            offers_with_coords += 1
                    
                    details += f", {offers_with_coords} with valid coordinates"
                    
                    if offers_with_coords < len(offers):
                        print(f"⚠️  Warning: {len(offers) - offers_with_coords} offers missing coordinates for map display")
                else:
                    success = False
                    details = "Missing offers field in response"
            else:
                details = f"Status: {response.status_code}"
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('error', 'Unknown')}"
                except:
                    pass
            
            self.log_test("Get All Offers API", success, details, response.json() if success else None)
            return success
            
        except Exception as e:
            self.log_test("Get All Offers API", False, f"Exception: {str(e)}")
            return False

    def test_categories_api(self) -> bool:
        """Test categories API"""
        try:
            response = requests.get(f"{self.base_url}/api/categories", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if "categories" in data:
                    categories = data["categories"]
                    details = f"Found {len(categories)} categories"
                    
                    # Check category structure
                    if categories:
                        cat = categories[0]
                        required_fields = ['id', 'name', 'icon']
                        missing_fields = [field for field in required_fields if field not in cat]
                        if missing_fields:
                            print(f"⚠️  Warning: Category missing fields: {missing_fields}")
                else:
                    success = False
                    details = "Missing categories field"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Categories API", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Categories API", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all backend tests"""
        print("🧪 Running MapChap Backend API Tests...\n")
        
        # Basic connectivity
        health_ok = self.test_health_check()
        if not health_ok:
            print("❌ Health check failed - stopping tests")
            return self.get_results()
        
        # Test authentication flow
        auth_ok = self.test_telegram_auth()
        if not auth_ok:
            print("❌ Telegram auth failed - skipping user-dependent tests")
            self.test_categories_api()
            self.test_get_all_offers()
            return self.get_results()
        
        # Test verification APIs
        self.test_inn_verification()
        self.test_manual_verification()
        
        # Test offers functionality
        self.test_create_offer()
        self.test_get_user_offers()
        self.test_get_all_offers()
        
        # Test supporting APIs
        self.test_categories_api()
        
        return self.get_results()

    def get_results(self) -> Dict[str, Any]:
        """Get test results summary"""
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed ({success_rate:.1f}%)")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All backend tests passed!")
        else:
            print("⚠️  Some backend tests failed - check details above")
        
        # Identify critical vs non-critical failures
        critical_failures = []
        non_critical_failures = []
        
        for result in self.test_results:
            if not result['success']:
                if any(keyword in result['name'].lower() for keyword in ['auth', 'verification', 'create offer']):
                    critical_failures.append(result['name'])
                else:
                    non_critical_failures.append(result['name'])
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": success_rate,
            "critical_failures": critical_failures,
            "non_critical_failures": non_critical_failures,
            "test_details": self.test_results,
            "timestamp": datetime.now().isoformat(),
            "test_user_id": self.test_user_id,
            "created_offers": self.created_offers
        }

def main():
    """Main test runner"""
    tester = MapChapAPITester()
    results = tester.run_all_tests()
    
    # Save results to file
    results_file = "/app/test_reports/mapchap_backend_test.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Return exit code based on success
    return 0 if results["success_rate"] == 100 else 1

if __name__ == "__main__":
    sys.exit(main())