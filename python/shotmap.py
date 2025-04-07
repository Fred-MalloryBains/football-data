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

def get_data(url, driver, name):
    try:
        driver.get(url)
    except:
        print ("error")

    time.sleep(5)
    driver.execute_script("window.scroll(0, document.body.scrollHeight);")
    time.sleep(5)


    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr['message'])['message'] for lr in logs_raw]
    open ('logs.txt', 'w').write(json.dumps(logs, indent=4))
    request_id = None
    for x in logs: 
        if name in x['params'].get('headers', {}).get(':path',''):
            print(x['params'].get('headers', {}).get(':path',''))
            request_id = x['params']['requestId']
            break
    print (request_id)
    try:
        response = driver.execute_cdp_cmd('Network.getResponseBody',{'requestId': request_id})['body']
        print ('response', response)
    except Exception as e:
        print (e)
    return json.loads (driver.execute_cdp_cmd('Network.getResponseBody',{'requestId': x['params']['requestId']})['body'])[name]


def get_api_urls(url,driver):
    try:
        driver.get(url)
    except:
        print ("error")

    time.sleep(5)
    driver.execute_script("window.scroll(0, document.body.scrollHeight);")
    time.sleep(5)


    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr['message'])['message'] for lr in logs_raw]
    open ('logs.txt', 'w').write(json.dumps(logs, indent=4))
    urls = []
    for log in logs: 
        if log['method'] == 'Network.responseReceived':
            repsonse_urls = log['params'].get("response", {}).get("url", "")
            urls.append(repsonse_urls)
    return urls
    
url = 'https://www.sofascore.com/football/match/manchester-united-leicester-city/GK#id:12437027,tab:lineups'
#shotmap = get_data(url, driver, 'lineups')

print (get_data(url, driver, 'lineups'))



#for i in shotmap:
#    print (i['player']['name'])
'''   
url = 'https://www.sofascore.com/football/match/manchester-united-leicester-city/GK#id:12437027,tab:lineups'
lineups = get_data(url, driver, 'lineups')
for i in lineups['home']['players']:
    print (i['player']['name'])
'''

{"January":"1","February":2, "March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}