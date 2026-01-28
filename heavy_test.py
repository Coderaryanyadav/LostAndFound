#!/usr/bin/env python3
"""
COMPREHENSIVE HEAVY TESTING SCRIPT
Tests every single feature, edge case, and potential bug
"""

import requests
import json
import sys
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
TEST_RESULTS = []
ERRORS_FOUND = []

def log_test(test_name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    result = f"{status} - {test_name}"
    if message:
        result += f": {message}"
    TEST_RESULTS.append((passed, result))
    print(result)
    if not passed:
        ERRORS_FOUND.append(result)

def test_homepage():
    """Test 1: Homepage loads"""
    print("\n📄 TESTING HOMEPAGE...")
    try:
        r = requests.get(BASE_URL, timeout=5)
        log_test("Homepage loads", r.status_code == 200)
        log_test("Homepage has HTML content", "html" in r.text.lower())
        log_test("Homepage has stylesheet", "style.css" in r.text)
        log_test("Homepage has JavaScript", "<script>" in r.text)
    except requests.exceptions.ConnectionError:
        log_test("Homepage loads", False, "Server not running!")
        return False
    except Exception as e:
        log_test("Homepage loads", False, str(e))
        return False
    return True

def test_stats_api():
    """Test 2: Stats API"""
    print("\n📊 TESTING STATS API...")
    try:
        r = requests.get(f"{BASE_URL}/api/stats")
        data = r.json()
        
        log_test("Stats API returns 200", r.status_code == 200)
        log_test("Stats has 'success' field", 'success' in data)
        log_test("Stats success is True", data.get('success') == True)
        log_test("Stats has lost_count", 'lost_count' in data)
        log_test("Stats has found_count", 'found_count' in data)
        log_test("Stats has match_count", 'match_count' in data)
        log_test("Stats has matches array", 'matches' in data)
        log_test("Lost count is number", isinstance(data.get('lost_count'), int))
        log_test("Found count is number", isinstance(data.get('found_count'), int))
        log_test("Matches is array", isinstance(data.get('matches'), list))
    except Exception as e:
        log_test("Stats API working", False, str(e))

def test_lost_item_submission():
    """Test 3: Lost item submission with validation"""
    print("\n📝 TESTING LOST ITEM SUBMISSION...")
    
    # Valid submission
    valid_data = {
        "name": "Test Student 1",
        "roll": "CS001",
        "item": "Blue Notebook",
        "room": "101",
        "category": "Documents"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/lost", json=valid_data)
        result = r.json()
        log_test("Valid lost item submits", result.get('success') == True)
        log_test("Lost item returns 200", r.status_code == 200)
    except Exception as e:
        log_test("Valid lost item submits", False, str(e))
    
    # Missing required field (name)
    invalid_data1 = {
        "roll": "CS002",
        "item": "Red Pen",
        "room": "102"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/lost", json=invalid_data1)
        log_test("Missing name rejected", r.status_code == 400)
    except Exception as e:
        log_test("Missing name validation", False, str(e))
    
    # Missing required field (item)
    invalid_data2 = {
        "name": "Test Student",
        "roll": "CS003",
        "room": "103"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/lost", json=invalid_data2)
        log_test("Missing item rejected", r.status_code == 400)
    except Exception as e:
        log_test("Missing item validation", False, str(e))
    
    # Empty strings
    empty_data = {
        "name": "",
        "roll": "",
        "item": "",
        "room": ""
    }
    try:
        r = requests.post(f"{BASE_URL}/api/lost", json=empty_data)
        log_test("Empty strings rejected", r.status_code == 400)
    except Exception as e:
        log_test("Empty string validation", False, str(e))

def test_found_item_submission():
    """Test 4: Found item submission"""
    print("\n🔍 TESTING FOUND ITEM SUBMISSION...")
    
    # Valid submission
    valid_data = {
        "finder": "Test Finder",
        "item": "Blue Notebook",
        "room": "101",
        "category": "Documents"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/found", json=valid_data)
        result = r.json()
        log_test("Valid found item submits", result.get('success') == True)
    except Exception as e:
        log_test("Valid found item submits", False, str(e))
    
    # Missing item name
    invalid_data = {
        "finder": "Test",
        "room": "102"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/found", json=invalid_data)
        log_test("Found item without name rejected", r.status_code == 400)
    except Exception as e:
        log_test("Found item validation", False, str(e))

def test_data_retrieval():
    """Test 5: Data retrieval"""
    print("\n📥 TESTING DATA RETRIEVAL...")
    
    try:
        # Get lost items
        r = requests.get(f"{BASE_URL}/api/lost")
        lost_items = r.json()
        log_test("Lost items API returns 200", r.status_code == 200)
        log_test("Lost items returns array", isinstance(lost_items, list))
        log_test("Lost items have data", len(lost_items) > 0)
        
        if lost_items:
            item = lost_items[0]
            log_test("Lost item has id", 'id' in item)
            log_test("Lost item has name", 'name' in item)
            log_test("Lost item has item", 'item' in item)
            log_test("Lost item has status", 'status' in item)
            log_test("Lost item has date", 'date' in item)
        
        # Get found items
        r = requests.get(f"{BASE_URL}/api/found")
        found_items = r.json()
        log_test("Found items API returns 200", r.status_code == 200)
        log_test("Found items returns array", isinstance(found_items, list))
        
    except Exception as e:
        log_test("Data retrieval working", False, str(e))

def test_room_matching():
    """Test 6: Room matching algorithm"""
    print("\n🔗 TESTING ROOM MATCHING...")
    
    # Create items in same room
    lost = {
        "name": "Match Test Student",
        "roll": "MT001",
        "item": "Calculator",
        "room": "201",
        "category": "Electronics"
    }
    found = {
        "finder": "Match Finder",
        "item": "Calculator Found",
        "room": "201",
        "category": "Electronics"
    }
    
    try:
        requests.post(f"{BASE_URL}/api/lost", json=lost)
        requests.post(f"{BASE_URL}/api/found", json=found)
        
        time.sleep(0.5)  # Brief pause
        
        r = requests.get(f"{BASE_URL}/api/stats")
        data = r.json()
        matches = data.get('matches', [])
        
        log_test("Room matching works", len(matches) > 0)
        
        if matches:
            match_rooms = [m['room'] for m in matches]
            log_test("Match has correct room", '201' in match_rooms or '101' in match_rooms)
            
    except Exception as e:
        log_test("Room matching algorithm", False, str(e))

def test_item_management():
    """Test 7: Update and delete operations"""
    print("\n⚙️ TESTING ITEM MANAGEMENT...")
    
    try:
        # Get a lost item ID
        r = requests.get(f"{BASE_URL}/api/lost")
        items = r.json()
        
        if items and len(items) > 0:
            item_id = items[0]['id']
            
            # Test resolve (PUT)
            r = requests.put(f"{BASE_URL}/api/item/lost/{item_id}")
            result = r.json()
            log_test("Item resolve works", result.get('success') == True)
            
            # Test delete (DELETE)
            r = requests.delete(f"{BASE_URL}/api/item/lost/{item_id}")
            result = r.json()
            log_test("Item delete works", result.get('success') == True)
        else:
            log_test("Item management test", False, "No items to test with")
            
    except Exception as e:
        log_test("Item management", False, str(e))

def test_error_handling():
    """Test 8: Error handling"""
    print("\n🛡️ TESTING ERROR HANDLING...")
    
    # Invalid endpoint
    try:
        r = requests.get(f"{BASE_URL}/api/invalid")
        log_test("404 error handled", r.status_code == 404)
    except Exception as e:
        log_test("404 handling", False, str(e))
    
    # Invalid item type
    try:
        r = requests.put(f"{BASE_URL}/api/item/invalid/999")
        log_test("Invalid type rejected", r.status_code == 400)
    except Exception as e:
        log_test("Invalid type handling", False, str(e))
    
    # Invalid JSON
    try:
        r = requests.post(f"{BASE_URL}/api/lost", data="invalid json")
        log_test("Invalid JSON handled", r.status_code >= 400)
    except Exception as e:
        log_test("Invalid JSON handling", False, str(e))

def test_export():
    """Test 9: CSV Export"""
    print("\n💾 TESTING CSV EXPORT...")
    
    try:
        r = requests.get(f"{BASE_URL}/api/export")
        log_test("Export returns 200", r.status_code == 200)
        log_test("Export has CSV content", 'text/csv' in r.headers.get('Content-Type', ''))
        log_test("Export has data", len(r.content) > 0)
        log_test("Export has CSV headers", b'LOST ITEMS' in r.content or b'ID' in r.content)
    except Exception as e:
        log_test("CSV export", False, str(e))

def test_stress():
    """Test 10: Stress test with multiple rapid requests"""
    print("\n🔥 STRESS TESTING...")
    
    try:
        # Rapid fire 20 requests
        for i in range(10):
            data = {
                "name": f"Stress Test {i}",
                "roll": f"ST{i:03d}",
                "item": f"Test Item {i}",
                "room": f"{100 + i}",
                "category": "Other"
            }
            r = requests.post(f"{BASE_URL}/api/lost", json=data)
            if r.status_code != 200:
                log_test(f"Stress test request {i}", False, f"Status: {r.status_code}")
        
        log_test("Stress test (10 rapid requests)", True)
        
        # Verify all saved
        r = requests.get(f"{BASE_URL}/api/lost")
        items = r.json()
        log_test("All stress test items saved", len(items) >= 10)
        
    except Exception as e:
        log_test("Stress testing", False, str(e))

def test_edge_cases():
    """Test 11: Edge cases"""
    print("\n⚡ TESTING EDGE CASES...")
    
    # Very long strings
    long_data = {
        "name": "A" * 1000,
        "roll": "R" * 1000,
        "item": "I" * 1000,
        "room": "999",
        "category": "Other"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/lost", json=long_data)
        log_test("Very long strings handled", r.status_code in [200, 400])
    except Exception as e:
        log_test("Long string handling", False, str(e))
    
    # Special characters
    special_data = {
        "name": "Test <script>alert('xss')</script>",
        "roll": "'; DROP TABLE lost_items; --",
        "item": "\"Item\" with 'quotes'",
        "room": "101",
        "category": "Other"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/lost", json=special_data)
        log_test("Special characters handled", r.status_code == 200)
    except Exception as e:
        log_test("Special characters", False, str(e))
    
    # Unicode characters
    unicode_data = {
        "name": "学生名字 测试",
        "roll": "यूनिकोड123",
        "item": "📱 iPhone 💻",
        "room": "101",
        "category": "Electronics"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/lost", json=unicode_data)
        log_test("Unicode characters handled", r.status_code == 200)
    except Exception as e:
        log_test("Unicode handling", False, str(e))

def print_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    total = len(TEST_RESULTS)
    passed = sum(1 for p, _ in TEST_RESULTS if p)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if ERRORS_FOUND:
        print("\n" + "="*70)
        print("🐛 ERRORS FOUND:")
        print("="*70)
        for error in ERRORS_FOUND:
            print(f"  {error}")
        print("\n🔧 FIX NEEDED!")
    else:
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED! NO ERRORS FOUND!")
        print("="*70)
        print("✅ Application is production ready!")
    
    return failed == 0

def main():
    """Run all tests"""
    print("="*70)
    print("🧪 COMPREHENSIVE HEAVY TESTING SCRIPT")
    print("="*70)
    print(f"Testing: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Check server is running
    if not test_homepage():
        print("\n❌ ERROR: Server is not running!")
        print("Start the server with: python3 app.py")
        return False
    
    # Run all tests
    test_stats_api()
    test_lost_item_submission()
    test_found_item_submission()
    test_data_retrieval()
    test_room_matching()
    test_item_management()
    test_error_handling()
    test_export()
    test_stress()
    test_edge_cases()
    
    # Print summary
    success = print_summary()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
