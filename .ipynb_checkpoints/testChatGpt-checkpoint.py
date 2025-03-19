import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {"performance": "ALL", "browser": "ALL"})
# Adding user agent to look more like a real browser
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(30)

def get_data(url, driver, name):
    # Clear existing logs
    driver.get("about:blank")
    logs = driver.get_log("performance")
    
    # Load the page
    print(f"Loading URL: {url}")
    driver.get(url)
    
    # Wait for the page to load properly
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
    except:
        print("Timeout waiting for page to load")
    
    # Interact with the page to trigger API calls
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    
    # Get network logs
    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr['message'])['message'] for lr in logs_raw]
    
    # Direct API approach - try to call the API directly
    
    match_id = url.split("#id:")[1].split(",")[0] if "#id:" in url else None
    if match_id:
        print(f"Extracted match ID: {match_id}")
        api_url = f"https://www.sofascore.com/api/v1/event/{match_id}/{name}"
        
        # Open the API URL directly
        driver.execute_script(f"window.open('{api_url}', '_blank');")
        time.sleep(2)
        
        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)
        
        # Get the page source which should contain the JSON
        page_source = driver.page_source
        
        # Extract JSON from the page source
        if "application/json" in page_source or "{" in page_source:
            start_idx = page_source.find("{")
            end_idx = page_source.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = page_source[start_idx:end_idx]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    print("Failed to parse JSON response")
        
        # Close the tab and switch back
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    
    # Look for the API call in the logs
    request_ids = []
    for log in logs:
        if log["method"] == "Network.requestWillBeSent":
            request_url = log["params"].get("request", {}).get("url", "")
            if name in request_url:
                print(f"✅ Found API request: {request_url}")
                request_ids.append(log["params"]["requestId"])
    
    if not request_ids:
        print("❌ No valid request ID found for:", name)
        return None
    
    # Try each request ID
    for request_id in request_ids:
        try:
            response = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
            print("✅ Response Body Retrieved")
            return json.loads(response['body'])
        except Exception as e:
            print(f"❌ Error with request ID {request_id}: {str(e)}")
    
    print("❌ Failed to retrieve data with all request IDs")
    return None

# Test URL
url = "https://www.sofascore.com/football/match/manchester-united-leicester-city/GK#id:12437027,tab:statistics"
'''
data = get_data(url, driver, "lineups")

if data:
    print("✅ Successfully fetched data!")
    # Print a sample of the data
    for i in data['home']['players']:
        print(i['player']['name'])
    for i in data['away']['players']:
        print(i['player']['name'])
else:
    print("❌ Failed to fetch data.")
'''

data = get_data(url, driver, "shotmap")
if data:
    print("✅ Successfully fetched data!")
    for i in data:
        print(i['player']['name'])
driver.quit()