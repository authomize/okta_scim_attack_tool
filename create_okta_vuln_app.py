from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from configparser import ConfigParser
import requests
import urllib3
import json
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = ConfigParser()
parser.read('oktaAppCreator.config')

oktaToken = parser.get('DEFAULT', 'oktaToken')
oktaDomain = parser.get('DEFAULT', 'oktaDomain')
label = parser.get('DEFAULT', 'label')
chromeDriverPath = parser.get('DEFAULT', 'chromeDriverPath')
scimServerAddress = parser.get('DEFAULT', 'scimServerAddress')

basicHeaders={
"Accept": "application/json",
"Content-Type": "application/json",
"Authorization": f"SSWS {oktaToken}"
}

def get_headers(driver, oktaDomain):
    cookies = []
    for cookie in driver.get_cookies():
        cookies.append(f"{cookie['name']}={cookie['value']}")
    cookies_str = "; ".join(cookies)
    xsrfToken = driver.find_element("id", "_xsrfToken").get_attribute("innerHTML")
    #print(xsrfToken)

    headers = {
        'authority': f'{oktaDomain}',
        'accept': 'text/plain, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': cookies_str,
        'origin': f'{oktaDomain}',
        'referer': f'{oktaDomain}/admin/app/scim2headerauth/instance/0oa7rk1lthY4NExbd5d7/',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'x-okta-xsrftoken': xsrfToken,
        'x-requested-with': 'XMLHttpRequest'
    }
    return headers

def create_new_scim_app(label, oktaDomain):
    data = {
    "name": "scim2headerauth",
    "label": label,
    "signOnMode": 'AUTO_LOGIN',
    "credentials": {
    "scheme": "EXTERNAL_PASSWORD_SYNC",
    "userNameTemplate": {
      "template": "${source.login}",
      "type": "BUILT_IN"
    },
    "revealPassword": 'false',
    "signing": {}
  },
    }

    url = f"{oktaDomain}/api/v1/apps"
    res = requests.post(url, headers=basicHeaders, json=data, verify=False)
    json_res = json.loads(res.text)
    if "errorCode" in json_res or res.status_code >= 400:
        print(res.text)
        exit()
    else:
        print(f"App \"{label}\" was created with this id: {json_res['id']}")
        return json_res['id']

def setup_provisioning(driver):
    config_integration_buttons = driver.find_elements("id", "userMgmtSettings.edit_link")
    for obj in config_integration_buttons:
        if obj.text == 'Configure API Integration':
            obj.click()

    #instead of enabeling API integration (checkbox)
    driver.execute_script("document.getElementById('options').style.display = 'block';")

def enable_integration(oktaDomain, driver, scimServer, app_id):
    headers = get_headers(driver, oktaDomain)
    
    data = {
        '_xsrfToken': headers['x-okta-xsrftoken'],
        'enabled':'true',
        '_enabled':'on',
        'scim_base_url':scimServer,
        'scim_auth_header_value_new':'token',  # value should not be changed
        '_profileMaster':'on',
        '_pushNewAccount':'on',
        'pushNewAccount':'true',
        '_pushProfile':'on',
        '_pushDeactivation':'on',
        'pushPassword':'true',
        '_pushPassword':'on',
        'syncUniquePassword':'false',
        '_cycleSyncedPassword':'on'
    }

    url = f'{oktaDomain}/admin/app/scim2headerauth/instance/{app_id}/settings/user-mgmt'
    res = requests.post(url, data=data, headers=headers, verify=False)

def get_everyone_group_id(oktaDomain):
    url = f"{oktaDomain}/api/v1/groups?q=Everyone"
    res = requests.get(url, headers=basicHeaders, verify=False)
    json_res = json.loads(res.text)
    return json_res[0]['id']

def assign_everyone(driver, oktaDomain, app_id):
    everyone_group_id = get_everyone_group_id(oktaDomain)
    url = f'{oktaDomain}/api/v1/apps/{app_id}/groups/{everyone_group_id}'
    headers = get_headers(driver, oktaDomain)
    data = {"id": everyone_group_id}
    res = requests.put(url, headers=basicHeaders, json=data, verify=False)

def print_banner():
    print("""
  O         o  o                        
 / \        |  |              o         
o---o o  o -o- O--o o-o o-O-o | o-o o-o 
|   | |  |  |  |  | | | | | | |  /  |-' 
o   o o--o  o  o  o o-o o o o | o-o o-o 

This tool was provided by Authomize
""")

print_banner()
app_id = create_new_scim_app(label, oktaDomain)
ser = Service(chromeDriverPath)
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(service=Service(chromeDriverPath), options=options)

driver.get(f'{oktaDomain}');
cc = input("After loging in Okta, Please press any keyboard key to continue")
time.sleep(1)
driver.get(f'{oktaDomain}/admin/app/scim2headerauth/instance/{app_id}/#tab-user-management')
time.sleep(5)
setup_provisioning(driver)
enable_integration(oktaDomain, driver, scimServerAddress, app_id)
assign_everyone(driver, oktaDomain, app_id)
driver.refresh()
