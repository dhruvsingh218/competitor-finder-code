import time
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys


# -----------------------------
# GOOGLE SHEET CONNECT
# -----------------------------

scope = [
'https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
r'C:\Users\DHRUV\Documents\Automation_2\credentials.json', scope)

client = gspread.authorize(creds)

sheet = client.open("traffic_sheet2").sheet1

websites = sheet.col_values(5)[1:]   # Column E


# -----------------------------
# 🔥 RESUME LOGIC
# -----------------------------

start_index = 0

for i in range(len(websites)):
    sheet_row = i + 2

    val = sheet.cell(sheet_row, 6).value

    if not val or str(val).strip() == "":
        start_index = i
        break

print(f"🚀 Resuming from row: {start_index + 2}")


# -----------------------------
# START BROWSER
# -----------------------------

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver,30)


# -----------------------------
# 🔥 AUTO LOGIN
# -----------------------------

driver.get("https://www.thehoth.com/orders/freetools?tool=SEMrushStats")

email = wait.until(EC.presence_of_element_located((By.NAME,"email")))
email.clear()
email.send_keys("ds9654711751@gmail.com")
time.sleep(2)

password = wait.until(EC.presence_of_element_located((By.NAME,"password")))
password.clear()
password.send_keys("@Dhruvsingh10")
time.sleep(2)

password.send_keys(Keys.ENTER)

print("✅ Login submitted")

time.sleep(6)


# -----------------------------
# OPEN TOOL
# -----------------------------






# -----------------------------
# BATCH SIZE
# -----------------------------

batch_size = 20


for start in range(start_index, len(websites), batch_size):

    batch = websites[start:start+batch_size]
    row_start = start + 2

    print("\nProcessing batch:",batch)


    # 🔥 FIX: ALWAYS RE-SWITCH IFRAME (ADDED)
    driver.switch_to.default_content()
    iframe = wait.until(
        EC.presence_of_element_located((By.TAG_NAME,"iframe"))
    )
    driver.switch_to.frame(iframe)

    time.sleep(random.uniform(2,4))   # stability


    textarea = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR,"textarea"))
    )

    textarea.clear()


    for site in batch:
        site = site.strip()
        if site:
            textarea.send_keys(site+"\n")


    view_btn = wait.until(
    EC.element_to_be_clickable((By.XPATH,"//button[contains(text(),'View')]"))
    )

    view_btn.click()

    print("Fetching traffic...")


    wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR,"table tbody tr"))
    )


    time.sleep(random.uniform(4,8))


    driver.execute_script("window.scrollBy(0,300)")
    time.sleep(random.uniform(2,4))


    rows = driver.find_elements(By.CSS_SELECTOR,"table tbody tr")


    for i,row in enumerate(rows):

        sheet_row = row_start + i

        if sheet.cell(sheet_row,6).value not in ["", None]:
            print("⏩ Skipping already filled row")
            continue

        cols = row.find_elements(By.TAG_NAME,"td")

        domain = cols[0].text
        traffic = cols[3].text.replace(",","")

        try:
            traffic = int(traffic)
        except:
            traffic = 0


        print(domain," → ",traffic)


        sheet.update_cell(sheet_row,6,traffic)


        if traffic < 50:
            sheet.update_cell(sheet_row,12,"Client traffic is low")


    # -----------------------------
    # RESET TOOL (NO REFRESH)
    # -----------------------------

    driver.switch_to.default_content()

    iframe = wait.until(
    EC.presence_of_element_located((By.TAG_NAME,"iframe"))
    )

    driver.switch_to.frame(iframe)

    textarea = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR,"textarea"))
    )

    textarea.send_keys(Keys.CONTROL + "a")
    textarea.send_keys(Keys.DELETE)

    print("🧹 Cleared... waiting before next batch")

    time.sleep(random.uniform(4,7))


    # -----------------------------
    # COOL DOWN
    # -----------------------------
    if start != 0 and start % (batch_size * 2) == 0:
        print("⏳ Cooling down 60 sec...")
        time.sleep(60)


    # -----------------------------
    # LIGHT REFRESH
    # -----------------------------
    if start != 0 and start % (batch_size * 3) == 0:
        print("🔄 Light refresh...")

        driver.switch_to.default_content()
        driver.refresh()

        time.sleep(8)

        iframe = wait.until(
        EC.presence_of_element_located((By.TAG_NAME,"iframe"))
        )

        driver.switch_to.frame(iframe)


driver.quit()

print("\n🔥 ALL DONE")