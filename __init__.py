"""
Author: Shypilo Oleksandr
GitHub: https://github.com/ssshipilo

Disclaimer:
This code is provided as a sample program to demonstrate how automation works. 
It is intended for educational purposes only. The author is not responsible 
for any issues or damages that may arise from the use of this code.
"""

import subprocess
import sys
import importlib.util
import requests

def install(package):
    """Install a package using pip silently."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def package_installed(package_name):
    """Check if a package is installed."""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

# List of required packages
required_packages = [
    'google-auth-oauthlib',
    'google-auth',
    'selenium_driverless',
    'requests',
    'urllib3',
    'warnings'
]

# Check and install missing packages silently
for package in required_packages:
    if not package_installed(package.split('==')[0]):
        install(package)

import os
import json
import inspect
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from selenium_driverless.sync import webdriver
from selenium_driverless.types.by import By
from selenium.webdriver import Keys, ActionChains
import os
import time
import random
import urllib
import urllib.parse
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", message="the tabs aren't ordered by position in the window")

class Logger:
    COLORS = {
        'INFO': '\033[93m',    # Yellow for INFO
        'WARNING': '\033[38;5;208m', # Orange for WARNING
        'ERROR': '\033[91m',   # Red for ERROR
        'SUCCESS': '\033[92m', # Green for SUCCESS
        'RESET': '\033[0m',    # Reset to default
        'WHITE': '\033[97m',   # White for message text
    }
    
    def __init__(self, level='INFO'):
        self.level = level

    def _log(self, level, message):
        if self._should_log(level):
            time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            level_color = self.COLORS.get(level, self.COLORS['RESET'])
            reset = self.COLORS['RESET']
            white = self.COLORS['WHITE']
            print(f"{level_color}{level}{reset}\t[{time_str}]\t {white}{message}{reset}")

    def _should_log(self, level):
        levels = ['INFO', 'WARNING', 'ERROR', 'SUCCESS']
        return levels.index(level) >= levels.index(self.level)

    def info(self, message):
        self._log('INFO', message)

    def warning(self, message):
        self._log('WARNING', message)

    def error(self, message):
        self._log('ERROR', message)

    def success(self, message):
        self._log('SUCCESS', message)

logger = Logger(level='INFO')

class GoogleCredentials():
    """
    Class for managing Google API credentials.

    This class handles the process of obtaining and refreshing OAuth2 credentials for accessing Google APIs.
    It uses a client secrets file for authorization and stores the token in a file for future use.

    Attributes:
        email (str): User's email address for authorization.
        password (str): User's password for authorization.
        credentials_path (str): Path to the client secrets file.
        scopes (list): List of scopes required for authorization.
        proxy (bool): Whether to use a proxy server for authorization. Defaults to False.
        send_code_no_valid (str): Address with endpint where the code will be sent in the body as {"code": ""}

    Args:
        email (str): User's email address for authorization.
        password (str): User's password for authorization.
        credentials_path (str): Path to the client secrets file.
        scopes (list, optional): List of scopes for authorization. Defaults to an empty list.
        proxy (bool, optional): Flag to use a proxy server. Defaults to False.
        send_code_no_valid (str): Address with endpint where the code will be sent in the body as {"code": ""}
    """

    def __init__(self, email, password, credentials_path, scopes=[], proxy=False, send_code_no_valid=False):
        """Initialize the GoogleCredentials object.

        Args:
            email (str): User's email address for authorization.
            password (str): User's password for authorization.
            credentials_path (str): Path to the client secrets file.
            scopes (list, optional): List of scopes for authorization. Defaults to an empty list.
            proxy (bool, optional): Flag to use a proxy server. Defaults to False.
        """
        self.proxy = proxy
        self.email = email
        self.password = password
        self.credentials_path = credentials_path
        self.scopes = scopes
        self.send_code_no_valid = send_code_no_valid

    def get(self):
        """Obtain Google API credentials.

        This method performs the following steps:
        1. Checks for an existing token file.
        2. If the token exists and is valid, loads it.
        3. If the token is missing or invalid, performs the authorization process:
            - Loads client secrets.
            - Requests an authorization URL and authorization code.
            - Exchanges the code for a token.
        4. Saves the new token to a file for future use.

        Returns:
            google.auth.credentials.Credentials: The credentials object obtained from authorization.
        """
        
        driver = False
        try:
            current_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
            current_dir = os.path.dirname(current_file_path)
            r_el = str(self.email).split("@")[0]
            TOKEN_FILE = os.path.join(current_dir, "session", f"{r_el}_token.pickle")
            creds = None
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                    with open(self.credentials_path) as f:
                        credentials = json.loads(f.read())
                    flow.redirect_uri = credentials['installed']['redirect_uris'][0]
                    auth_url, _ = flow.authorization_url()
                    auth_driver = GoogleAuthDriver(url_auth=auth_url, proxy=self.proxy, email=self.email, password=self.password, send_code_no_valid=self.send_code_no_valid)
                    driver = auth_driver.driver
                    code = auth_driver.auth()
                    flow.fetch_token(code=code)
                    creds = flow.credentials

                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
                    
            return creds
        except Exception as e:
            print(e)
            pass
        finally:
            try:
                driver.quit()
            except:
                pass

class GoogleAuthDriver():
    """
    A class to handle the initialization and management of a Chrome WebDriver instance for automation.

    This class sets up a Chrome WebDriver with options for headless operation, proxy configuration, and various
    browser settings. It also supports loading browser extensions for specific functionalities.

    Attributes:
        url_auth (str): The URL to be used for authentication.
        email (str): The email address for authentication.
        password (str): The password for authentication.
        headless (bool): Whether to run the browser in headless mode (i.e., without a graphical user interface).
        proxy (bool or str): Proxy configuration. If a string is provided, it should be in the format "username:password@host:port".
    """

    def __init__(self, 
            proxy=False, 
            url_auth=False,
            email=False, 
            password=False,
            headless=False,
            send_code_no_valid=False
        ):
        """
        Initializes the GoogleAuthDriver with the specified configuration.

        Args:
            proxy (bool or str, optional): Proxy configuration. Defaults to False.
            url_auth (str, optional): The URL for authentication. Defaults to False.
            email (str, optional): Email address for authentication. Defaults to False.
            password (str, optional): Password for authentication. Defaults to False.
            headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
        """

        self.url_auth = url_auth
        self.email = email
        self.password = password
        self.headless = headless
        self.send_code_no_valid = send_code_no_valid
        self.proxy = proxy
        if proxy:
            self.proxy_type_http = proxy
            username, passandhost, port = str(proxy).split(":")
            password, host = passandhost.split("@")
            self.proxy = {"user": username, "pass": password, "host": host, "port": port}
        self.driver = self.__init_driver__()

    def __init_driver__(self):
        """
        Initializes the Chrome WebDriver with the specified options.

        Sets up the WebDriver with various arguments, including those for headless operation, proxy settings,
        and loading browser extensions.

        Returns:
            webdriver.Chrome: The initialized Chrome WebDriver instance.
        """
        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-gpu")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-webrtc")
        options.add_argument("--disable-ipv6")
        options.add_argument("--lang=en-us")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--allow-insecure-localhost")

        # Load multiple extensions
        extensions = []
        
        current_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
        current_dir = os.path.dirname(current_file_path)
        path_disabler_webrtc = os.path.join(current_dir, 'plugin', 'webrtc-disabled', 'v3')
        extensions.append(path_disabler_webrtc)
        options.add_argument("--load-extension=" + ",".join(extensions))
        
        # Init driver
        driver = webdriver.Chrome(options=options)
        if self.proxy:
            proxy = f"http://{self.proxy['user']}:{self.proxy['pass']}@{self.proxy['host']}:{self.proxy['port']}/"
            driver.set_single_proxy(proxy)

        return driver

    def __find_element__(self, by, element, wait=10):
        time_start = time.time()
        while True:
            df = time.time() - time_start
            if df > wait:
                return False
            try:
                el = self.driver.find_element(by, element)
                if el:
                    return el
            except:
                continue
            
    def __random_wait__(self):
        time.sleep(random.uniform(1, 3))
            
    def auth(self):
        try:
            self.driver.get(self.url_auth)
            
            # Email
            while True:
                try:
                    identifierId = self.__find_element__(By.ID, "identifierId")
                    identifierId.click(move_to=True)
                    identifierId.send_keys(self.email)
                    break
                except:
                    continue
            
            submit = self.__find_element__(By.CSS_SELECTOR, "#identifierNext button")
            submit.click(move_to=True)
            
            self.__random_wait__()
            
            # Password
            while True:
                try:
                    password = self.__find_element__(By.CSS_SELECTOR, "#password [type='password']")
                    password.click(move_to=True)
                    password.send_keys(self.password)
                    break
                except:
                    continue
            
            submit = self.__find_element__(By.CSS_SELECTOR, "#passwordNext button")
            submit.click(move_to=True)
            
            self.__random_wait__()
            
            wait = 10
            time_start = time.time()
            while True:
                df = time.time() - time_start
                if df > wait:
                    break
                try:
                    identifierId = self.__find_element__(By.CSS_SELECTOR, "form[novalidate] #identifierId")
                    if identifierId:
                        print("Found authentication from an untrusted computer")
                        while True:
                            code_valid = self.driver.execute_script("return document.querySelector('form[novalidate] section:nth-child(2) span').textContent;")
                            if code_valid != "":
                                print(f"Waiting for confirmation, click on the code: {code_valid}")
                                if self.send_code_no_valid:
                                    try:
                                        requests.post(self.send_code_no_valid, json={"code": code_valid})
                                    except:
                                        pass
                                break
                            else:
                                continue
                            
                        no_find = False
                        while True:
                            try:
                                identifierId = self.__find_element__(By.CSS_SELECTOR, "form[novalidate] #identifierId")
                                if identifierId:
                                    continue
                                else:
                                    no_find = True
                                    break
                            except:
                                no_find = True
                                break
                        if no_find:
                            break
                    else:
                        continue
                except:
                    continue
            
            self.__random_wait__()
        
            wait = 10
            time_start = time.time()
            while True:
                df = time.time() - time_start
                if df > wait:
                    return False
                try:
                    el = self.driver.execute_script("""return document.querySelector("[data-is-secondary-action-disabled]").querySelectorAll('button')[1];""")
                    if el:
                        el.click(move_to=True)
                        break
                except:
                    continue
            
            self.__random_wait__()

            # Checkbox
            while True:
                try:
                    password = self.__find_element__(By.CSS_SELECTOR, "[type='checkbox']")
                    password.click(move_to=True)
                    break
                except:
                    continue
            
            self.__random_wait__()

            # Continue
            wait = 10
            time_start = time.time()
            while True:
                df = time.time() - time_start
                if df > wait:
                    return False
                try:
                    el = self.driver.execute_script("""return document.querySelector("[data-is-secondary-action-disabled]").querySelectorAll('button')[1];""")
                    if el:
                        el.click(move_to=True)
                        break
                except:
                    continue
            
            while True:
                time.sleep(1)
                url = self.driver.current_url
                parsed_url = urllib.parse.urlparse(url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                code = query_params.get('code', [None])[0]
                if code:
                    return code
        except Exception as e:
            print(e)
            try:
                self.driver.quit()
            except:
                pass
            self.auth()
        finally:
            self.driver.quit()


