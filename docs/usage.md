# Usage

To use ruleminer in a project:

```python
import ruleminer
```

After installation you can use the functions in the package in for
example a Jupyter notebook.

Examples below are based the following dataset.

| Name      | Type      | Assets | TP-nonlife | TP-nonlife | Own funds | Excess |
|-----------|-----------|--------|------------|------------|-----------|--------|
| Insurer 1 | life      | 1000   | 800        | 0          | 200       | 200    |
| Insurer 2 | non-life  | 4000   | 0          | 3200       | 800       | 800    |
| Insurer 3 | non-life  | 800    | 0          | 700        | 100       | 100    |
| Insurer 4 | life      | 2500   | 1800       | 0          | 700       | 700    |
| Insurer 5 | non-lifer | 2100   | 0          | 2200       | 200       | 200    |
| Insurer 6 | life      | 9000   | 8800       | 0          | 200       | 200    |
| Insurer 7 | non-life  | 9000   | 0          | 8800       | 200       | 200    |
| Insurer 8 | life      | 9000   | 8800       | 0          | 200       | 200    |
| Insurer 9 | non-life  | 9000   | 8800       | 0          | 200       | 200    |
| Insurer 10| life      | 9000   | 0          | 8800       | 200       | 199.99 |

## Calculating metrics

Take the rule

```
if ({"Type"} == "life") then ({"TP-life"} > 0)
```

This rule says: if an insurer reports for column "Type" (noted by the curved brackets) the value "life" then the value of the column "TP-life" should be higher than zero. 

With the code

```python
templates = [{'expression': 'if ({"Type"} == "life") then ({"TP-life"} > 0)'}]

r = ruleminer.RuleMiner(templates=templates, data=df)
```

you can generate the rule metrics of this rule given the data in the DataFrame above (available with r.rules).

| id   | definition                                             | status | abs support | abs exceptions | confidence | encodings |
|------|--------------------------------------------------------|--------|-------------|----------------|------------|-----------|
| 0    | if ({"Type"} == "life") then ({"TP-life"} > 0) | None   | 5           | 0              | 1          | {}        |

There are 5 rows in the data that support this rule. There are no exceptions (i.e. where the if-clause is satisfied, but not the then-clause), so this rule has confidence 1.

## Generating rules

You can define rule templates that contain regular expressions for column names and strings. The package will then generate rules that satisfy the rule template with matching column names and strings from the DataFrame. For example column regex:
```
{"T.*"}
```

will satisfy column names:
```
{"Type"}, {"TP-life"}, {"TP-nonlife"}
```

So, if you apply the following rule:
```
if ({"T.*"} == ".*") then ({"TP.*"} > 0)
```

then the following rules are generated

| id   | definition                                                    | status | abs support | abs exceptions | confidence | encodings |
|------|---------------------------------------------------------------|--------|-------------|----------------|------------|-----------|
| 0    | if ({"Type"} == "non-life") then ({"TP-nonlife"} > 0) | None   | 4           | 1              | 0.8        | {}        |
| 1    | if ({"Type"} == "life") then ({"TP-life"} > 0)        | None   | 5           | 0              | 1          | {}        |

You can use rules without an if-clause, for example:
```
{"Assets"} > 0
```

The metrics for these rules are calculated as if the if-clause is always satisfied.

## Rule examples

The following rules can be applied to the data above:
```
{"Assets"} > 0

if ({"Type"} == ".*") then ({".*"} > 0)

if ({".*"} > 0) then (({".*"} == 0) & ({".*"} > 0))

(({".*"} + {".*"} + {".*"}) == {".*"})

(min({".*"}, {".*"}) == {".*"})

({"Own funds"} <= quantile({"Own funds"}, 0.95))

(substr({"Type"}, 0, 1) in ["a", "b"])
```

## Parameters

### Rule metrics

Several rule metrics have been proposed in the past. You can add the metrics that you want as a parameter to the ruleminer, i.e.:

```python
params = {'metrics': ['added value', 'abs support', 'abs exceptions', 'confidence']}

r = ruleminer.RuleMiner(templates=templates, data=df, params=params)
```

This will produce the desired metrics. Available metrics are:

* abs support (the absolute number of rows that satisfy the rule)

* abs exceptions (the absolute number of rows that do no satisfy the rule)

* confidence

* support

* added value

* casual confidence

* casual support

* conviction

* lift

* rule power factor

The default metrics are 'abs support', 'abs exceptions' and 'confidence'.

See for the definitions `Measures for Rules <https://mhahsler.github.io/arules/docs/measures#Measures_for_Rules>`_ from Michael Hahsler.

### Metric filters

If you want to select only rules that satisfy a certain metric threshold then you can use:
```python
params = {"filter" : {"confidence": 0.75, "abs support": 10}}
```

The default metric filter is: {"confidence": 0.5, "abs support": 2}

### Rule precision

In many situations the equal-operator when used on quantitative data is too strict as small differences can occur that you do no want to consider as exceptions to the rule. For this you can define a decimal parameter inside the params dictionary by this:

```python
params={'decimal': 3}
```

