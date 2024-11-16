import os
import time
from tkinter import filedialog, Tk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import Listbox, MULTIPLE, Checkbutton, IntVar
import datetime
from urllib.parse import urljoin

# URL til innloggingssiden
login_url = 'https://reports.bambora.com/login'
# URL til hovedsiden etter innlogging
main_url = 'https://reports.bambora.com/'

# Dine innloggingsdetaljer
username = 'ditt_brukernavn'
password = 'ditt_passord'

# Start en selenium nettleser
chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 10)

driver.get(login_url)
logged_in = False

try:
    # Prøv å finne innloggingsfeltene ved forskjellige metoder
    try:
        username_input = wait.until(EC.presence_of_element_located((By.ID, 'id1')))
        password_input = wait.until(EC.presence_of_element_located((By.ID, 'id2')))
    except:
        try:
            username_input = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            password_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        except:
            try:
                username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]')))
                password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
            except:
                try:
                    username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @name='username']")))
                    password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password' or @name='password']")))
                except Exception as e:
                    print("Brukernavn og passordfelter ikke funnet. Mulig allerede logget inn:", e)
                    logged_in = True

    if not logged_in:
        print(f"Fyller inn brukernavn: {username}")
        username_input.send_keys(username)
        print(f"Fyller inn passord.")
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        # Vent litt for at siden skal laste inn
        time.sleep(5)
except Exception as e:
    print("En feil oppstod under innlogging:", e)

# Debugging: print all input elements' IDs, names, and types
inputs = driver.find_elements(By.TAG_NAME, 'input')
print("Alle input elementer funnet på siden:")
for input_elem in inputs:
    print("ID:", input_elem.get_attribute('id'), "Name:", input_elem.get_attribute('name'), "Type:", input_elem.get_attribute('type'))

# Naviger til hovedsiden
driver.get(main_url)

# Vent litt for at siden skal laste inn
time.sleep(5)

# Hent sideinnholdet
page_source = driver.page_source

# Parse HTML-innholdet
soup = BeautifulSoup(page_source, 'html.parser')

# Debugging print statements to understand the structure
print("Hovedsiden HTML innhold:")
print(soup.prettify()[:2000])  # Skriv ut de første 2000 tegnene av HTML-innholdet

# Funksjon for å finne alle lenker til merchants innenfor hele HTML-strukturen
def find_merchant_links(soup):
    merchant_links = []
    for div in soup.find_all('div', class_='merchant-list-selector'):
        merchant_links.extend(div.find_all('a', class_='merchant'))
    return merchant_links

merchant_links = find_merchant_links(soup)

if not merchant_links:
    print("Fant ikke noen merchants. Sjekk HTML-strukturen.")
