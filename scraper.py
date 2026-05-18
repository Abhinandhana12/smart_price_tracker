import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── Clean Price ───────────────────────────────────────────────
def clean_price(price_str):
    if not price_str:
        return None
    cleaned = re.sub(r'[^\d.]', '', str(price_str).replace(',', ''))
    parts = cleaned.split('.')
    if len(parts) > 2:
        cleaned = parts[0] + '.' + parts[1]
    try:
        val = float(cleaned)
        return val if val > 0 else None
    except:
        return None

# ── Create Browser ────────────────────────────────────────────
def get_driver():
    options = Options()
    options.add_argument('--headless')              # run in background (no window)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--window-size=1920,1080')
    options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         f'AppleWebKit/537.36 (KHTML, like Gecko) '
                         f'Chrome/122.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

# ── Amazon Scraper ────────────────────────────────────────────
def fetch_amazon(url):
    driver = None
    try:
        driver = get_driver()
        driver.get(url)
        time.sleep(random.uniform(2, 4))

        selectors = [
            '.priceToPay .a-offscreen',
            '#corePriceDisplay_desktop_feature_div .a-price .a-offscreen',
            '.a-price .a-offscreen',
            '#priceblock_ourprice',
            '#priceblock_dealprice',
            '#price_inside_buybox',
            '#newBuyBoxPrice',
        ]

        for sel in selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el:
                    p = clean_price(el.get_attribute('innerHTML') or el.text)
                    if p and p > 1:
                        print(f"[Amazon] Found price: Rs.{p}")
                        return p
            except:
                continue

        # Fallback: scan page text for rupee prices
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        matches = re.findall(r'₹\s*[\d,]+(?:\.\d+)?', page_text)
        for m in matches:
            p = clean_price(m)
            if p and p > 1:
                print(f"[Amazon] Fallback price: Rs.{p}")
                return p

    except Exception as e:
        print(f"[Amazon error] {e}")
    finally:
        if driver:
            driver.quit()
    return None

# ── Flipkart Scraper ──────────────────────────────────────────
def fetch_flipkart(url):
    driver = None
    try:
        driver = get_driver()
        clean_url = url.split('?')[0]
        driver.get(clean_url)
        time.sleep(random.uniform(3, 5))

        # Close login popup if it appears
        for popup_sel in ['button._2KpZ6l._2doB4z', 'button._2doB4z', '[class*="close"]']:
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, popup_sel)
                close_btn.click()
                time.sleep(1)
                break
            except:
                continue

        # ── Strategy 1: Use JavaScript to find selling price ──
        # Flipkart stores the final price in specific elements
        # We use JS to find elements containing ₹ that are NOT struck-through
        try:
            price = driver.execute_script("""
                // Find all elements with rupee symbol
                let allEls = document.querySelectorAll('*');
                let prices = [];
                for (let el of allEls) {
                    // Skip struck-through prices (MRP)
                    let style = window.getComputedStyle(el);
                    if (style.textDecoration.includes('line-through')) continue;
                    if (el.children.length > 0) continue; // skip parent elements
                    let text = el.innerText || el.textContent;
                    if (text && text.includes('₹')) {
                        let match = text.match(/₹\\s*([\\d,]+)/);
                        if (match) {
                            let val = parseFloat(match[1].replace(/,/g, ''));
                            if (val > 0) prices.push(val);
                        }
                    }
                }
                // Return the minimum non-zero price (selling price)
                return prices.length > 0 ? Math.min(...prices) : null;
            """)
            if price and price > 0:
                print(f"[Flipkart] JS selling price: ₹{price}")
                return float(price)
        except Exception as e:
            print(f"[Flipkart JS error] {e}")

        # ── Strategy 2: Specific CSS selectors for selling price ──
        selling_price_selectors = [
            '._30jeq3._16Jk6d',
            '.hl05eU ._30jeq3',
            '._25b18 ._30jeq3',
            '.dyC4hf ._30jeq3',
            'div._30jeq3',
        ]
        for sel in selling_price_selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el:
                    p = clean_price(el.text)
                    if p and p > 0:
                        print(f"[Flipkart] Selling price via {sel}: ₹{p}")
                        return p
            except:
                continue

        # ── Strategy 3: Get all ._30jeq3, skip struck-through ones ──
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, '._30jeq3')
            for el in elements:
                text_deco = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).textDecoration;", el)
                if 'line-through' in (text_deco or ''):
                    continue  # skip MRP (crossed out price)
                p = clean_price(el.text)
                if p and p > 0:
                    print(f"[Flipkart] Non-strikethrough price: ₹{p}")
                    return p
        except:
            pass

    except Exception as e:
        print(f"[Flipkart error] {e}")
    finally:
        if driver:
            driver.quit()
    return None

# ── Main Entry Point ──────────────────────────────────────────
def fetch_price(url):
    url = url.strip()
    if 'amazon' in url.lower():
        return fetch_amazon(url)
    elif 'flipkart' in url.lower():
        return fetch_flipkart(url)
    return None