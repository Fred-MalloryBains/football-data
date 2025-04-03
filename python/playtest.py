import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.set_capability(
    'goog:loggingPrefs', {"performance": "ALL", "browser": "ALL"}
)
options.add_argument("--disable-blink-features=AutomationControlled")

# Use this for newer Selenium versions
driver = webdriver.Chrome(options=options)

driver.set_page_load_timeout(30)


try:
    driver.get('https://www.sofascore.com/football/match/manchester-united-leicester-city/GK#id:12437027,tab:statistics')
except:
    print ("error")

time.sleep(5)
driver.execute_script("window.scroll(0, document.body.scrollHeight);")
time.sleep(5)


logs_raw = driver.get_log("performance")
logs = [json.loads(lr['message'])['message'] for lr in logs_raw]

for x in logs: 
    if 'shotmap' in x['params'].get('headers', {}).get(':path',''):
        print(x['params'].get('headers', {}).get(':path',''))
        break
   
shotmap = json.loads (driver.execute_cdp_cmd('Network.getResponseBody',{'requestId': x['params']['requestId']})['body'])['shotmap']

for i in shotmap:
    print (i['player']['name'])
