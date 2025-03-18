import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Enable performance logs
options = Options()
capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
options.add_argument("--headless")  # Optional: Run headless mode

driver = webdriver.Chrome(options=options)

# Start capturing network logs
driver.execute_cdp_cmd("Network.enable", {})

try:
    driver.get('https://www.sofascore.com/football/match/manchester-united-leicester-city/GK#id:12437027,tab:statistics')
except:
    print("Page load error")

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# Capture logs and filter 'shotmap' requests
logs_raw = driver.get_log("performance")
logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

# Find the shotmap request
request_id = None
for log in logs:
    if "Network.responseReceived" in log["method"]:
        url = log["params"].get("response", {}).get("url", "")
        if "shotmap" in url:
            request_id = log["params"]["requestId"]
            break

# Ensure request ID exists before extracting the response
if request_id:
    response = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
    shotmap_data = json.loads(response["body"])["shotmap"]
    
    for shot in shotmap_data:
        print(shot["player"]["name"])
else:
    print("Shotmap request not found!")

driver.quit()
