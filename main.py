from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

TELEGRAM_URL = "https://web.telegram.org/k/"  # aktualny adres Telegram Web (wersja K)

def is_logged_in(driver):
    """
    Heurystyka wykrywania zalogowania:
    - URL nie zawiera 'login'
    - albo pojawia się element typowy dla listy czatów / głównego UI
    """
    url_ok = "login" not in driver.current_url.lower()
    if url_ok:
        return True
    try:
        # kilka możliwych selektorów, z których przynajmniej jeden zwykle występuje po zalogowaniu
        possible_locators = [
            (By.CSS_SELECTOR, 'input[type="search"]'),           # pole wyszukiwania
            (By.CSS_SELECTOR, '[data-testid="chat-list"]'),      # lista czatów (często stosowany atrybut testowy)
            (By.CSS_SELECTOR, 'div[class*="sidebar"]'),          # prawa/lewa kolumna z czatami
            (By.CSS_SELECTOR, 'div[class*="chatlist"]'),         # lista czatów po nazwie klasy
        ]
        for by, sel in possible_locators:
            if driver.find_elements(by, sel):
                return True
    except Exception:
        pass
    return False

def main():
    # Opcje przeglądarki (możesz dodać np. profil, jeśli chcesz zapamiętywać sesję)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    # Jeżeli chcesz użyć istniejącego profilu Chrome (by nie logować się co raz):
    # chrome_options.add_argument("--user-data-dir=/ścieżka/do/profilu")
    # chrome_options.add_argument("--profile-directory=Default")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=chrome_options)

    try:
        driver.get(TELEGRAM_URL)

        print("Otworzono Telegram Web. Zeskanuj kod QR lub zaloguj się kodem z telefonu…")

        # Najpierw poczekaj aż załaduje się ekran logowania (np. QR / przycisk 'Log in by phone Number')
        # Nie jest to obowiązkowe, ale daje pewność, że strona się w pełni podniosła.
        try:
            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.url_contains("login"),
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas'))  # QR bywa w <canvas>
                )
            )
        except Exception:
            pass  # jeśli nie złapiemy nic – trudno, idziemy dalej

        # Teraz czekamy aż użytkownik się zaloguje.
        # Używamy pętli, bo warunek jest niestandardowy (sprawdzamy stan strony/URL).
        max_wait_seconds = 300  # 5 minut
        start = time.time()
        while time.time() - start < max_wait_seconds:
            if is_logged_in(driver):
                print("✅ Wykryto zalogowanie do Telegram Web.")
                break
            time.sleep(1)
        else:
            print("⏳ Minął limit czasu oczekiwania na zalogowanie.")

        # (Opcjonalnie) zrób coś po zalogowaniu – np. pokaż tytuł strony lub aktualny URL
        print("Aktualny URL:", driver.current_url)
        print("Tytuł strony:", driver.title)

        # Trzymaj przeglądarkę otwartą
        input("Naciśnij Enter, aby zamknąć przeglądarkę…")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