else:
    merchants = {link.find('h3', class_='title').text: urljoin(main_url, link['href']) for link in merchant_links}

    # Lag et GUI-vindu for å vise merchants
    def open_selection_window():
        root = tk.Tk()
        root.title("Velg merchants")
        root.geometry('600x600')  # Sett størrelse på vinduet

        # Variabel for checkbox status
        select_all_var = IntVar()

        listbox = Listbox(root, selectmode=MULTIPLE, width=50, height=20)  # Sett størrelse på listbox
        for merchant in merchants.keys():
            listbox.insert(tk.END, merchant)
        listbox.pack(pady=20, padx=20, expand=True, fill=tk.BOTH)

        def select_all():
            if select_all_var.get() == 1:  # Hvis checkbox er merket
                listbox.select_set(0, tk.END)  # Merk alle elementer
            else:
                listbox.select_clear(0, tk.END)  # Fjern markering på alle elementer

        select_all_checkbox = Checkbutton(root, text="Merk alle", variable=select_all_var, command=select_all)
        select_all_checkbox.pack()

        def on_submit():
            selected_indices = listbox.curselection()
            selected_merchants = [listbox.get(i) for i in selected_indices]
            root.destroy()
            print("Valgte merchants:", selected_merchants)
            open_month_selection_window(selected_merchants)

        submit_button = tk.Button(root, text="Velg", command=on_submit)
        submit_button.pack(pady=20)
        root.mainloop()

    def open_month_selection_window(selected_merchants):
        month_root = tk.Tk()
        month_root.title("Velg måneder")
        month_root.geometry('600x600')

        # Variabel for checkbox status
        select_all_months_var = IntVar()

        months = [("Januar", "01", "January"), ("Februar", "02", "February"), ("Mars", "03", "March"), ("April", "04", "April"), ("Mai", "05", "May"), ("Juni", "06", "June"),
                  ("Juli", "07", "July"), ("August", "08", "August"), ("September", "09", "September"), ("Oktober", "10", "October"), ("November", "11", "November"), ("Desember", "12", "December")]

        month_vars = {}
        for month in months:
            month_vars[month[0]] = IntVar()

        def select_all_months():
            for month in months:
                month_vars[month[0]].set(select_all_months_var.get())

        select_all_months_checkbox = Checkbutton(month_root, text="Merk alle måneder", variable=select_all_months_var, command=select_all_months)
        select_all_months_checkbox.pack()

        for month in months:
            cb = Checkbutton(month_root, text=month[0], variable=month_vars[month[0]])
            cb.pack()

        def on_month_submit():
            selected_months = [(month[1], month[2]) for month in months if month_vars[month[0]].get() == 1]
            month_root.destroy()
            print("Valgte måneder:", selected_months)

            # Åpne filvelger for å velge nedlastingsmappe
            root = Tk()
            root.withdraw()
            download_dir = filedialog.askdirectory()
            root.destroy()
            if not download_dir:
                print("Ingen nedlastingsmappe valgt. Avslutter.")
                return

            print(f"Nedlastingsmappe valgt: {download_dir}")

            # Oppdater Chrome-innstillinger for å bruke denne mappen
            driver.execute_cdp_cmd('Page.setDownloadBehavior', {'behavior': 'allow', 'downloadPath': download_dir})
            download_reports(selected_merchants, selected_months, download_dir)

        submit_month_button = tk.Button(month_root, text="Velg måneder", command=on_month_submit)
        submit_month_button.pack(pady=20)
        month_root.mainloop()

    def close_modals():
        try:
            close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='dialog']//button[contains(@class, 'close')]")))
            close_button.click()
            time.sleep(2)  # Vent til modal lukkes
            print("Lukket modal.")
        except Exception as e:
            print("Ingen modal funnet eller feil ved lukking av modal:", e)

    def wait_for_downloads(download_dir, timeout=60):
        seconds = 0
        dl_wait = True
        while dl_wait and seconds < timeout:
            time.sleep(1)
            dl_wait = False
            files = os.listdir(download_dir)
            for fname in files:
                if fname.endswith('.crdownload'):
                    dl_wait = True
            seconds += 1
        return seconds < timeout

    def download_reports(selected_merchants, selected_months, download_dir):
        for merchant_name in selected_merchants:
            merchant_url = merchants[merchant_name]
            driver.get(merchant_url)
            time.sleep(3)  # Vent til siden lastes inn

            # Lukk eventuell modal før du går videre
            close_modals()

            # Naviger til "Reports"
            try:
                reports_link = wait.until(EC.presence_of_element_located((By.ID, 'navbar-link-reports')))
                print(f"Fant reports link for {merchant_name}")
                reports_link.click()
                time.sleep(3)

                # Naviger til "Detailed"
                details_link = wait.until(EC.presence_of_element_located((By.XPATH, "//div[text()='Detailed']")))
                print(f"Fant detailed link for {merchant_name}")
                details_link.click()
                time.sleep(3)

                # Hente rapporter for valgte måneder
                for selected_month in selected_months:
                    month_number, month_name_english = selected_month
                    # Finn rapportelementene for den valgte måneden og last ned rapportene
                    month_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, f"//div[@class='report-item' and .//div[@class='month-title' and text()='{month_name_english}']]")))
                    print(f"Fant måned elementer for {month_name_english} for {merchant_name}")
                    for month_element in month_elements:
                        download_button = month_element.find_element(By.XPATH, ".//button[@class='download-btn']")
                        download_button.click()
                        time.sleep(5)  # Vent til nedlastning starter
                        wait_for_downloads(download_dir)  # Vent til nedlastning fullføres

                print(f"Rapporter for {merchant_name} i månedene {', '.join([m[1] for m in selected_months])} er lastet ned.")
            except Exception as e:
                print(f"Feil ved behandling av {merchant_name}: {e}")

    open_selection_window()

# Lukk nettleseren etter at vinduet er lukket
driver.quit()
