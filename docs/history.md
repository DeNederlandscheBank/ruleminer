# History

### 1.0.0 (2025-5-23)

- Bump to production version

### 0.3.18 (2025-5-9)

- Added logging of results for strings, bools and datetimes
- Updated docs
- Minor bug fix for complex expressions

### 0.3.13 (2025-5-4)

- Refactored grammar: infinite nesting, all functions caseless
- Some refactoring in parser of lists and list comprehensions

### 0.3.12 (2025-5-2)

- Added logging for comparisions without tolerance
- Fix for bug parsing list comprehensions
- Added power function to deal with interval arithmetic
- Changed 'between'-function to a >= lower_bound and a <= upper_bound instead of internal Pandas function
- Renamed interval functions by removing `_`
- Updated documentation

### 0.3.9 (2025-4-25)

- Minor change to 'between'-function: if interval is (a,b) then (min(a,b),max(a,b)) is used
- Refactoring of comparisons logging (and fix for logging of > operators)
- Added unittests for these changes
- Minor buf fix for 'between'-function

### 0.3.6 (2025-4-15)

- The right side of a 'between' comparison operator can now be a list of mathematical expressions
- Added 'not match' as comparison operator.

### 0.3.4 (2025-4-11)

- When using COUNTIF() with a single list as a parameter, all elements that evaluate to True are counted, like for example COUNTIF([K==1 FOR K in [{"A"}, {"B"}, {"C"}]]) counts the number of items that evaluate to 1.
- Added 'table' function to check whether a tuple is in an external table, for example '([{"A"}, {"B"}] in TABLE("data", ["a", "b"]))' checks for each row in columns A and B whether the tuple is in the data DataFrame with columns a and b.

### 0.3.3 (2025-4-10)

- Added 'between' and 'not between' as comparison operator to grammar
- Enforced parameters of 'between' to lowercase

### 0.3.1 (2025-3-25)

- Small fix in logging when comparing two columns

### 0.3.0 (2025-3-21)

- Applied rounding to 8 decimals in interval numbers
- Changed strictly higher-operator: (max_left >= min_right) & (min_left > max_right) (instead of max_left > min_right)
- Changed strictly lower-operator: (min_left <= max_right) & (max_left < min_right) (instead of min_left < max_right)
- deleted rule_status from rules and results dataframes

### 0.2.40 (2025-3-20)

- Added unittests for logging of intermediate results
- Fix in logging of ranges for == and !=
- Fix for consistent use of double parentheses in parser
- Changed exact function with one or two extra parameters to include lower and upper bounds
- Refactored evaluator code

### 0.2.36 (2025-3-14)

- Correction for logging and calculation of < and > comparisons
- Logging: added ; as separator between comparison results
- Logging: separated if and then comparisons
- Grammar: an extra exact-function is allowed around nested functions

### 0.2.35 (2025-3-13)

