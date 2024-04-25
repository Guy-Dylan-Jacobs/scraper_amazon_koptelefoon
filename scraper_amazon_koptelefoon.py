# scraper_Amazon_koptelefoon.py

# Dit script automatiseert het proces van het schrapen van koptelefoongegevens van Amazon.nl,
# het opslaan ervan in een MySQL-database en het omgaan met paginering om gegevens van meerdere pagina's met zoekresultaten op te halen.

# Importeer de vereiste modules
import re
import time
import mysql.connector
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Initialiseer Chrome-opties
chrome_opties = webdriver.ChromeOptions()
chrome_opties.add_experimental_option("detach", True)

# Initialiseer de Chrome-driver met opties
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_opties)

# Open de website van Amazon Nederland
driver.get("https://www.amazon.nl")

# Accepteer cookies
accepteer_cookies = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "sp-cc-accept")))
accepteer_cookies.click()

# Zoek naar koptelefoon
search_bar = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "twotabsearchtextbox")))
search_bar.clear()
search_bar.send_keys("koptelefoon")

# Zoekknop vinden en klikken
zoek_knop = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "nav-search-submit-button")))
zoek_knop.click()

afdeling_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "n-title")))
afdeling_dropdown.click()

Over_ear_koptelefoons = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="n/16366269031"]/span/a/span')))
Over_ear_koptelefoons.click()

# Dropdownmenu voor geluidsbeheersing vinden en klikken
geluidsbeheersing_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "p_n_feature_thirteen_browse-bin-title")))
geluidsbeheersing_dropdown.click()

# Selecteer geluidsbeheersing
actieve_ruisonderdrukking = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="p_n_feature_thirteen_browse-bin/27957745031"]/span/a/span')))
actieve_ruisonderdrukking.click()

# wacht 10 seconden om te controleren of de selectie correct is
time.sleep(10)

# Query's voor het aanmaken van de database Amazon en koptelefoon table
drop_db = 'DROP DATABASE IF EXISTS Amazon'
creer_db = 'CREATE DATABASE IF NOT EXISTS Amazon'
geb_db = 'USE Amazon'
drop_table = 'DROP TABLE IF EXISTS koptelefoons'
creer_tabel = '''CREATE TABLE IF NOT EXISTS koptelefoons (
                    Model TEXT,
                    Prijs FLOAT
                    )'''

# Maak verbinding met het MySQL-server
amazon_koptel_db = mysql.connector.connect(
    host='localhost',
    user='G_jacobs_portfolio',
    password='G_jacobs1234'
)

# Maak databasecursor
mycursor = amazon_koptel_db.cursor()

# Drop Amazon database als deze bestaat
#mycursor.execute(drop_db)
# Maak Amazon database als deze niet bestaat
mycursor.execute(creer_db)
# Selecteer de 'Amazon'-database
mycursor.execute(geb_db)
# Drop koptelefoons tabel als deze bestaat
mycursor.execute(drop_table)
# Maak koptelefoons tabel als deze niet bestaat
mycursor.execute(creer_tabel)

# Voer de wijzigingen door in de database
amazon_koptel_db.commit()

# Itereer over de paginanummers van 1 tot en met 3
for paginanummer in range(1, 6):

    # Haal de HTML van de pagina op
    pagina_html = driver.page_source

    # Maak een BeautifulSoup-object van de HTML
    soup = BeautifulSoup(pagina_html, 'html.parser')

    # Zoek alle elementen voor koptelefoons op de pagina
    koptelefoons = soup.findAll('div', {'class': 's-result-item'})

    # Sorteer de koptelefoons op basis van hun 'data-index' attribuut
    koptelefoons.sort(key=lambda x: int(x.get('data-index', 0)))

    # Haal gegevens uit en voeg ze toe aan de database
    for koptelefoon in koptelefoons:
        model_element = koptelefoon.find('span', {'class': 'a-size-base-plus a-color-base a-text-normal'})
        prijs_element = koptelefoon.find('span', {'class': 'a-price-whole'})
        if model_element:
            model = model_element.text.strip()
        else:
            model = None

        if prijs_element:
            prijs_text = re.sub(r'[^\d.,]', '', prijs_element.text.strip())
            try:
                prijs = float(prijs_text.replace(',', '.'))
            except ValueError:
                prijs = None
        else:
            prijs = None

        if model and prijs is not None:
            voeg_data_in = "INSERT INTO koptelefoons (Model, Prijs) VALUES (%s, %s)"
            data = (model, prijs)
            mycursor.execute(voeg_data_in, data)
            amazon_koptel_db.commit()
            print('Naam:', model)
            print('Prijs:', prijs)
            print()

    # Wacht tot de knop klikbaar is en selecteer de "Volgende Pagina" knop
    volgende_pagina_knop = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "s-pagination-next")]')))
    volgende_pagina_knop.click()

    # Wacht 10 seconden voordat u de browser sluit
    time.sleep(10)

print("Data succesvol opgehaald en toegevoegd.")

# Sluit de browser
driver.quit()
# Sluit de cursor
mycursor.close()
# Sluit de databaseverbinding
amazon_koptel_db.close()