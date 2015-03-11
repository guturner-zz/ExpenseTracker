# ExpenseTracker 
Python Flask Web Application for Managing Expenses.

Want to try out the official development environment? Check it out here! http://dev-expensetracker.rhcloud.com/

**App Not Loading?** OpenShift places apps on free accounts in an 'idle' state after periods of inactivity. Try hitting the URL above and then waiting 5 minutes, the app should restart on its own.

**Important!** Although I'm the only contributor to this repository, this was a collaborative project between myself and [Zachary Black](https://github.com/zacharybblack). The project's full code-base is held in our OpenShift repository. We chose not to link that repository to GitHub to prevent accidentally committing sensitive data (see note below).

# Intro
Demonstrates knowledge of:
* Python
* [Flask](http://flask.pocoo.org/) (Web Framework)
* [OpenShift](https://www.openshift.com/) (Platform as a Service)
* User Authentication
* Relational Databases (via MySQL and [SQLAlchemy](http://www.sqlalchemy.org/))
* HTML5 and Twitter Bootstrap (Shout-out to [SB-Admin-2](http://startbootstrap.com/template-overviews/sb-admin-2/)!)
* [Selenium](http://www.seleniumhq.org/) (Browser Automated Regression Testing)

# Considerations
### Sensitive Information
Some files in this project (e.g. 'config.py') are mocked to suppress sensitive data.

### Database
This project relies on a MySQL database. '/wsgi/app/models.py' contains all relevant table information.

Try leveraging SQLAlchemy to create your database for you!
```python
app = Flask(__name__)
with app.app_context():
    db.create_all()
```

# Run This App Locally
Follow these steps to setup your own Expense Tracker:

1. Clone this project on your local machine:
    * ```git clone https://github.com/guturner/ExpenseTracker.git```
2. Create a MySQL database.
    * Create your own version of 'config.py' in the root directory (see 'config-fake.py') and populate it with your database information.
    * Generate your tables (either by hand as per 'wsgi/app/models.py' or via SQLAlchemy's ```db.create_all()```).
3. Run 'run.py'.
