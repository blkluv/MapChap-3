#!/usr/bin/env python3
"""
MapChap Analytics API Testing Suite
Tests all analytics endpoints for business owners
"""

import requests
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

class AnalyticsAPITester:
    def __init__(self, base_url: str = "https://process-steps-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.test_telegram_id = 111222333  # From test credentials
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        print(f"🚀 Starting MapChap Analytics API Tests")
        print(f"📡 Base URL: {base_url}")
        print(f"👤 Test User ID: {self.test_telegram_id}")
        print("=" * 60)

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
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

    def test_analytics_dashboard(self) -> bool:
        """Test analytics dashboard endpoint"""
        try:
            url = f"{self.base_url}/api/analytics/dashboard/{self.test_telegram_id}"
            
            # Test different periods
            periods = ["7d", "30d", "90d"]
            all_success = True
            
            for period in periods:
                response = requests.get(f"{url}?period={period}", timeout=15)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    # Validate response structure
                    required_fields = ["period", "summary", "chart_data", "offers", "recommendations"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        success = False
                        details = f"Missing fields: {missing_fields}"
                    else:
                        # Check summary structure
                        summary = data.get("summary", {})
                        summary_fields = ["total_offers", "active_offers", "total_views", "unique_visitors", "trend_percent"]
                        missing_summary = [field for field in summary_fields if field not in summary]
                        
                        if missing_summary:
                            success = False
                            details = f"Missing summary fields: {missing_summary}"
                        else:
                            details = f"Period: {period}, Offers: {summary.get('total_offers')}, Views: {summary.get('total_views')}"
                else:
                    details = f"Status: {response.status_code}"
                    if response.status_code == 404:
                        details += " - User not found or not business owner"
                    elif response.status_code == 403:
                        details += " - Access denied"
                
                self.log_test(f"Analytics Dashboard ({period})", success, details, data if success else None)
                if not success:
                    all_success = False
            
            return all_success
        except Exception as e:
            self.log_test("Analytics Dashboard", False, f"Exception: {str(e)}")
            return False

    def test_offer_analytics(self) -> bool:
        """Test individual offer analytics"""
        try:
            # First, get user offers to test with
            offers_url = f"{self.base_url}/api/offers/user/{self.test_telegram_id}"
            offers_response = requests.get(offers_url, timeout=10)
            
            if offers_response.status_code != 200:
                self.log_test("Offer Analytics", False, "Could not fetch user offers for testing")
                return False
            
            offers_data = offers_response.json()
            offers = offers_data.get("offers", [])
            
            if not offers:
                self.log_test("Offer Analytics", False, "No offers found for testing")
                return False
            
            # Test analytics for first offer
            test_offer = offers[0]
            offer_id = test_offer.get("id")
            
            url = f"{self.base_url}/api/analytics/offer/{offer_id}"
            params = {
                "telegram_id": self.test_telegram_id,
                "period": "30d"
            }
            
            response = requests.get(url, params=params, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                # Validate response structure
                required_fields = ["offer_id", "offer_title", "period", "summary", "charts", "recommendations"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    # Check summary structure
                    summary = data.get("summary", {})
                    summary_fields = ["total_views", "unique_visitors", "trend_percent", "conversion_rate", "peak_hour"]
                    missing_summary = [field for field in summary_fields if field not in summary]
                    
                    if missing_summary:
                        success = False
                        details = f"Missing summary fields: {missing_summary}"
                    else:
                        # Check charts structure
                        charts = data.get("charts", {})
                        if "views_by_day" not in charts or "views_by_hour" not in charts:
                            success = False
                            details = "Missing chart data"
                        else:
                            details = f"Offer: {data.get('offer_title')}, Views: {summary.get('total_views')}, Peak: {summary.get('peak_hour')}"
            else:
                details = f"Status: {response.status_code}"
                if response.status_code == 404:
                    details += " - Offer not found"
                elif response.status_code == 403:
                    details += " - Not authorized"
            
            self.log_test("Offer Analytics", success, details, data if success else None)
            return success
            
        except Exception as e:
            self.log_test("Offer Analytics", False, f"Exception: {str(e)}")
            return False

    def test_compare_analytics(self) -> bool:
        """Test compare offers analytics"""
        try:
            # Get user offers for comparison
            offers_url = f"{self.base_url}/api/offers/user/{self.test_telegram_id}"
            offers_response = requests.get(offers_url, timeout=10)
            
            if offers_response.status_code != 200:
                self.log_test("Compare Analytics", False, "Could not fetch user offers for testing")
                return False
            
            offers_data = offers_response.json()
            offers = offers_data.get("offers", [])
            
            if len(offers) < 2:
                # Test with single offer if only one available
                offer_ids = [offers[0]["id"]] if offers else []
            else:
                # Test with first two offers
                offer_ids = [offers[0]["id"], offers[1]["id"]]
            
            if not offer_ids:
                self.log_test("Compare Analytics", False, "No offers found for comparison")
                return False
            
            url = f"{self.base_url}/api/analytics/compare/{self.test_telegram_id}"
            params = {"offer_ids": ",".join(offer_ids)}
            
            response = requests.get(url, params=params, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                # Validate response structure
                if "comparison" not in data:
                    success = False
                    details = "Missing comparison field"
                else:
                    comparison = data["comparison"]
                    if not isinstance(comparison, list):
                        success = False
                        details = "Comparison should be a list"
                    else:
                        # Check comparison item structure
                        if comparison:
                            item = comparison[0]
                            required_fields = ["id", "title", "category", "views_30d", "total_views", "favorites"]
                            missing_fields = [field for field in required_fields if field not in item]
                            
                            if missing_fields:
                                success = False
                                details = f"Missing comparison fields: {missing_fields}"
                            else:
                                details = f"Compared {len(comparison)} offers"
                        else:
                            details = "Empty comparison result"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Compare Analytics", success, details, data if success else None)
            return success
            
        except Exception as e:
            self.log_test("Compare Analytics", False, f"Exception: {str(e)}")
            return False

    def test_categories_endpoint(self) -> bool:
        """Test categories endpoint (needed for analytics context)"""
        try:
            response = requests.get(f"{self.base_url}/api/categories", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if "categories" not in data:
                    success = False
                    details = "Missing categories field"
                else:
                    categories = data["categories"]
                    if not isinstance(categories, list) or len(categories) == 0:
                        success = False
                        details = "Categories should be a non-empty list"
                    else:
                        details = f"Found {len(categories)} categories"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Categories Endpoint", success, details, data if success else None)
            return success
        except Exception as e:
            self.log_test("Categories Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_user_endpoint(self) -> bool:
        """Test user endpoint to verify business owner status"""
        try:
            response = requests.get(f"{self.base_url}/api/users/{self.test_telegram_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ["telegram_id", "role", "is_verified"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing user fields: {missing_fields}"
                else:
                    role = data.get("role")
                    is_verified = data.get("is_verified")
                    details = f"Role: {role}, Verified: {is_verified}"
                    
                    if role != "business_owner":
                        print(f"⚠️  Warning: Test user is not a business owner (role: {role})")
            else:
                details = f"Status: {response.status_code}"
                if response.status_code == 404:
                    details += " - User not found"
            
            self.log_test("User Endpoint", success, details, data if success else None)
            return success
        except Exception as e:
            self.log_test("User Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_offers_endpoint(self) -> bool:
        """Test user offers endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/offers/user/{self.test_telegram_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if "offers" not in data:
                    success = False
                    details = "Missing offers field"
                else:
                    offers = data["offers"]
                    details = f"Found {len(offers)} offers"
                    
                    if offers:
                        # Check offer structure
                        offer = offers[0]
                        required_fields = ["id", "title", "category", "views", "status"]
                        missing_fields = [field for field in required_fields if field not in offer]
                        
                        if missing_fields:
                            print(f"⚠️  Warning: Offer missing fields: {missing_fields}")
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("User Offers", success, details, data if success else None)
            return success
        except Exception as e:
            self.log_test("User Offers", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all analytics tests"""
        print("🧪 Running Analytics API Tests...\n")
        
        # Basic connectivity tests
        health_ok = self.test_health_check()
        if not health_ok:
            print("❌ Health check failed - stopping tests")
            return self.get_results()
        
        # User and data setup tests
        self.test_user_endpoint()
        self.test_categories_endpoint()
        self.test_offers_endpoint()
        
        # Analytics tests
        self.test_analytics_dashboard()
        self.test_offer_analytics()
        self.test_compare_analytics()
        
        return self.get_results()

    def get_results(self) -> Dict[str, Any]:
        """Get test results summary"""
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed ({success_rate:.1f}%)")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed - check details above")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": success_rate,
            "test_details": self.test_results,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Main test runner"""
    tester = AnalyticsAPITester()
    results = tester.run_all_tests()
    
    # Save results to file
    results_file = "/app/test_reports/backend_analytics_test.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Return exit code based on success
    return 0 if results["success_rate"] == 100 else 1

if __name__ == "__main__":
    sys.exit(main())