This means that comparisons like:
```
A==B
```

are translated to:
```
abs(A-B) <= 1.5*10**(-decimal)
```

If no 'decimal' parameter is provided then the absolute difference should be exactly zero.

### Precision based on datapoint values

If the precision should depend on the specific value, which is the case for some XBRL validation rules (see for example [EIOPA XBRL Taxonomy Documentation](https://dev.eiopa.europa.eu/Taxonomy/Full/2.8.0/Common/EIOPA_XBRL_Taxonomy_Documentation_2.8.0.pdf), then you can define tolerances that depend on the values in this way:

```python
params = {
    'tolerance': {
        "default": {
            (  0, 1e3): 1,
            (1e3, 1e6): 2, 
            (1e6, 1e8): 3, 
            (1e8, np.inf): 4
        }
    }
}
```

This means that if abs(value) >= 1e3 and < 1e6 then the precision of that value is -2, and so on.

To describe how it works we use the following example taken from the document mentioned above (page 41). In case of addition of two numbers A and B, where A is interval [A1, A2], and B is interval [B1, B2], the result is interval [A1+B1, A2+B2]. If the interval of the reported numbers overlap with the computed interval the rule is satisfied. An example in C = A + B, where:

* A is reported as 1499 with precision in units (decimals = 0) hence the resulting range is [1498.5, 1499.5];

* B is reported as 1502 with precision in units (decimals = 0) hence the resulting range is [1501.5, 1502.5]; and 

* C is reported as = 3000 with precision in units (decimals = 0) hence the resulting range is [2999.5, 3000.5].

Following the basic operations, the computed tolerance interval for A + B is [1498.5+1501.5, 1499.5+1502.5] = [3000, 3002]. There is an overlap between the interval of C and interval of A + B. As a result the rule is satisfied. If C was reported as 2999, the resulting interval ( with precision in units) would be [2998.5, 2999.5]. With no overlap the rule would not be  satisfied and an exception would be raised.

So to check whether 'A = B' there must be overlap between intervals [A1, A2] and [B1, B2], and that is the case if A2 >= B1 and A1 <= B2. Likewise, for the comparison 'A > B' we check whether A1 > B2 and for the comparison 'A < B' we check whether A2 < B1, and similar for operators <= and >=.

The example can be reproduced in ruleminer in the following way:
```python
df = pd.DataFrame(
    columns=[
        "A",
        "B",
        "C",
    ],
    data=[
        [1499, 1502, 3000],
        [1499, 1500, 2999],
    ],
)
```

And you define the following template:
```python
templates = [{'expression': '({"A"} + {"B"} == {"C"})'}]
```

Then you can run:
```python
r = ruleminer.RuleMiner(templates=templates, data=df, params=params)
```

And r.rules gives you the following output

| id   | definition                                                    | status | abs support | abs exceptions | confidence | encodings |
|------|---------------------------------------------------------------|--------|-------------|----------------|------------|-----------|
| 0    | ```if () then ((({"C"}-0.5*abs({"C"}.apply(__tol__, (...)``` | None   | 1           | 1              | 0.5        | {}        |


Note that the tolerance function is not stored in the formula; the 'tolerance' parameter should be passed every time a Ruleminer object is constructed.

If a rule contains minus or division operators then the signs of tolerances of the right part (that falls under the minus or division) are reversed.

If you have different tolerances per report of per data point then you can add keys in the form of regexes in the tolerance dictionary. For example the following tolerance definition would use for all columns that start with an "A" zero decimals and for the rest the default tolerance:

```python
params = {
    'tolerance': {
        "A.*": {
            (0, np.inf): 0
        },
        "default": {
            (  0, 1e3): 1,
            (1e3, 1e6): 2, 
            (1e6, 1e8): 3, 
            (1e8, np.inf): 4
        }
    }
}
```

### Implementation of precision based on datapoint values

In ruleminer, a comparison like:
```
A==B
```

is translated to:
```
    max(A+tol(A), A-tol(A)) >= min(B+tol(B), B-tol(B))

    &

    min(A+tol(A), A-tol(A)) <= max(B+tol(B), B-tol(B))
```

where tol(Α) returns ```0.5*10**(precision)```, with precision based on value A and the tolerance defined in the 'tolerance' parameter.

Comparison operators are evaluated as follows (a and b can be any (nested) mathematical expression following the grammar):
```
    == -> (max((a, +), (a, -)) >= min((b, +), (b, -))) & (min((a, +), (a, -)) <= max((b, +), (b, -)))

    != -> (max((a, +), (a, -)) < min((b, +), (b, -))) | (min((a, +), (a, -)) > max((b, +), (b, -)))

    > -> (a, +) > (b, -)

    >= -> (a, +) >= (b, -)

    < -> (a, -) < (b, +)

    <= (a, -) < (b, +)
```

Mathematical operators are evaluated as follows (a and b can be any (nested) mathematical expression following the grammar):
```
    plus((a, b), -) -> (a, -) + (b, -)

    plus((a, b), +) -> (a, +) + (b, +)

    minus((a, b), -) -> (a, -) - (b, +)

    minus((a, b), +) -> (a, +) - (b, -)

    multiply((a, b), -) -> min(
        ((a, -) * (b, -)),
        ((a, -) * (b, +)),
        ((a, +) * (b, -)),
        ((a, +) * (b, +)),
    )

    multiply((a, b), +) -> max(
        ((a, -) * (b, -)),
        ((a, -) * (b, +)),
        ((a, +) * (b, -)),
        ((a, +) * (b, +)),
    )

    divide((a, b), -) -> min(
        ((a, -) / (b, -)), 
        ((a, -) / (b, +)),
        ((a, +) / (b, -)),
        ((a, +) / (b, +)), 
    )

    divide((a, b), +) -> max(
        ((a, -) / (b, -)),
        ((a, -) / (b, +)), 
        ((a, +) / (b, -)), 
        ((a, +) / (b, +)),
    )
```

Note that the plus operator does not change the direction of the tolerance, but the minus operator does change the direction of the tolerance for the right side of the expression, i.e. the lower bound of A - B is calculated by (A-tol) - (B+tol). This also holds for negative values.

For the multiply and divide operators we need to calculate all possible directions and take the lower or upper bound. This is because A and/or B can be negative. The lower bound of A * B can be either (A+tol) * (B+tol), (A+tol) * (B-tol), (A-tol) * (B+tol), or (A-tol) * (B-tol), depending on the specific values of A and B.

### Rule results

Add the following parameters to the parameter dictionary to specify the output:

* 'output_confirmations': a boolean to specify whether the indices of the data that satisfy a rule should be returned (default=True)
* 'output_exceptions': a boolean to specify whether the indicesof the data that do not satisfy a rule should be returned (default=True)
* 'output_not_applicable': a boolean to specify whether the indices of the data to which a rule does not apply (i.e. where the antecedent is not true) should be returned (default=False)

## Evaluating results within rules

Suppose you want to use an expression with a quantile:
```
({"Own funds"} <= quantile({"Own funds"}, 0.95))
```

Then you can choose to evaluate the quantile based on the dataset on which the rules were generated or not with:
```python
params = {'evaluate_statistics': True}
```

This would produce the rule:
```
if () then ({"Own funds"}<=755.0)
```

If you use:
```python
params = {'evaluate_statistics': False}
```

then this would produce:
```
if () then ({"Own funds"}<=quantile({"Own funds"},0.95))
```

In this case the quantile is re-evaluated each time based when the rule is evaluated and the outcome will depend on the current dataset. 

The default is False (quantiles within rules are not evaluated).

## Rule pruning

By using regex in column names, it will sometimes happen that rules are identical to other rules, except that they have a different ordering of columns. For example:
```
max({"TP life"}, {"TP nonlife"})
```

is identical to:
```
max({"TP nonlife"}, {"TP life"})
```

The generated rules are therefore pruned to delete the identical rules from the generated list of rules.

* a==b is identical to b==a
* a!=b is identical to b!=a
* min(a, b) is identical to min(b, a)
* max(a, b) is identical to max(b, a)
* a+b is identical to b+a
* a*b is identical to b*a

These identities are applied recursively in rules. So the rule:
```
(({"4"}>{"3"}) & (({"2"}+{"1"})=={"0"}))
```

is identical to:
```
((({"1"}+{"2"})=={"0"}) & ({"4"}>{"3"}))
```

and will therefore be pruned from the list if the first rule is already in the list.

## Rule template grammar

The rule template describes the structure of the rule. Columns and quoted strings in the rule template can contain simple regular expressions.

The syntax of the template follows a grammar defined as follows:

* a *template* is of the form:
```
if cond_1 then cond_2
```
  or simply a single:
```
cond_1
```

* a *condition* is either a combination of *comparisons* with *logical operators* ('&' and '|') and parenthesis:
```
( comp_1 & comp_2 | comp_3 )
```

or simply a single *comparison*:
```
comp_1
```

* a *comparison* consists of a *term*, a *comparison operator* (>=, >, <=, <, != or ==) and a *term*, so::
```
term_1 > term_2
```

* a *term* can be a *number* (e.g. 3.1415 or 9), *quoted string* (a string with single or double quotes), or a *function of columns*

* a *function of columns* is either a prefix operator (min, max, quantile, or abs, in lower or uppercase) on one or more *columns*, and of the form, for example:
```
min(col_1, col_2, col_3)
```

  or infix operators with one or more columns:
```
(col_1 + col_2 * col_3)
```

* a *column* is a *string* with braces, so:
```
{"Type"}
```

  where "Type" is the name of the column in the DataFrame with the data

* a *string* consists of a-z A-Z 0-9 _ . , ; ; < > * = + - / \ ? | @ # $ % ^ & ( )

## Debugging rules

If you are using this in a Jupyter notebook you can add a the beginning::

    logging.basicConfig(stream=sys.stdout, 
                        format='%(asctime)s %(message)s',
                        level=logging.DEBUG)

Information about the rule generating process with be displayed in the notebook. Set the debug level to logging.INFO is you want less results.

