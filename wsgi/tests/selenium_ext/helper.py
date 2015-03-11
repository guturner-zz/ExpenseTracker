from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

def doesWarningExist(browser, warnId, warnMsg):
    warnings = browser.find_elements(By.ID, warnId)
    for warning in warnings:
        if warnMsg in warning.text:
            return True

    return False

def navigateToCreateExpense(browser):
        "Go to create expense page"
        browser.find_element_by_id("expense_dd").click()
        browser.find_element_by_id("create_expense_btn").click()
