"""
Testes E2E adicionais — Tarefa 2.1
Usam Selenium para validar fluxos de interface não cobertos nos testes originais.
"""

import threading
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app import create_app, services

E2E_PORT = 5098
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


def test_e2e_book_shows_available_sim(driver, flask_server):
    """Livro recém-adicionado deve exibir 'Sim' na coluna Disponível."""
    driver.get(flask_server)
    wait = WebDriverWait(driver, 10)

    wait.until(EC.presence_of_element_located((By.ID, "title"))).send_keys(
        "Livro Disponivel Extra"
    )
    driver.find_element(By.ID, "author").send_keys("Autor Extra")
    driver.find_element(By.ID, "add-book-btn").click()

    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "books-table"), "Livro Disponivel Extra"
        )
    )

    table_text = driver.find_element(By.ID, "books-table").text
    assert "Sim" in table_text


def test_e2e_borrow_book_changes_status_to_nao(driver, flask_server):
    """Clicar em 'Emprestar' deve mudar o status do livro para 'Não'."""
    driver.get(flask_server)
    wait = WebDriverWait(driver, 10)

    title_input = wait.until(EC.presence_of_element_located((By.ID, "title")))
    title_input.clear()
    title_input.send_keys("Livro Para Emprestar")
    author_input = driver.find_element(By.ID, "author")
    author_input.clear()
    author_input.send_keys("Autor Borrow")
    driver.find_element(By.ID, "add-book-btn").click()

    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "books-table"), "Livro Para Emprestar"
        )
    )

    borrow_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//td[text()='Livro Para Emprestar']/following-sibling::td//button[text()='Emprestar']")
        )
    )
    borrow_btn.click()

    wait.until(
        EC.text_to_be_present_in_element((By.ID, "books-table"), "Não")
    )
    table_text = driver.find_element(By.ID, "books-table").text
    assert "Não" in table_text
