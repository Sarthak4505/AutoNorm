
# AutoNorm — Automatic Database Normalization System

## 1. Project Overview

AutoNorm is a web-based DBMS course project that helps users analyze relational schemas and normalize them using functional dependencies.

The system accepts a relation name, attributes, and functional dependencies as input. It identifies candidate keys, checks normal forms, generates decomposed relations, and provides an SQL schema preview.

## 2. Objectives

- Identify candidate keys using attribute closure.
- Analyze 1NF, 2NF, 3NF, and BCNF.
- Generate 3NF and BCNF decompositions.
- Check whether a decomposition is lossless.
- Check whether functional dependencies are preserved.
- Generate SQL CREATE TABLE statements with inferred primary and foreign key constraints.
- Validate invalid relation attributes and functional dependencies.
- Display the optional MySQL connection status.

## 3. Technology Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python and Flask
- Database: MySQL 8.0
- Database connector: mysql-connector-python
- Template engine: Jinja2

## 4. Main Features

### Input Validation
Validates relation names, attribute names, duplicate attributes, and functional dependencies.

### Candidate Key Detection
Uses attribute closure to identify candidate keys from the supplied functional dependencies.

### Normal Form Analysis
Analyzes 1NF confirmation, 2NF, 3NF, and BCNF based on the supplied schema and dependencies.

### 3NF Decomposition
Uses a minimal-cover-based synthesis approach to generate relations.

### BCNF Decomposition
Uses recursive decomposition based on functional dependencies projected onto relations.

### Lossless Join Validation
Checks whether the decomposition can reconstruct the original relation without spurious tuples under the supplied functional dependencies.

### Dependency Preservation Validation
Checks whether the union of projected functional dependencies implies the original dependencies.

### SQL Generation
Generates a preview of CREATE TABLE statements with inferred primary and foreign key constraints.

### MySQL Connection Status
Displays whether the application can connect to the configured MySQL database.

## 5. Project Workflow

1. Enter the relation name.
2. Enter the relation attributes.
3. Enter functional dependencies.
4. Confirm 1NF status.
5. Select 3NF or BCNF as the target normal form.
6. Analyze the relation.
7. Review candidate keys and normal form results.
8. Review the decomposed relations.
9. Check lossless join and dependency preservation results.
10. Review and copy the generated SQL.

## 6. Installation and Execution

### Prerequisites

- Python installed
- MySQL 8.0 installed (optional for analysis)
- Project files extracted
- A virtual environment available in the project folder

### Run the Application

Open PowerShell in the AutoNorm project directory and execute:

```powershell
.\venv\Scripts\python.exe app.py
```

Alternatively, double-click `START_AUTONORM.bat` if it is available and configured correctly.

Open the following URL in your browser:

http://127.0.0.1:5000

## 7. MySQL Configuration

The application uses these default settings:

- Host: localhost
- Port: 3307
- User: root
- Database: autonorm_db

Set the database password in PowerShell before starting the application:

```powershell
$env:AUTONORM_DB_PASSWORD="your_local_password"
```

Replace the placeholder with your local MySQL password. Do not publish passwords in source code, screenshots, or project documentation.

The application can still perform normalization analysis when MySQL is unavailable.

## 8. Testing

The following cases have been tested during development:

- Candidate key identification
- 3NF decomposition
- BCNF decomposition
- Lossless join validation
- Dependency preservation validation
- MySQL primary key and foreign key constraints
- Unknown attribute validation
- Duplicate attribute validation
- Invalid functional dependency validation

The tested examples include:

### Example 1: Employee

Attributes: EmpID, DeptID, DeptName

Functional dependencies:

- EmpID -> DeptID
- DeptID -> DeptName

Expected candidate key: EmpID

### Example 2: BCNF

Attributes: A, B, C

Functional dependencies:

- A, B -> C
- C -> B

Expected candidate keys: {A, B} and {A, C}

This example demonstrates a relation that satisfies 3NF but violates BCNF.

### Example 3: Transitive Dependency

Attributes: A, B, C

Functional dependencies:

- A -> B
- B -> C

Expected candidate key: A

This example demonstrates a transitive dependency and BCNF decomposition.

## 9. Limitations

- The 1NF check is based on user confirmation; the application does not inspect actual row values.
- The SQL preview uses VARCHAR(255) for generated attributes.
- Generated SQL is a preview and is not automatically executed by the application.
- Existing table data is not migrated into decomposed relations.
- Primary and foreign key inference should be validated against additional functional dependency patterns and edge cases.
- The normalization algorithms should be tested with more textbook examples before being considered generally reliable.
- Analysis history and persistent result storage are not implemented.

## 10. Future Enhancements

- Support for importing existing database schemas.
- Automatic data type inference.
- Execution of generated SQL after explicit user confirmation.
- Data migration support.
- Analysis history and report export.
- More extensive automated tests for normalization and decomposition algorithms.
- Improved visualization of functional dependencies and decomposition steps.

## 11. Conclusion

AutoNorm demonstrates how functional dependencies, candidate keys, normal form analysis, and relational decomposition can be combined in a web-based normalization tool. It provides an educational environment for understanding database normalization and reviewing generated SQL schemas.
