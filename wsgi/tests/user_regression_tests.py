import unittest
from selenium import webdriver
from wsgi.app import app
from wsgi.app.models import *
from selenium_ext.helper import *

class NewUserTests(unittest.TestCase):
    emailAddressUserOne = "regressiontestuser1@flask.expensetracker.com"
    firstNameUserOne = "a"
    passwordUserOne = "a"
    emailAddressUserTwo = "regressiontestuser2@flask.expensetracker.com"
    firstNameUserTwo = "b"
    passwordUserTwo = "b"

    """
    @classmethod
    def setUpClass(self):
        # Setup localhost connection:
        app.config["HOST"] = app.config["LOCALHOST"]
        app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://' + app.config["USERNAME"] + ':' + app.config["PASSWORD"] + '@' + app.config["HOST"] + ':3306/' + app.config["DB_NAME"]

        self.browser = webdriver.Firefox()

    @classmethod
    def tearDownClass(self):
        self.browser.quit()
    """

    def setUp(self):
        # Setup localhost connection:
        app.config["HOST"] = app.config["LOCALHOST"]
        app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://' + app.config["USERNAME"] + ':' + app.config["PASSWORD"] + '@' + app.config["HOST"] + ':3306/' + app.config["DB_NAME"]

        self.browser = webdriver.Firefox()

        # Remove users from database:
        with app.app_context():
            household = Household.query.filter_by(name="testHousehold").first()
            if household:
                db.session.delete(household)
                db.session.commit()
            household2 = Household.query.filter_by(name="Regression Test Household").first()
            if household2:
                db.session.delete(household2)
                db.session.commit()
            user1 = User.query.filter_by(email=self.emailAddressUserOne).first()
            if user1:
                db.session.delete(user1)
                db.session.commit()
            user2 = User.query.filter_by(email=self.emailAddressUserTwo).first()
            if user2:
                db.session.delete(user2)
                db.session.commit()


    def tearDown(self):
        self.browser.quit()

        # Remove users from database:
        with app.app_context():
            household = Household.query.filter_by(name="testHousehold").first()
            if household:
                db.session.delete(household)
                db.session.commit()
            household2 = Household.query.filter_by(name="Regression Test Household").first()
            if household2:
                db.session.delete(household2)
                db.session.commit()
            user1 = User.query.filter_by(email=self.emailAddressUserOne).first()
            if user1:
                db.session.delete(user1)
                db.session.commit()
            user2 = User.query.filter_by(email=self.emailAddressUserTwo).first()
            if user2:
                db.session.delete(user2)
                db.session.commit()

    def testCreateUserNewHousehold(self):
        self.browser.get("http://127.0.0.1:5000/")

        # Assert user doesn't exist in db:
        with app.app_context():
            user1 = User.query.filter_by(email=self.emailAddressUserOne).first()
            assert(not user1)

        # Assert logged out:
        assert (self.browser.find_element_by_id("no_account_msg").is_displayed())

        # Go to signup page:
        self.browser.find_element_by_id("create_account_btn").click()
        assert (self.browser.title == "Flask Expense Tracker: Signup")

        ###
        # Test ID:     1
        # Description: User clicks "Signup!" when all fields are empty.
        # Result:      Warning message says please enter name, email, and password (and confirm password).
        ###

        # Submit form:
        self.browser.find_element_by_id("signup_btn").click()

        # Check warning messages:
        assert(doesWarningExist(self.browser, "signup_warn", "Please enter your first name."))
        assert(doesWarningExist(self.browser, "signup_warn", "Please enter your e-mail address."))
        assert(doesWarningExist(self.browser, "signup_warn", "Please enter a password."))
        assert(doesWarningExist(self.browser, "signup_warn", "Please confirm your password."))

        ###
        # Test ID:     2
        # Description: User clicks "Signup!" with incorrect email format.
        # Result:      Warning message says please enter email formatted correctly.
        ###
        self.browser.find_element_by_id("email").send_keys("abc")

        # Submit form:
        self.browser.find_element_by_id("signup_btn").click()

        # Check warning messages:
        assert(doesWarningExist(self.browser, "signup_warn", "Your e-mail address must follow the form: example@website.com"))

        # Reset email field:
        self.browser.find_element_by_id("email").clear()

        ###
        # Test ID:     3
        # Description: User clicks "Signup!" when password fields don't match.
        # Result:      Warning message says your password doesn't match.
        ###
        # Must fill out first name and email fields for password validation to run:
        self.browser.find_element_by_id("firstName").send_keys("RegressionTestUser1")
        self.browser.find_element_by_id("email").send_keys(self.emailAddressUserOne)
        self.browser.find_element_by_id("pwd").send_keys("abc")
        self.browser.find_element_by_id("confirmPwd").send_keys("xyz")

        # Submit form:
        self.browser.find_element_by_id("signup_btn").click()

        # Check warning messages:
        assert(doesWarningExist(self.browser, "signup_warn", "Your passwords don't match."))

        ###
        # Test ID:     4
        # Description: User clicks "Signup!" without providing either an association key or a household name.
        # Result:      Warning message asks you to enter a key or a household name.
        ###

        # Clear form:
        self.browser.find_element_by_id("first_name_txt").clear()
        self.browser.find_element_by_id("email_txt").clear()

        # Fill out form:
        self.browser.find_element_by_id("first_name_txt").send_keys("RegressionTestUser1")
        self.browser.find_element_by_id("email_txt").send_keys(self.emailAddressUserOne)
        self.browser.find_element_by_id("pwd").send_keys("admin")
        self.browser.find_element_by_id("confirm_password_txt").send_keys("admin")

        # Submit form:
        self.browser.find_element_by_id("signup_btn").click()

        # Check warning messages:
        assert(doesWarningExist(self.browser, "signup_warn", "You must either join a household or create a new one."))

        ###
        # Test ID:     5
        # Description: User clicks "Signup!" while providing both an association key or a household name.
        # Result:      Warning message asks you to enter either a key or a household name, not both.
        ###

        # Must provide password again:
        self.browser.find_element_by_id("password_txt").send_keys("admin")
        self.browser.find_element_by_id("confirm_password_txt").send_keys("admin")

        # Key and household name:
        self.browser.find_element_by_id("household_key_txt").send_keys("12345678901234567890123456789012")
        self.browser.find_element_by_id("household_name_txt").send_keys("Regression Test Household")

        # Submit form:
        self.browser.find_element_by_id("signup_btn").click()

        # Check warning messages:
        assert(doesWarningExist(self.browser, "signup_warn", "You cannot both join and create a household, choose one."))

        ###
        # Test ID:     6
        # Description: User clicks "Signup!" while providing an incorrect association key.
        # Result:      Warning message tells you key is invalid.
        ###

        # Must provide password again:
        self.browser.find_element_by_id("password_txt").send_keys("admin")
        self.browser.find_element_by_id("confirm_password_txt").send_keys("admin")

        # Get rid of household name:
        self.browser.find_element_by_id("household_name_txt").clear()

        # Submit form:
        self.browser.find_element_by_id("signup_btn").click()

        # Check warning messages:
        assert(doesWarningExist(self.browser, "signup_warn", "That household association key is invalid."))

        ###
        # Test ID:     7
        # Description: User clicks "Signup!" with correct information and a new household name.
        # Result:      User is redirected to the index page. A new user is inserted into the database along with a
        #              new household name and unique HID.
        ###

        # Must provide password again:
        self.browser.find_element_by_id("password_txt").send_keys("admin")
        self.browser.find_element_by_id("confirm_password_txt").send_keys("admin")

        # Clear association key:
        self.browser.find_element_by_id("household_key_txt").clear()

        # Add household name:
        self.browser.find_element_by_id("household_name_txt").send_keys("Regression Test Household")

        # Submit form:
        self.browser.find_element_by_id("signup_btn").click()

        # Assert user exists:
        with app.app_context():
            user1      = User.query.filter_by(email=self.emailAddressUserOne).first()
            assert(user1)
            household1 = Household.query.filter_by(id=user1.hid).first()
            assert(household1)


        ###
        # Test ID:     8
        # Description: Submit correct user information, and an existing household association key.
        # Result:      User is redirected to the index page. A new user is inserted into the database with
        #              the hid associated with the association key.
        ###

        #logging out
        self.browser.find_element_by_id("username_dd").click()
        self.browser.find_element_by_id("logout_btn").click()

        #get started click
        self.browser.find_element_by_id("create_account_btn").click()
        assert (self.browser.title == "Flask Expense Tracker: Signup")

        #enter user credentials
        self.browser.find_element_by_id("first_name_txt").send_keys(self.firstNameUserTwo)
        self.browser.find_element_by_id("email_txt").send_keys(self.emailAddressUserTwo)
        self.browser.find_element_by_id("password_txt").send_keys(self.passwordUserTwo)
        self.browser.find_element_by_id("confirm_password_txt").send_keys(self.passwordUserTwo)

        #association key
        with app.app_context():
            userOne = db.session.query(User).join(Household).filter(User.hid == Household.id,
                                                             User.email == self.emailAddressUserOne).first()
            userOneHousehold = Household.query.filter_by(id = userOne.hid).first()
            associationKey = userOneHousehold.key

        self.browser.find_element_by_id("household_key_txt").send_keys(associationKey)

        #signup button
        self.browser.find_element_by_id("signup_btn").click()
        assert (self.browser.title == "Flask Expense Tracker: Home Page")

        with app.app_context():
            userTwo = db.session.query(User).join(Household).filter(User.hid == Household.id,
                                                             User.email == self.emailAddressUserTwo).first()
        #User one and two must be in the same household
        assert userTwo.hid == userOne.hid

    def testExpenseAdd(self):
        self.browser.get("http://127.0.0.1:5000/")

        #create two users in the same household
        with app.app_context():
            household = Household("testHousehold")
            db.session.add(household)
            db.session.commit()
            household = Household.query.filter_by(name="testHousehold").first()
            userOne = User(self.firstNameUserOne, "", self.emailAddressUserOne, self.passwordUserOne, household.id)
            userOne.set_password(self.passwordUserOne)
            userTwo = User(self.firstNameUserTwo, "", self.emailAddressUserTwo, self.passwordUserTwo, household.id)
            userTwo.set_password(self.passwordUserTwo)
            db.session.add(userOne)
            db.session.add(userTwo)
            db.session.commit()

            assert User.query.filter_by(email=self.emailAddressUserOne).first()
            assert User.query.filter_by(email=self.emailAddressUserTwo).first()
            assert User.query.filter_by(email=self.emailAddressUserOne).first().hid == household.id
            assert User.query.filter_by(email=self.emailAddressUserTwo).first().hid == household.id

        #login user one
        self.browser.find_element_by_id("welcome_dd").click()
        self.browser.find_element_by_id("login_btn").click()
        self.browser.find_element_by_id("email").send_keys(self.emailAddressUserOne)
        self.browser.find_element_by_id("password").send_keys(self.passwordUserOne)
        self.browser.find_element_by_id("login_submit_btn").click()

        ###
        # Test ID:     1, 3, 7
        # Description: Submit an expense with no fields filled in or checked.
        # Result:      User Receives the following errors: "Please enter and expense description.",
        #               "Please enter an amount.", and "Please enter a date for your expense."
        ###

        #navigate to expense create page
        navigateToCreateExpense(self.browser)

        #clear date field
        self.browser.find_element_by_id("date").clear()

        #submit expense
        self.browser.find_element_by_id("submit_expense_btn").click()

        #assert the 3 error messages
        assert(doesWarningExist(self.browser, "expense_add_warning", "Please enter an expense description."))
        assert(doesWarningExist(self.browser, "expense_add_warning", "Please enter an amount."))
        assert(doesWarningExist(self.browser, "expense_add_warning", "Please enter a date for your expense."))

        ###
        # Test ID:     2
        # Description: Create an Expense with more than 64 characters with correct amount and date input
        #             (They are required).
        # Result:      The user receives an error stating their expense description is too long.
        ###

        navigateToCreateExpense(self.browser)

        #correctly fill amount field
        self.browser.find_element_by_id("amount").send_keys("1.00")

        #submit 65 a characters for description
        self.browser.find_element_by_id("name").send_keys("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.browser.find_element_by_id("submit_expense_btn").click()

        #test warning message
        assert(doesWarningExist(self.browser, "expense_add_warning", "Expense name must not exceed 64 characters."))

        ###
        # Test ID:     4
        # Description: Create an expense with a non numerical amount.
        # Result:      The user receives an error stating the expense amounts must be numbers.
        ###

        navigateToCreateExpense(self.browser)

        #send correct desc info
        self.browser.find_element_by_id("name").send_keys("a")

        #submit non number to amount field
        self.browser.find_element_by_id("amount").send_keys("a")
        self.browser.find_element_by_id("submit_expense_btn").click()

        #assert warning message
        assert(doesWarningExist(self.browser, "expense_add_warning", "Expense amount must be a number."))

        ###
        # Test ID:     5
        # Description: Create an expense with a negative number
        # Result:      The user receives an error stating the expense amount must be positive.
        ###

        browser = navigateToCreateExpense(self.browser)

        #send correct desc info
        self.browser.find_element_by_id("name").send_keys("a")

        #send negative number to amount
        self.browser.find_element_by_id("amount").send_keys("-0.1")
        self.browser.find_element_by_id("submit_expense_btn").click()

        #assert warning message
        assert(doesWarningExist(self.browser, "expense_add_warning", "Expense amount must be greater than 0."))

        ###
        # Test ID:     6
        # Description: Create an expense with a 0
        # Result:      The user receives an error stating the expense amount must be positive.
        ###

        browser = navigateToCreateExpense(self.browser)

        #send correct desc info
        self.browser.find_element_by_id("name").send_keys("a")

        #send negative number to amount
        self.browser.find_element_by_id("amount").send_keys("-0.1")
        self.browser.find_element_by_id("submit_expense_btn").click()

        #assert warning message
        assert(doesWarningExist(self.browser, "expense_add_warning", "Expense amount must be greater than 0."))

        ###
        # Test ID:     8
        # Description: Create an expense without a correctly formatted date.
        # Result:      The user receives an error that the date is formatted incorrectly
        ###

        browser = navigateToCreateExpense(self.browser)

        #send correct desc and amount info
        self.browser.find_element_by_id("name").send_keys("a")
        self.browser.find_element_by_id("amount").send_keys("1.00")

        #send incorrect date format
        self.browser.find_element_by_id("date").send_keys("1")
        self.browser.find_element_by_id("submit_expense_btn").click()

        assert(doesWarningExist(self.browser, "expense_add_warning",
                                "Invalid expense date format. Please use YYYY-MM-DD."))

        ###
        # Test ID:     9
        # Description: Create an expense without any participants.
        # Result:      The user receives an error that there must be at least one participant.
        ###

        browser = navigateToCreateExpense(self.browser)

        #send correct desc, date, and amount info
        self.browser.find_element_by_id("name").send_keys("a")
        self.browser.find_element_by_id("amount").send_keys("1.00")
        self.browser.find_element_by_id("date").send_keys("2014-01-01")

        self.browser.find_element_by_id("submit_expense_btn").click()

        assert(doesWarningExist(self.browser, "expense_add_warning",
                                "You must add at least one participant besides the currently logged in user."))

        ###
        # Test ID:     10
        # Description: Create an expense where currently logged in user is the only participant.
        # Result:      The user receives an error that there must be at least one participant
        ###

        browser = navigateToCreateExpense(self.browser)

        #send correct desc, date, and amount info
        self.browser.find_element_by_id("name").send_keys("a")
        self.browser.find_element_by_id("amount").send_keys("1.00")
        self.browser.find_element_by_id("date").send_keys("2014-01-01")

        #click only the logged in user's participant checkbox
        self.browser.find_element_by_id("participant-0-checkBox").click()
        self.browser.find_element_by_id("submit_expense_btn").click()

        assert(doesWarningExist(self.browser, "expense_add_warning",
                                "You must add at least one participant besides the currently logged in user."))

        ###
        # Test ID:     11
        # Description: Create  expense Description: "Test A" Amount: 1 Due Date:
        #              Default, between user A and B. Use Auto Split button.
        # Result:      The expense is properly submitted and the user is taken to the view expenses page.
        #              "expenses/view". The household page now shows user B owing user A $1.00.
        #              Expense participants are messaged about the new expense.
        ###

        browser = navigateToCreateExpense(self.browser)

        #send correct desc, and amount info
        self.browser.find_element_by_id("name").send_keys("Test A")
        self.browser.find_element_by_id("amount").send_keys("1")

        #select user 1 and 2 as participants and autosplit
        self.browser.find_element_by_id("participant-0-checkBox").click()
        self.browser.find_element_by_id("participant-1-checkBox").click()
        self.browser.find_element_by_id("auto_split_button").click()

        #submit
        self.browser.find_element_by_id("submit_expense_btn").click()

        #asserts on expense view page
        assert (self.browser.title == "Flask Expense Tracker: View Expenses")
        with app.app_context():
            assert Expense.query.filter_by(name="Test A").first()
            assert Message.query.filter_by()

        #assert household page shows who owes who
        self.browser.find_element_by_id("household_btn").click()
        #self.browser.find_element_by_xpath("id('page-wrapper')/x:div/x:div[2]/x:div/x:table/x:tbody/x:tr/x:td[3]").get_attribute("value")

if __name__ == "__main__":
    unittest.main()