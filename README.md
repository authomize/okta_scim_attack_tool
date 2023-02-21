This repository contains a pen-testing tool based on (#passbleed) that allows pen-testers to extract clear text passwords from Okta by abusing Okta's implementation of the System for Cross-domain Identity Management (SCIM) protocol. The issue allows for clear text password stealing and PII theft. The issue was discovered by [Authomize](https://www.authomize.com/). More information can be found in this [blog post](https://authomize.com/blog/authomize-discovers-password-stealing-and-impersonation-risks-to-in-okta/#challenges).

The repository uses the [go-scim](https://github.com/imulab/go-scim) repo to create a SCIM server and a Python script to create an app in Okta that will allow you to export the clear text credentials.
** Please note:
1. The server must first be installed  
2. In order to use a domain rather than IP, you have to buy one and set an A record in your DNS server

## prerequisites
Docker, Docker-compose, make and go should be installed<br />
Server must be accessible from the internet

## TLDR
1. Clone this repo:
  ```bash
  git clone https://github.com/authomize/okta_scim_attack_tool
  ```
2. Install server:
  ```bash
  sh ./install.sh
  cd server
  make docker compose
  ```
3. Create the app for exporting the clear text credentials in Okta From a PC with a GUI Chrome browser:
  - Download Chromium: https://chromedriver.chromium.org/downloads
  - Config the variables in create_okta_vuln_app.config
  - Execute ```pyhon create_okta_vuln_app.py```
  - When browser opens - log in to Okta with "Application Admin" user
  - Press Enter key in the CMD/Terminal after you loged in to Okta
  - Wait for users to log in or log in to your user
  - Go to Okta -> Applications -> The vulnerable app we created ("Offensive SCIM APP") -> provisioning tab
  - Scroll down and click on "Force Sync"
  - Go to your SCIM server (defined in create_okta_vuln_app.config)<br />
  &emsp; for example: http://your_server_IP/scim/v2/Users
  - You should see your clear text password as well as all other users that logged in to Okta after the app was created
  
## Installation Diagram
![Attack Diagram](https://github.com/authomize/okta_scim_attack_tool/blob/master/Okta%20attack.png)

## Server Setup
To run the SCIM server, navigate to the server directory and execute the following commands:
```bash
sh install.sh
cd server
make docker compose
```

The server default URI is: /scim/v2, it can be changed in the server/.env file
In order to view users, you should browse to: http://<IP_ADDRESS or Domain>/scim/v2/Users

## Create Okta vulnerbale app
**This script requires GUI Chrome browser**<br />
**Save chromedriver file in the executing folder<br />
**In order to install all dependencies please execute:**
```python
pip install -r requirements.txt
```
To create the app in Okta, execute create_okta_vuln_app.py and provide the following parameters in create_okta_vuln_app.config file:
- oktaToken: A token to create a new SCIM app, get the "Everyone" group id and assign the "Everyone" group to the new app
- oktaDomain: The domain of your Okta account and API.
- label: The name of the new app in Okta (default name is "Offensive SCIM APP")
- chromeDriverPath: The path to Chrome Driver for Selenium. Relevant versions can be found at https://chromedriver.chromium.org/downloads
- scimServerAddress: The IP or domain of your SCIM server with the uri you chose, for example: http://<IP_ADDRESS or Domain>/scim/v2 

## Additional info
- The easiest way to clean the DB is to execute ```docker-compose down```

## Clarifications
- Since this script creates a malicious app in Okta, it is recommended to delete the token after the app is created
- Clear text passwords will only be shown for users who have signed in to Okta after the app was created. Other users will have hashed passwords. - in order to see new passwords please click "Force sync" under Application -> Provisioning -> "Attribute Mappings"
- Authomize provides this tool for educational purposes only

If you have any further questions, please contact Authomize 

## Future improvments
1. HTTPS support using Certbot - Okta doesn't support self-signed certificates
2. Attack by changing an existing application SCIM base url

## Disclaimer
This tool was developed for Penetration Testing purposes only. <br />
Authomize is not responsible for any possible illegal or malicious usage of any files or instructions provided by this repository. <br />
If you intend to use this tool for any malicious purposes, use it at your own risk!

## License 
Server license can be found in [go-scim LICENSE file](https://github.com/imulab/go-scim/blob/master/LICENSE)
<br /><br />
The software is provided "as is", without warranty of any kind, express or
implied, including but not limited to the warranties of merchantability,
fitness for a particular purpose and noninfringement. in no event shall the
authors or copyright holders be liable for any claim, damages or other
liability, whether in an action of contract, tort or otherwise, arising from,
out of or in connection with the software or the use or other dealings in the
software.
<br /><br />
Users of this repository are solely responsible for their use of the content and should seek professional advice before taking any action based on its contents.
<br /><br />
Also by using this tool, you agree to be an awesome person. Try to help others, strive not to be a script kiddie, speak fairly to everyone, offer free hugs to everyone (provided the other person agrees in a mutual hug, don't FORCE), and never underestimate anyone.
