from setuptools import setup

setup(name='Flask Expense Tracker - Dev',
      version='0.5',
      description='Multi-user expense tracker.',
      author='Zachary Black, Guy Turner',
      author_email='flask.expense.tracker@gmail.com',
      url='http://flask-app.rhcloud.com/',
      install_requires=['Flask', 'MarkupSafe', "flask-security", "WTForms", "wtforms-html5",
                        "flask-sqlalchemy", "MySQL-python", "flask-moment"],
)
