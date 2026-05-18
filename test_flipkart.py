from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

url = "https://www.flipkart.com/boat-bassheads-900-wired-headphones/p/itm75695e3b59495"

options = Options()
# options.add_argument('--headless')  # commented out so you can SEE the browser
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('excludeSwitches', ['enable-automation'])

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)
time.sleep(5)

# Print ALL elements with ₹ symbol
elements = driver.find_elements(By.XPATH, "//*[contains(text(), '₹')]")
print(f"\nFound {len(elements)} elements with ₹:\n")
for el in elements:
    try:
        style = driver.execute_script("return window.getComputedStyle(arguments[0]).textDecoration;", el)
        tag = el.tag_name
        text = el.text.strip()
        cls = el.get_attribute('class')
        if text:
            print(f"TAG:{tag} | CLASS:{cls} | TEXT:{text} | DECORATION:{style}")
    except:
        pass

driver.quit()