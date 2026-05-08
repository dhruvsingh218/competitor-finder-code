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

from PIL import Image


GYAZO_TOKEN = "glocktivB8Eb5H4aGVbZ2pNrsMD6IQ0S4zJsDAig9BA"


# ---------------- GYAZO UPLOAD ----------------
def upload_gyazo(image_path):

    url = "https://upload.gyazo.com/api/upload"

    with open(image_path, "rb") as img:

        response = requests.post(
            url,
            files={"imagedata": img},
            data={"access_token": GYAZO_TOKEN}
        )

    return response.json()["url"]


# ---------------- GOOGLE SHEETS ----------------
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    r'C:\Users\DHRUV\Documents\Automation_2\credentials.json',
    scope
)

client = gspread.authorize(creds)

sheet = client.open("traffic_sheet2").sheet1


# ---------------- DRIVER ----------------
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

wait = WebDriverWait(driver, 30)


# ---------------- HUMAN DELAY ----------------
def human_delay(a=2, b=5):
    time.sleep(random.uniform(a, b))


# ---------------- SWITCH IFRAME ----------------
def switch_iframe():

    iframe = wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )

    driver.switch_to.frame(iframe)


# ---------------- CAPTCHA WAIT ----------------
def captcha_wait():

    while "sorry" in driver.current_url.lower():
        print("⚠ CAPTCHA detected... solve manually")
        time.sleep(5)


# ---------------- 🔥 AUTO LOGIN ----------------
driver.get("https://www.thehoth.com/login")

email = wait.until(
    EC.presence_of_element_located((By.NAME, "email"))
)

email.clear()
email.send_keys("ds9654711751@gmail.com")

time.sleep(2)

password = wait.until(
    EC.presence_of_element_located((By.NAME, "password"))
)

password.clear()
password.send_keys("@Dhruvsingh10")

time.sleep(2)

login_btn = wait.until(
    EC.element_to_be_clickable((By.ID, "login-submit"))
)

driver.execute_script(
    "arguments[0].click();",
    login_btn
)

print("✅ Login submitted")

time.sleep(6)


# ---------------- TOOL PAGE ----------------
driver.get(
    "https://www.thehoth.com/orders/freetools?tool=SEMrushStats"
)

captcha_wait()

switch_iframe()


# ---------------- RESUME LOGIC ----------------
rows_data = sheet.get_all_values()

start_index = 0

for i in range(1, len(rows_data)):

    row = rows_data[i]

    client_site = row[4]      # E
    comp_site = row[7]        # H
    screenshot_link = row[10] # K

    if str(client_site).strip() != "" and \
       str(comp_site).strip() != "" and \
       str(screenshot_link).strip() == "":

        start_index = i - 1
        break

print(f"🚀 Resuming from row: {start_index + 2}")


# ---------------- MAIN LOOP ----------------
for i in range(start_index, len(rows_data) - 1):

    try:

        row_data = rows_data[i + 1]

        client_site = row_data[4].strip()
        comp_site = row_data[7].strip()

        if not client_site or not comp_site:
            continue

        row = i + 2

        print(f"\n🚀 Processing Row {row}")

        # ---------------- RESET TOOL WITHOUT RELOAD ----------------

        driver.switch_to.default_content()

        iframe = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )

        driver.switch_to.frame(iframe)

        textarea = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
        )

        # 🔥 CLEAR WITHOUT PAGE REFRESH
        textarea.send_keys(Keys.CONTROL + "a")
        textarea.send_keys(Keys.DELETE)

        print("🧹 Textarea cleared without reload")

        time.sleep(random.uniform(2, 4))

        textarea = wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "textarea"))
        )

        textarea.clear()

        textarea.send_keys(comp_site + "\n" + client_site)

        # ---------------- VIEW BUTTON ----------------

        view_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(text(),'View')]"
            ))
        )

        driver.execute_script(
            "arguments[0].click();",
            view_btn
        )

        print("⏳ Waiting for results...")

        wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "table tbody tr"
            ))
        )

        time.sleep(2)

        # ---------------- HIDE EXTRA COLUMNS ----------------

        driver.execute_script("""
        let rows = document.querySelectorAll("table tr");

        rows.forEach(row => {

            let cells = row.querySelectorAll("th, td");

            for (let i = cells.length - 1; i >= 4; i--) {
                cells[i].style.display = 'none';
            }

        });
        """)

        time.sleep(1)

        # ---------------- SELECT TABLE CONTAINER ----------------

        table = driver.find_element(By.CSS_SELECTOR, "table")

        container = table.find_element(
            By.XPATH,
            "./ancestor::div[2]"
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            container
        )

        time.sleep(1)

        # ---------------- SCREENSHOT ----------------

        screenshot_file = f"result_{row}.png"

        container.screenshot(screenshot_file)

        # ---------------- CROP IMAGE ----------------

        img = Image.open(screenshot_file)

        width, height = img.size

        cropped = img.crop((
            0,
            0,
            width,
            int(height * 0.55)
        ))

        cropped.save(screenshot_file)

        print("📸 FINAL CLEAN SCREENSHOT")

        # ---------------- UPLOAD ----------------

        try:

            link = upload_gyazo(screenshot_file)

            sheet.update_cell(row, 11, link)

            print("🔗 Uploaded:", link)

        except Exception as upload_error:

            print("⚠ Upload failed:", upload_error)

    except Exception as e:

        print("❌ ERROR:", e)

        try:

            driver.switch_to.default_content()

            driver.get(
                "https://www.thehoth.com/orders/freetools?tool=SEMrushStats"
            )

            captcha_wait()

            switch_iframe()

        except:
            pass

        continue


driver.quit()

print("🎉 DONE")