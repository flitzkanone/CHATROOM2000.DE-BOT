import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- Konfiguration für den Server-Betrieb ---
# Wir nutzen Chrome-Optionen, um den Browser "headless" zu starten
chrome_options = Options()
chrome_options.add_argument("--headless") # Keine grafische Oberfläche
chrome_options.add_argument("--no-sandbox") # Erforderlich für den Betrieb auf vielen Cloud-Plattformen
chrome_options.add_argument("--disable-dev-shm-usage") # Verhindert bestimmte Absturzprobleme
chrome_options.add_argument("--disable-gpu") # In einer headless-Umgebung nicht nötig
chrome_options.add_argument("window-size=1920,1080") # Simuliert eine Bildschirmgröße

# --- Login-Daten sicher aus Umgebungsvariablen laden ---
# Diese werden wir später in Render setzen
DEIN_USERNAME = os.environ.get('CHAT_USER')
DEIN_PASSWORT = os.environ.get('CHAT_PASS')

if not DEIN_USERNAME or not DEIN_PASSWORT:
    print("Fehler: Umgebungsvariablen CHAT_USER und CHAT_PASS nicht gefunden!")
    exit() # Beendet das Skript, wenn die Login-Daten fehlen

# Liste mit Nachrichten
nachrichten_liste = [
    "Hallo zusammen, ich teste hier nur etwas.",
    "Wie ist die Stimmung heute?",
    "Das Wetter ist super!",
    "Ich wünsche allen einen schönen Tag.",
    "Was gibt es Neues?",
    "Automatisierung mit Python ist faszinierend."
]

# --- Initialisierung des Browsers ---
# Auf Render wird der chromedriver automatisch durch ein Buildpack gefunden
driver = webdriver.Chrome(options=chrome_options)

print("INFO: Skript gestartet, Browser wird initialisiert.")

# --- Hauptlogik des Bots ---
try:
    # 1. Webseite öffnen
    print("INFO: Öffne chatroom2000.de...")
    driver.get("https://www.chatroom2000.de/")

    # 2. Cookies akzeptieren
    try:
        print("INFO: Suche nach dem Cookie-Button...")
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept all')]"))
        )
        cookie_button.click()
        print("INFO: Cookies akzeptiert.")
        time.sleep(1)
    except Exception as e:
        print("WARNUNG: Konnte den Cookie-Button nicht finden oder es gab keinen.")

    # 3. Einloggen
    print("INFO: Fülle Login-Formular aus...")
    username_feld = driver.find_element(By.NAME, "nick")
    passwort_feld = driver.find_element(By.NAME, "pass")
    login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Los gehts!')]")

    username_feld.send_keys(DEIN_USERNAME)
    passwort_feld.send_keys(DEIN_PASSWORT)
    login_button.click()
    print("INFO: Login-Daten gesendet.")

    # Warte, bis der Chat geladen ist, indem wir auf das Eingabefeld warten.
    # Analyse hat ergeben, dass das Eingabefeld den Namen 'chat-input' hat.
    chat_input_selector = "chat-input"
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, chat_input_selector))
    )
    print("INFO: Erfolgreich eingeloggt und im Chatraum.")

    # 4. Nachrichten in einer Schleife senden
    while True:
        try:
            zwei_nachrichten = random.sample(nachrichten_liste, 2)
            
            for nachricht in zwei_nachrichten:
                chat_input = driver.find_element(By.NAME, chat_input_selector)
                
                # Der Sende-Button ist ein 'submit'-Button innerhalb des Formulars.
                # Wir können die Nachricht einfach mit .submit() abschicken.
                chat_input.send_keys(nachricht)
                chat_input.submit()
                
                print(f"NACHRICHT GESENDET: '{nachricht}'")
                time.sleep(3)

            print("INFO: Warte 30 Sekunden...")
            time.sleep(30)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"FEHLER in der Sendeschleife: {e}")
            # Bei Fehlern (z.B. Timeout) Screenshot zur Fehlersuche machen
            driver.save_screenshot('error_screenshot.png')
            print("FEHLER: Screenshot 'error_screenshot.png' wurde erstellt (nur auf lokalen Systemen sichtbar).")
            break

finally:
    print("INFO: Skript wird beendet, Browser wird geschlossen.")
    driver.quit()
