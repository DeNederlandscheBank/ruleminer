# History

### 0.1.0 (2021-11-21)

- First release on PyPI.

### 0.1.1 (2021-11-23)

- Added more documentation to the README text

### 0.1.2 (2022-1-20)

- Bug fixes wrt some complex expressions

### 0.1.3 (2022-1-26)

- Optimized rule generation process

### 0.1.4 (2022-1-26)

- Evaluated columns in then part are now dependent on if part of rule

### 0.1.5 (2022-1-30)

- Rule with quantiles added (including evaluating intermediate results)

### 0.1.6 and 0.1.7 (2022-2-1)

- A number of optimization in rule generation process

### 0.1.8 (2022-2-3)

- Rule power factor metric added

### 0.1.12 (2022-5-11)

- Optimizations: metric calculations are done with boolean masks of DataFrame

### 0.1.14 (2023-4-17)

- Nested functions added
- substr and in operators added

### 0.1.16 (2023-8-3)

- Templates now do not necessarily have to contain a regex
- Bug fix when evaluating rules that contain columns that do not exist
- Templates now can start with 'if () then'

### 0.1.17 (2023-8-8)

- Generate rules now runs without specified data

### 0.1.18 (2023-8-8)

- Dedicated function added for template to rule conversion without data
- Exp sign changed from ^ to **

### 0.1.19 (2023-8-27)

- Small fixes rule conversion without data

### 0.1.20 (2023-8-29)

- Small fixes in evaluating rules with syntax errors

### 0.1.21 (2023-10-11)

- Changed sum to nansum
- Added tolerance functionality for ==

### 0.1.22 (2023-10-17)

- Added tolerance functionality for !=, <, <=, > and >=
- Updated docs

### 0.1.23 (2023-10-18)

- Added nested conditions in functions

### 0.1.24 (2023-10-25)

- Added sumif and improved tolerance functionality

### 0.1.26 (2023-4-22)

- Added additional arguments estimate, base and sample_weights to fit_ensemble_and_extract_expressions function to use more than AdaBoost
- Added decision tree functions to __init__.py

### 0.1.28 (2023-5-3)

- Bug fix

### 0.1.30 (2024-10-2)

- Added functionality for countif and sumif
- Bug fix for tolerances in combination with >=, <=, > and <
- Bug fix for tolerances in formulas like A - B - C
- Added tests for these bug fixes

### 0.2.0 (2024-10-14)

- Converted docs to mkdocs and added ruff
- Changed setup.py to pyproject.toml
- Deleted (some) redundant parentheses in rule code
- Restructured code to parse rule tree to rule code
- Fixed incorrect parsing of negative numbers in rule expressions
- Fixed issue when applying tolerance and decimal to comparisons with strings
- Fixed issue with identifying empty strings in rule expressions

### 0.2.1 (2024-10-14)

- Added list comprehension for countif
- Fixed issue with evaluating first part of list comprehension
- Second parameter of split starts at 1

### 0.2.2 (2024-10-17)

- Fix for sum, sumif, count and countif with list comprehensions

### 0.2.3 (2024-20-21)

- Use zip for sumif and countif so list comprehensions need not to be evaluated 
- Suppressed brackets in parser and changed code accordingly
- Some refactoring for readability

### 0.2.4 (2024-23-10)

- Added parameters 'output_confirmations', 'output_exceptions', 'output_not_applicable' to specify which results to return
- Fixed issue with parenthesis in combination with max, min and abs functions
- Added parameters 'rules_datatype' and 'results_datatype' for output in pandas or polars dataframes
- Separated pandas parser code from general parser.py
- Moved tolerance code to pandas parsing instead including it in rule definition

### 0.2.5 (2024-11-08)

- Fix when applying tolerances with column names that contain strings
- When applying 'output_not_applicable' the results now contain the indices of the rows to which a rule does not apply
- Added match logical operator to check if column that contains strings satisfies a regular expression

### 0.2.6 (2024-11-12)

- Better fix when applying tolerances with column names that contain strings
- Tolerances are not applied to columns where dtype is string, bool or datetime64_ns
- Logging 'finished' with rule_id per rule_id
- Fix for data DataFrames that contain 'pd.libs.missing.NAType()'