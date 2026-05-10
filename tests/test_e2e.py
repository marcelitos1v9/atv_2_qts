import threading
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app import create_app, services

E2E_PORT = 5099
BASE_URL = f"http://127.0.0.1:{E2E_PORT}"


@pytest.fixture(scope="module")
def flask_server():
    services.reset_store()
    app = create_app(testing=True)

    from werkzeug.serving import make_server

    server = make_server("127.0.0.1", E2E_PORT, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)
    yield BASE_URL
    server.shutdown()


@pytest.fixture(scope="module")
def driver(flask_server):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")

    try:
        d = webdriver.Chrome(options=options)
    except Exception:
        pytest.skip("Chrome não disponível para testes E2E")
        return

    yield d
    d.quit()


def test_e2e_page_loads(driver, flask_server):
    driver.get(flask_server)
    assert "Biblioteca" in driver.title
    h1 = driver.find_element(By.TAG_NAME, "h1")
    assert h1.text == "Biblioteca"


def test_e2e_add_book_appears_in_table(driver, flask_server):
    driver.get(flask_server)
    wait = WebDriverWait(driver, 10)

    title_input = wait.until(EC.presence_of_element_located((By.ID, "title")))
    author_input = driver.find_element(By.ID, "author")

    title_input.clear()
    title_input.send_keys("Livro E2E Teste")
    author_input.clear()
    author_input.send_keys("Autor Selenium")

    driver.find_element(By.ID, "add-book-btn").click()

    wait.until(
        EC.text_to_be_present_in_element((By.ID, "books-table"), "Livro E2E Teste")
    )
    table_text = driver.find_element(By.ID, "books-table").text
    assert "Livro E2E Teste" in table_text
    assert "Autor Selenium" in table_text


def test_e2e_search_filters_results(driver, flask_server):
    driver.get(flask_server)
    wait = WebDriverWait(driver, 10)

    wait.until(EC.presence_of_element_located((By.ID, "title"))).send_keys(
        "Outro Livro"
    )
    driver.find_element(By.ID, "author").send_keys("Outro Autor")
    driver.find_element(By.ID, "add-book-btn").click()
    time.sleep(0.5)

    search_input = wait.until(EC.presence_of_element_located((By.ID, "search")))
    search_input.clear()
    search_input.send_keys("E2E")
    driver.find_element(By.ID, "search-btn").click()

    time.sleep(0.5)
    table_text = driver.find_element(By.ID, "books-table").text
    assert "Livro E2E Teste" in table_text
    assert "Outro Livro" not in table_text
