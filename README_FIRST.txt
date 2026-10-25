AUTONORM - EASY START
=====================

You do NOT need to copy each code file manually.

1. Download AutoNorm_Ready_To_Run.zip.
2. Extract the ZIP.
3. Copy the files and folders inside it into your existing AutoNorm folder:
   C:\Users\Shree\Documents\database_managment_system_course_project\AutoNorm
4. If Windows asks whether to replace files, choose Replace.
5. Do NOT delete your existing venv folder. The included launcher can reuse it.
6. Double-click START_AUTONORM.bat.
7. Wait for package installation and Flask startup.
8. Open http://127.0.0.1:5000 in your browser.

MYSQL
-----
The app still works when MySQL is not connected. If you want the status banner to show
connected, set the password in PowerShell before starting app.py:
$env:AUTONORM_DB_PASSWORD="your local password"
Do not send your password in screenshots or chat.
Defaults: localhost, port 3307, user root, database autonorm_db.

FEATURES
--------
- Relation and FD validation
- Attribute closure and candidate-key detection
- 1NF confirmation plus 2NF, 3NF, BCNF checks
- 3NF synthesis and recursive BCNF decomposition
- SQL schema preview and Copy SQL button
- Optional MySQL connection status

LIMITATIONS
-----------
This is a course-project prototype, not production-ready. The SQL preview currently uses
VARCHAR(255) and does not automatically add all PK/FK constraints or migrate existing rows.
It does not execute generated SQL or save analysis history. Test with known textbook examples.
The 1NF check is a user confirmation because actual data values are not supplied.