- Fix to accept NaT in tolerance function
- Fix to not suppress parentheses in pyparsing.infixNotation (Kevin's curious case)
- Fix to not apply tolerance for Pandas datetime64-types
- Fix for nan values in corr-function

### 0.2.32 (2025-3-9)

- Fix for abs-function where lower < 0 and upper > 0 (then the real lower bound is 0)
- Correction for logging of <=, <, >=, > comparisons
- Two bug fixes in corr-function

### 0.2.29 (2025-3-4)

- Added <=, <, >=, >-operators that take tolerance into account
- Applied sqrt in the corr-function
- Added round, ceil and floor-functions
- Reformatted comparison-logs: {LHS - RHS = diff} operator [LHS_min - LHS - RHS_max + RHS, LHS_max - LHS - RHS_min + RHS]

### 0.2.28 (2025-2-28)

- Added 'contains' and 'not contains' comparison operators
- Added intermediate results for unequalities
- Refactoring for logging intermediate results
- Added intermediate results for equalities and statistics

### 0.2.25 (2025-2-11)

- Improved performance of evaluation (antecedent and consequent are calculated only once)
- Added corr-function to calculate correlations
- Refactored code
- Added some preparations for logging rule evaluations
- Improved logging info of evaluation of rules

### 0.2.22 (2025-1-28)

- Fix in evaluation of unequal operators in combination with tolerances
- Fix in evaluation of equal and unequal operators when writing debug info

### 0.2.20 (2025-1-14)

- Added exact-function to grammar and parser to ignore tolerance of specific part of expression
- When exponentials like x ** y are used, for x max(0, x) is substituted to prevent imaginary numbers (as x can be negative)
- The tolerance dict can now contain None values:
	- if params={'tolerance': {"A": None', 'default': { ... }}} then tolerance is not applied to column A and other columns are set to 'default'
	- if params={'tolerance': {"default": None, "A": { ... }}} then tolerance is not applied as default except for column A
	- the keys of the tolerance dict can contain regular expressions. They are matched with columns when converting the expressions
- Added regex to dependency in pyproject.toml

### 0.2.19 (2024-12-19)

- Added mean and std functions to grammar and parser
- Changed parameter name 'evaluate_quantile' to 'evaluate_statistics' to cover mean and std
- Changed subst parameter definitions: substr(x, a, b) is now translated to x.str.slice(a-1, a+b-1)

### 0.2.18 (2024-12-17)

- Added multiply and divide functions when left and right side both contain columns (see usage documentation)
- Changed grammar to separate plus, minus on one hand and multiplication, division on other hand into separate groups (needed for first point)
- Added debugging information on lower and upper bounds when evaluating (in)equalities

### 0.2.17 (2024-12-10)

- Fix in grammar when parsing mathematical expressions in function parameters
- Fix for applying tolerances

### 0.2.16 (2024-12-8)

- Added: 'not in' as comparison operator
- Added: parameter 'apply_rules_on_indices' (default True) that allows indices to be included as columns when generating and evaluating rules (if set to False then the data DataFrame is not changed)
- Output: dtypes of results DateFrame are enforced
- Performance: changed the internal equal and unequal functions to improve performance for columns with string, bool and datetime64_ns
- Logging: change to logging when all are not applicable
- Improved parsing performance

### 0.2.13 (2024-12-3)

- Changed tolerance function to be able to evaluate string values
- Small fix when collecting results

### 0.2.12 (2024-12-2)

- Refactoring
	- Created separated CodeEvaluator class
	- Created separated RuleParser class
	- Streamlined parentheses process (resulting expressions have same parentheses as original)
- Performance
	- Deleted concats when collecting rules and results
- Parameter 'results_datatype' can now be a dict that contains per column a list of results

### 0.2.11 (2024-11-27)

- Parser of list comprehension now accepts a wider range of expressions
- Fix when applying tolerances when denominator in rule expression is negative
- Shortened internal function names

### 0.2.10 (2024-11-25)

- Added dtype=float to np.sum operations to prevent divide by zero exceptions
- In the results a row with not applicable is only included is there are no exceptions and no confirmations
- Added days / months / years functions that return the number of days / months / years of an expression (the difference between two timedate64 columns)

### 0.2.9 (2024-11-18)
- Fix for SUMIF when data DataFrame contains pd.NA's
- Added date functions to extract day, month, quarter and year from a column
- Added date functions day_name, month_name, days_in_month, daysinmonth, is_leap_year, is_year_end, dayofweek, weekofyear, weekday, week, is_month_end, is_month_start, is_year_start, is_quarter_end and is_quarter_start

### 0.2.8 (2024-11-15)

- Added 'not applicable' as a default metric to be calculated (n - confirmations - exceptions)
- Restructured the parsing of parentheses (deleted some unnecessary pyparsing.groups)
- Fix for unnecessary parentheses around power function (**)
- Fix for necessary parentheses around mathematical expressions
- Adapted all unittests accordingly

### 0.2.7 (2024-11-13)

- Better fix when applying tolerances with column names that contain strings
- Tolerances are not applied to columns where dtype is string, bool or datetime64_ns
- Logging 'finished' with rule_id per rule_id
- Fix for data DataFrames that contain 'pd.libs.missing.NAType()'

### 0.2.5 (2024-11-08)

- Fix when applying tolerances with column names that contain strings
- When applying 'output_not_applicable' the results now contain the indices of the rows to which a rule does not apply
- Added match logical operator to check if column that contains strings satisfies a regular expression

### 0.2.4 (2024-23-10)

- Added parameters 'output_confirmations', 'output_exceptions', 'output_not_applicable' to specify which results to return
- Fixed issue with parentheses in combination with max, min and abs functions
- Added parameters 'rules_datatype' and 'results_datatype' for output in pandas or polars dataframes
- Separated pandas parser code from general parser.py
- Moved tolerance code to pandas parsing instead including it in rule definition

### 0.2.3 (2024-20-21)

- Use zip for sumif and countif so list comprehensions need not to be evaluated 
- Suppressed brackets in parser and changed code accordingly
- Some refactoring for readability

### 0.2.2 (2024-10-17)

- Fix for sum, sumif, count and countif with list comprehensions

### 0.2.1 (2024-10-14)

- Added list comprehension for countif
- Fixed issue with evaluating first part of list comprehension
- Second parameter of split starts at 1

### 0.2.0 (2024-10-14)

- Converted docs to mkdocs and added ruff
- Changed setup.py to pyproject.toml
- Deleted (some) redundant parentheses in rule code
- Restructured code to parse rule tree to rule code
- Fixed incorrect parsing of negative numbers in rule expressions
- Fixed issue when applying tolerance and decimal to comparisons with strings
- Fixed issue with identifying empty strings in rule expressions

### 0.1.30 (2024-10-2)

- Added functionality for countif and sumif
- Bug fix for tolerances in combination with >=, <=, > and <
- Bug fix for tolerances in formulas like A - B - C
- Added tests for these bug fixes

### 0.1.26 (2023-4-22)

- Added additional arguments estimate, base and sample_weights to fit_ensemble_and_extract_expressions function to use more than AdaBoost
- Added decision tree functions to __init__.py

### 0.1.24 (2023-10-25)

- Added sumif and improved tolerance functionality
- Added nested conditions in functions

### 0.1.22 (2023-10-17)

- Added tolerance functionality for !=, <, <=, > and >=
- Updated docs
- Changed sum to nansum
- Added tolerance functionality for ==

### 0.1.20 (2023-8-29)

- Small fixes in evaluating rules with syntax errors

### 0.1.19 (2023-8-27)

- Small fixes rule conversion without data

### 0.1.18 (2023-8-8)

- Dedicated function added for template to rule conversion without data
- Exp sign changed from ^ to **

### 0.1.17 (2023-8-8)

- Generate rules now runs without specified data

### 0.1.16 (2023-8-3)

- Templates now do not necessarily have to contain a regex
- Bug fix when evaluating rules that contain columns that do not exist
- Templates now can start with 'if () then'

### 0.1.14 (2023-4-17)

- Nested functions added
- substr and in operators added

### 0.1.12 (2022-5-11)

- Optimizations: metric calculations are done with boolean masks of DataFrame

### 0.1.4 (2022-1-26)

- Evaluated columns in then part are now dependent on if part of rule
- Rule with quantiles added (including evaluating intermediate results)
- A number of optimization in rule generation process
- Rule power factor metric added

### 0.1.1 (2021-11-23)

- Added more documentation to the README text
- Bug fixes wrt some complex expressions
- Optimized rule generation process

### 0.1.0 (2021-11-21)

- First release on PyPI.
