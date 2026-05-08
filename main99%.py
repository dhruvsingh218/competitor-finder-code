import time
import random
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ---------------- GOOGLE SHEET ----------------
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    r'C:\Users\DHRUV\Documents\Automation_2\credentials.json', scope)

client = gspread.authorize(creds)
sheet = client.open("traffic_sheet2").sheet1


# ---------------- DRIVER ----------------
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 30)


# ---------------- HUMAN DELAY ----------------
def human_delay(a=2, b=5):
    time.sleep(random.uniform(a, b))


# ---------------- RULE ----------------
def is_valid(client, comp):
    if 50 <= client <= 5000:
        return client+1000 <= comp <= client+20000
    elif client < 100000:
        return client+1000 <= comp <= client+50000
    else:
        return client+1000 <= comp <= client+400000


# ---------------- ECOMMERCE FILTER ----------------
def mini_ecommerce_check(domain):
    try:
        url = "https://" + domain
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers, timeout=5)
        html = res.text.lower()

        if any(k in html for k in [
            "request a quote",
            "get a quote",
            "rfq",
            "bulk order"
        ]):
            return False

        if any(k in html for k in [
            "add to cart",
            "buy now",
            "checkout",
            "cart"
        ]) and "price" in html:
            return True

        return False

    except:
        return False


# ---------------- GOOGLE SEARCH ----------------
def get_domains(niche):

    domains = []
    seen = set()

    driver.switch_to.new_window('tab')
    driver.get("https://www.google.com")

    # 🔥 CAPTCHA WAIT
    while "sorry" in driver.current_url.lower():
        print("⚠ CAPTCHA detected... Please solve it manually")
        time.sleep(5)

    human_delay()

    search = driver.find_element(By.NAME, "q")
    search.send_keys(f"{niche} online store in USA")
    search.send_keys(Keys.RETURN)

    human_delay(3, 5)

    # 🔥 AGAIN CHECK CAPTCHA AFTER SEARCH
    while "sorry" in driver.current_url.lower():
        print("⚠ CAPTCHA detected after search... solve manually")
        time.sleep(5)

    for page in range(3):

        print(f"📄 Scraping Google Page {page+1}")

        links = driver.find_elements(By.CSS_SELECTOR, "a")

        for link_el in links:
            link = link_el.get_attribute("href")

            if not link:
                continue

            if "http" not in link:
                continue

            domain = link.split("//")[-1].split("/")[0]

            if any(x in domain for x in [
                "google", "youtube", "facebook", "instagram",
                "amazon", "wikipedia", "linkedin"
            ]):
                continue

            if any(x in link for x in ["/blog", "/article", "/news"]):
                continue

            if domain not in seen:
                seen.add(domain)
                domains.append(domain)

        try:
            next_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "pnnext"))
            )

            driver.execute_script(
                "arguments[0].click();",
                next_btn
            )

            human_delay(3, 6)

            # 🔥 CAPTCHA CHECK ON NEXT PAGE
            while "sorry" in driver.current_url.lower():
                print("⚠ CAPTCHA detected on next page... solve manually")
                time.sleep(5)

        except:
            break

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return domains[:25]


# ---------------- 🔥 AUTO LOGIN ----------------
driver.get("https://www.thehoth.com/login")

email = wait.until(
    EC.presence_of_element_located((By.NAME,"email"))
)

email.clear()
email.send_keys("ds9654711751@gmail.com")
time.sleep(2)

password = wait.until(
    EC.presence_of_element_located((By.NAME,"password"))
)

password.clear()
password.send_keys("@Dhruvsingh10")
time.sleep(2)

login_btn = wait.until(
    EC.element_to_be_clickable((By.ID,"login-submit"))
)

driver.execute_script(
    "arguments[0].click();",
    login_btn
)

print("✅ Login submitted")

time.sleep(6)


# 🔥 TOOL PAGE
driver.get(
    "https://www.thehoth.com/orders/freetools?tool=SEMrushStats"
)

iframe = wait.until(
    EC.presence_of_element_located((By.TAG_NAME, "iframe"))
)

driver.switch_to.frame(iframe)


# ---------------- 🔥 RESUME LOGIC ----------------
rows_data = sheet.get_all_values()

start_index = 1

for i in range(1, len(rows_data)):

    row = rows_data[i]

    niche = row[6]        # G
    comp_site = row[7]    # H
    comp_traffic = row[9] # J
    reason = row[11]      # L

    if niche.strip() != "" and \
       str(comp_site).strip() == "" and \
       str(comp_traffic).strip() == "" and \
       str(reason).strip() == "":

        start_index = i
        break

print(f"🚀 Resuming from row: {start_index+1}")


# ---------------- MAIN LOOP ----------------
for i in range(start_index, len(rows_data)):

    try:

        row = rows_data[i]

        client_traffic = row[5]
        niche = row[6]

        if niche.strip() == "":
            continue

        try:
            client_traffic = int(client_traffic)
        except:
            continue

        print(f"\n🚀 Row {i+1} | {niche}")

        domains = get_domains(niche)

        print("Domains:", domains)

        # ---------------- RESET TOOL ----------------

        driver.switch_to.default_content()

        iframe = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )

        driver.switch_to.frame(iframe)

        textarea = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "textarea"))
        )

        # 🔥 CLEAR WITHOUT REFRESH
        textarea.send_keys(Keys.CONTROL + "a")
        textarea.send_keys(Keys.DELETE)

        print("🧹 Cleared textarea without reload")

        time.sleep(random.uniform(2,4))

        textarea = wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "textarea"))
        )

        textarea.clear()

        for d in domains:
            textarea.send_keys(d + "\n")

        view_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(text(),'View')]"
            ))
        )

        view_btn.click()

        rows = wait.until(
            EC.presence_of_all_elements_located((
                By.CSS_SELECTOR,
                "table tbody tr"
            ))
        )

        time.sleep(2)

        best_domain = None
        best_traffic = None
        min_diff = float('inf')

        for r in rows:

            try:

                cols = r.find_elements(By.TAG_NAME, "td")

                if len(cols) < 4:
                    continue

                domain = cols[0].text
                traffic = cols[3].text.replace(",", "")

                try:
                    traffic = int(traffic)
                except:
                    continue

                print(domain, "→", traffic)

                if is_valid(client_traffic, traffic):

                    if mini_ecommerce_check(domain):

                        diff = abs(traffic - client_traffic)

                        if diff < min_diff:
                            min_diff = diff
                            best_domain = domain
                            best_traffic = traffic

            except:
                continue

        if best_domain:

            print("✅ BEST:", best_domain, best_traffic)

            sheet.update_cell(i+1, 8, best_domain)
            sheet.update_cell(i+1, 10, best_traffic)

        else:

            print("❌ Not found")

            sheet.update_cell(
                i+1,
                12,
                "Suitable competitor not found"
            )

    except Exception as e:

        print("⚠ Error:", e)
        continue


driver.quit()

print("\n🔥 DONE")