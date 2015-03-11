########################### Notice To Github Viewers #############################
# This is a mocked file intended to represent 'config.py' in the actual project. #
# Because 'config.py' contains database credentials, it has been omitted.        #
##################################################################################

import os
basedir = os.path.abspath(os.path.dirname(__file__))
WTF_CSRF_ENABLED = True

SECRET_KEY = "" # Necessary for Flask session.           Example: "S0M3S3CR3TK3Y"

HOST       = "" # OpenShift Database IP.                 Example: "127.99.99.9"
LOCALHOST  = "" # Local Database IP for Port Forwarding. Example: "127.0.0.1"
USERNAME   = "" # Database username.                     Example: "admin-user"
PASSWORD   = "" # Database password.                     Example: "secret-pw"
DB_NAME    = "" # Database name.                         Example: "expensetracker"