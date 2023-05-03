"""Main module."""

import pandas as pd
import logging
import itertools
import re
import numpy as np
import pyparsing
from collections import defaultdict
import random

from ruleminer import parser
from ruleminer.utils import generate_substitutions
from ruleminer.metrics import metrics
from ruleminer.metrics import required_variables
from ruleminer.metrics import calculate_metrics
from ruleminer.const import CONFIDENCE
from ruleminer.const import ABSOLUTE_SUPPORT
from ruleminer.const import ABSOLUTE_EXCEPTIONS
from ruleminer.const import ADDED_VALUE
from ruleminer.const import RULE_ID
from ruleminer.const import RULE_GROUP
from ruleminer.const import RULE_DEF
from ruleminer.const import RULE_STATUS
from ruleminer.const import RULE_VARIABLES
from ruleminer.const import RESULT
from ruleminer.const import INDICES
from ruleminer.const import ENCODINGS
from ruleminer.const import DUNDER_DF
from ruleminer.const import VAR_X_AND_Y
from ruleminer.const import VAR_X_AND_NOT_Y
from ruleminer.const import VAR_Z
from ruleminer.encodings import encodings_definitions


class RuleMiner:
    """
    The RuleMiner object contains rules and data

    It used three basic functions:
    - update (rule expressions, rules or data)
    - generate (rules from rule expressions and data)
    - evaluate (results from rule)
    - suggest (suggestions for data correction)
    """

    def __init__(
        self,
        templates: list = None,
        rules: pd.DataFrame = None,
        data: pd.DataFrame = None,
        params: dict = None,
    ):
        """ """
        self.params = dict()
        self.update(templates=templates, rules=rules, data=data, params=params)

    def update(
        self,
        templates: list = None,
        rules: pd.DataFrame = None,
        data: pd.DataFrame = None,
        params: dict = None,
    ):
        """ """
        logger = logging.getLogger(__name__)

        if params is not None:
            self.params = params
        self.metrics = self.params.get(
            "metrics", [ABSOLUTE_SUPPORT, ABSOLUTE_EXCEPTIONS, CONFIDENCE]
        )
        self.metrics = metrics(self.metrics)
        self.required_vars = required_variables(self.metrics)
        self.filter = self.params.get("filter", {CONFIDENCE: 0.5, ABSOLUTE_SUPPORT: 2})

        if data is not None:
            self.data = data
            self.eval_dict = {
                "MAX": np.maximum,
                "MIN": np.minimum,
                "ABS": np.abs,
                "QUANTILE": np.quantile,
                "SUM": np.sum,
                "sum": np.sum,
                "max": np.maximum,
                "min": np.minimum,
                "abs": np.abs,
                "quantile": np.quantile,
            }

            # def get_encodings():
            #     for item in encodings_definitions:
            #         exec(encodings_definitions[item])
            #     encodings = {
            #         encodings[item]: locals()[item]
            #         for item in encodings_definitions.keys()
            #     }
            #     return encodings
            # encodings = metapattern.get("encodings", None)
            # if encodings is not None:
            #     encodings_code = get_encodings()
            #     for c in self.data.columns:
            #         if c in encodings.keys():
            #             self.data[c] = eval(
            #                 str(encodings[c]) + "(s)",
            #                 encodings_code,
            #                 {"s": self.data[c]},
            #             )

        if templates is not None:
            self.templates = templates
            self.generate()

        if rules is not None:
            self.rules = rules
            self.evaluate()

        logger.info("Finished")

        return None

    def generate(self):
        """ """
        assert (
            self.templates is not None
        ), "Unable to generate rules, no templates defined."
        assert self.data is not None, "Unable to generate rules, no data defined."

        self.setup_rules_dataframe()

        for template in self.templates:
            self.generate_rules(template=template)

        return None

    def evaluate(self):
        """ """
        assert self.rules is not None, "Unable to evaluate data, no rules defined."
        assert self.data is not None, "Unable to evaluate data, no data defined."

        self.setup_results_dataframe()

        # add temporary index columns (to allow rules based on index data)
        for level in range(len(self.data.index.names)):
            self.data[
                str(self.data.index.names[level])
            ] = self.data.index.get_level_values(level=level)

        for idx in self.rules.index:

            required_vars = required_variables(
                [ABSOLUTE_SUPPORT, ABSOLUTE_EXCEPTIONS, CONFIDENCE]
            )
            expression = self.rules.loc[idx, RULE_DEF]
            rule_code = parser.python_code_index(
                expression=expression, required=required_vars
            )
            results = self.evaluate_code(expressions=rule_code, dataframe=self.data)
            len_results = {
                key: len(results[key]) for key in results if results[key] is not None
            }
            rule_metrics = calculate_metrics(
                len_results=len_results,
                metrics=[ABSOLUTE_SUPPORT, ABSOLUTE_EXCEPTIONS, CONFIDENCE],
            )
            self.add_results(idx, rule_metrics, results[VAR_X_AND_Y], results[VAR_X_AND_NOT_Y])

    def suggest(self):
        """
        Function to generate suggestions for data that do not satisfy the rules
        """
        logger = logging.getLogger(__name__)
        assert self.rules is not None, "Unable to create suggestions, no rules defined."
        assert self.data is not None, "Unable to create suggestions, no data defined."

        # add temporary index columns (to allow rules based on index data)
        for level in range(len(self.data.index.names)):
            self.data[
                str(self.data.index.names[level])
            ] = self.data.index.get_level_values(level=level)

        suggestions = []
        # a sampled list is used to change the order of the rules 
        # every time suggestions are created
        for idx in random.sample(list(self.rules.index), len(self.rules.index)):
            expression = self.rules.loc[idx, RULE_DEF]
            confidence = self.rules.loc[idx, CONFIDENCE]
            try:
                parsed, if_part, then_part = self.split_rule(expression=expression)
            except:
                logger.error(
                    'Parsing error in expression "' + str(expression) + '"'
                )
                return None
            df_code = parser.python_code_for_columns(expression=flatten(if_part))
            # df_eval is the dataframe that satisfies the if-part
            df_eval = self.evaluate_code(expressions=df_code, dataframe=self.data)[VAR_Z]
            # extract then-part suggestions
            statements = []
            self.reformulate_to_statements(then_part, statements)
            for data_index in df_eval.index:
                for statement in statements:
                    if is_column(statement[0]):
                        lhs_column = statement[0][2:-2]
                        lhs_value = self.data.loc[data_index, lhs_column]
                    elif is_string(statement[0]):
                        lhs_column = None
                        lhs_value = statement[0][1:-1]
                    else:
                        lhs_column = None
                        lhs_value = float(statement[0])
                    if is_column(statement[2]):
                        rhs_column = statement[2][2:-2]
                        rhs_value = self.data.loc[data_index, rhs_column]
                    elif is_string(statement[2]):
                        rhs_column = None
                        rhs_value = statement[2][1:-1]
                    else:
                        rhs_column = None
                        rhs_value = float(statement[2])

                    if lhs_value != rhs_value:
                        if lhs_column is not None and rhs_column is None:
                            # if left-hand-side is column value and right-hand-side is value
                            column = lhs_column
                            original_value = lhs_value
                            suggested_value = rhs_value
                        elif rhs_column is not None and lhs_column is None:
                            # if right-hand-side is column value and left-hand-side is value
                            column = rhs_column
                            original_value = rhs_value
                            suggested_value = lhs_value
                        elif lhs_column is not None and rhs_column is not None:
                            # if both left and right-hand-side are column values
                            if (pd.isna(rhs_value) or rhs=="") and not (pd.isna(lhs_value) or lhs==""):
                                column = rhs_column
                                original_value = rhs_value
                                suggested_value = lhs_value
                            if (pd.isna(lhs_value) or lhs=="") and not (pd.isna(rhs_value) or rhs==""):
                                column = lhs_column
                                original_value = lhs_value
                                suggested_value = rhs_value
                            elif random.choice([True, False]):
                                column = rhs_column
                                original_value = rhs_value
                                suggested_value = lhs_value
                            else:
                                column = lhs_column
                                original_value = lhs_value
                                suggested_value = rhs_value
                        suggestions.append(
                            [
                                data_index, 
                                column,
                                original_value,
                                suggested_value,
                                confidence,
                                idx,
                                expression,
                            ]
                        )
        # remove temporarily added index columns
        for level in range(len(self.data.index.names)):
            del self.data[str(self.data.index.names[level])]

        return pd.DataFrame(index=range(len(suggestions)),
                            columns=['row', 'column', 'original', 'suggested', 'confidence', 'rule_index', 'rule_def'],
                            data=suggestions)


    def setup_rules_dataframe(self):
        """
        Helper function to set up the rules dataframe
        """
        self.rules = pd.DataFrame(
            columns=[RULE_ID, RULE_GROUP, RULE_DEF, RULE_STATUS]
            + self.metrics
            + [ENCODINGS]
        )

    def setup_results_dataframe(self):
        """
        Helper function to set up the results dataframe
        """
        self.results = pd.DataFrame(
            columns=[RULE_ID, RULE_GROUP, RULE_DEF, RULE_STATUS]
            + [ABSOLUTE_SUPPORT, ABSOLUTE_EXCEPTIONS, CONFIDENCE]
            + [RESULT, INDICES]
        )
        self.results[RESULT] = self.results[RESULT].astype(bool)


    def generate_rules(self, template: dict):
        """
        Main function to generate rules from data given a rule template
        """
        logger = logging.getLogger(__name__)

        group = template.get("group", 0)
        encodings = template.get("encodings", {})
        template_expression = template.get("expression", None)

        # temporarily add index names as columns, so we derive rules with index names
        for level in range(len(self.data.index.names)):
            self.data[
                str(self.data.index.names[level])
            ] = self.data.index.get_level_values(level=level)

        # if the template expression is not a if then rule then it is changed into a if then rule
        try:
            parsed, if_part, then_part = self.split_rule(expression=template_expression)
        except:
            logger.error(
                'Parsing error in expression "' + str(template_expression) + '"'
            )
            return None

        sorted_expressions = {}

        candidates = []
        if_part_column_values = self.search_column_value(if_part, [])
        if_part_substitutions = [
            generate_substitutions(df=self.data, column_value=column_value)
            for column_value in if_part_column_values
        ]
        if_part_substitutions = itertools.product(*if_part_substitutions)
        logger.info("Expression for if-part (" + str(if_part) + ") generated")
        for if_part_substitution in if_part_substitutions:
            candidate, _, _, _, _ = self.substitute_list(
                expression=if_part,
                columns=[item[0] for item in if_part_column_values],
                values=[item[1] for item in if_part_column_values],
                column_substitutions=[item[0] for item in if_part_substitution],
                value_substitutions=[item[1] for item in if_part_substitution],
            )
            df_code = parser.python_code_for_columns(expression=flatten(candidate))
            df_eval = self.evaluate_code(expressions=df_code, dataframe=self.data)[VAR_Z]
            if not isinstance(df_eval, float): # then it is nan

                # substitute variables in then_part
                then_part_substituted = self.substitute_group_names(then_part, [item[2] for item in if_part_substitution])
                then_part_column_values = self.search_column_value(then_part_substituted, [])
                then_part_substitutions = [
                    generate_substitutions(df=df_eval, column_value=column_value)
                    for column_value in then_part_column_values
                ]
                if if_part_substitution != ():
                    expression_substitutions = [
                        if_part_substitution + item
                        for item in itertools.product(*then_part_substitutions)
                    ]
                else:
                    expression_substitutions = list(
                        itertools.product(*then_part_substitutions)
                    )
                template_column_values = if_part_column_values + then_part_column_values
                for substitution in expression_substitutions:

                    # substitute variables in full expression
                    parsed_substituted = self.substitute_group_names(parsed, [item[2] for item in substitution])
                    candidate_parsed, _, _, _, _ = self.substitute_list(
                        expression=parsed_substituted,
                        columns=[item[0] for item in template_column_values],
                        values=[item[1] for item in template_column_values],
                        column_substitutions=[item[0] for item in substitution],
                        value_substitutions=[item[1] for item in substitution],
                    )
                    sorted_expression = flatten_and_sort(candidate_parsed)[1:-1]
                    reformulated_expression = self.reformulate(candidate_parsed)[1:-1]
                    if sorted_expression not in sorted_expressions.keys():
                        sorted_expressions[sorted_expression] = True
                        rule_code = parser.python_code_lengths(
                            expression=reformulated_expression,
                            required=self.required_vars
                        )
                        len_results = self.evaluate_code(
                            expressions=rule_code, dataframe=self.data
                        )
                        rule_metrics = calculate_metrics(
                            len_results=len_results, metrics=self.metrics
                        )
                        logger.debug(
                            "Candidate expression "
                            + reformulated_expression
                            + " has rule metrics "
                            + str(rule_metrics)
                        )
                        if self.apply_filter(metrics=rule_metrics):
                            self.add_rule(
                                rule_id=len(self.rules.index),
                                rule_group=group,
                                rule_def=reformulated_expression,
                                rule_status="",
                                rule_metrics=rule_metrics,
                                encodings=encodings,
                            )

        # remove temporarily added index columns
        for level in range(len(self.data.index.names)):
            del self.data[str(self.data.index.names[level])]

    def substitute_group_names(self, expr: str = None, group_names_list: list = []):
        """ """
        if isinstance(expr, str):
            for group_names in group_names_list:
                if group_names is not None:
                    for idx, key in enumerate(group_names):
                        expr = re.sub("\\x0"+str(idx+1), key, expr)
            return expr
        elif isinstance(expr, list):
            return [self.substitute_group_names(i, group_names_list) for i in expr]

    def search_column_value(self, expr, column_value):
        """ """
        if isinstance(expr, str):
            if is_column(expr):
                column_value.append((expr, None))
        elif isinstance(expr, list):
            if len(expr) == 3 and is_column(expr[0]) and is_string(expr[2]):
                column_value.append((expr[0], expr[2]))
            elif len(expr) == 3 and is_column(expr[2]) and is_string(expr[0]):
                column_value.append((expr[2], expr[0]))
            else:
                for item in expr:
                    self.search_column_value(item, column_value)
        return column_value

    def split_rule(self, expression: str = ""):
        """ """
        condition = re.compile(r"if(.*)then(.*)", re.IGNORECASE)
        rule_parts = condition.search(expression)
        if rule_parts is not None:
            if '()' not in rule_parts.group(1):
                if_part = parser.RULE_SYNTAX.parse_string(rule_parts.group(1)).as_list()
            else:
                if_part = ""
            then_part = parser.RULE_SYNTAX.parse_string(rule_parts.group(2)).as_list()
        else:
            expression = "if () then " + expression
            if_part = ""
            then_part = parser.RULE_SYNTAX.parse_string(expression).as_list()
        parsed = parser.RULE_SYNTAX.parse_string(expression).as_list()
        return parsed, if_part, then_part

    def substitute_list(
        self,
        expression: str = "",
        columns: list = [],
        values: list = [],
        column_substitutions: list = [],
        value_substitutions: list = [],
    ):
        if isinstance(expression, str):
            if columns != [] and columns[0] in expression:
                # replace only first occurrence in string
                return (
                    expression.replace(
                        columns[0], '{"' + column_substitutions[0] + '"}', 1
                    ),
                    columns[1:],
                    values,
                    column_substitutions[1:],
                    value_substitutions,
                )
            elif values != [] and values[0] is not None and values[0] in expression:
                return (
                    expression.replace(
                        values[0], '"' + value_substitutions[0] + '"', 1
                    ),
                    columns,
                    values[1:],
                    column_substitutions,
                    value_substitutions[1:],
                )
            elif values != [] and values[0] is None:
                return (
                    expression,
                    columns,
                    values[1:],
                    column_substitutions,
                    value_substitutions[1:],
                )
            else:
                return (
                    expression,
                    columns,
                    values,
                    column_substitutions,
                    value_substitutions,
                )
        else:
            r = []
            for item in expression:
                (
                    item_s,
                    columns,
                    values,
                    column_substitutions,
                    value_substitutions,
                ) = self.substitute_list(
                    expression=item,
                    columns=columns,
                    values=values,
                    column_substitutions=column_substitutions,
                    value_substitutions=value_substitutions,
                )
                r.append(item_s)
            return r, columns, values, column_substitutions, value_substitutions

    def apply_filter(self, metrics: dict = {}):
        """
        This function applies the filter to the rule metrics (for example confidence > 0.75)
        """
        return all([metrics[metric] >= self.filter[metric] for metric in self.filter])

    def evaluate_code(
        self,
        expressions: dict = {},
        dataframe: pd.DataFrame = None,
        encodings: dict = {},
    ):
        """ """
        dict_values = {**{DUNDER_DF: dataframe}, **self.eval_dict}
        variables = {}
        for key in expressions.keys():
            try:
                variables[key] = eval(expressions[key], encodings, dict_values)
            except:
                variables[key] = np.nan
        return variables

    def add_rule(
        self,
        rule_id: str = "",
        rule_group: int = 0,
        rule_def: str = "",
        rule_status: str = "",
        rule_metrics: dict = {},
        encodings: dict = {},
    ):
        """
        Function to add a rule with info to the discovered rule list
        """
        row = pd.DataFrame(
            data=[
                [rule_id, rule_group, rule_def, rule_status]
                + [rule_metrics[metric] for metric in self.metrics]
                + [encodings]
            ],
            columns=self.rules.columns,
        )
        self.rules = pd.concat([self.rules, row], ignore_index=True)

    def add_results(self, rule_idx, rule_metrics, co_indices, ex_indices):
        """
        Function to add a result to the results list
        """

        nco = len(co_indices if co_indices is not None else [])
        nex = len(ex_indices if ex_indices is not None else [])

        if nco > 0:
            data = [
                [
                    self.rules.loc[rule_idx, RULE_ID],
                    self.rules.loc[rule_idx, RULE_GROUP],
                    self.rules.loc[rule_idx, RULE_DEF],
                    self.rules.loc[rule_idx, RULE_STATUS],
                    rule_metrics[ABSOLUTE_SUPPORT],
                    rule_metrics[ABSOLUTE_EXCEPTIONS],
                    rule_metrics[CONFIDENCE],
                    True,
                    None,
                ]
            ] * nco

            data = pd.DataFrame(columns=self.results.columns, data=data)
            data[INDICES] = co_indices
            self.results = pd.concat([self.results, data], ignore_index=True)

        if nex > 0:
            data = [
                [
                    self.rules.loc[rule_idx, RULE_ID],
                    self.rules.loc[rule_idx, RULE_GROUP],
                    self.rules.loc[rule_idx, RULE_DEF],
                    self.rules.loc[rule_idx, RULE_STATUS],
                    rule_metrics[ABSOLUTE_SUPPORT],
                    rule_metrics[ABSOLUTE_EXCEPTIONS],
                    rule_metrics[CONFIDENCE],
                    False,
                    None,
                ]
            ] * nex

            data = pd.DataFrame(columns=self.results.columns, data=data)
            data[INDICES] = ex_indices
            self.results = pd.concat([self.results, data], ignore_index=True)

        return None

    def reformulate_to_statements(self, expression: str = "", statements: list=None):
        """ """
        logger = logging.getLogger(__name__)
        if not isinstance(expression, str):
            if len(expression)==3:
                if expression[1] in ["==", ">=", "<="]:
                    statements.append([expression[0], "=", expression[2]])
                else:
                    logger.error(
                        'Not able to create suggestions with expression with operator ' + str(expression[1])
                    )
            elif len(expression)==1:
                self.reformulate_to_statements(expression=expression[0], statements=statements)
            else:
                logger.error(
                    'Not able to create suggestions based on expression' + str(expression)
                )
                statements = []

    def reformulate(self, expression: str = ""):
        """ """
        if isinstance(expression, str):
            return expression
        else:
            for idx, item in enumerate(expression):
                if (
                    "decimal" in self.params.keys()
                    and isinstance(item, str)
                    and (item in ["=="])
                ):
                    if not (
                        is_string(expression[idx - 1]) and len(expression[:idx]) == 1
                    ) and (
                        not (
                            is_string(expression[idx + 1])
                            and len(expression[idx + 1 :]) == 1
                        )
                    ):
                        decimal = self.params.get("decimal", 0)
                        precision = 1.5 * 10 ** (-decimal)
                        return (
                            "(abs("
                            + self.reformulate(expression[:idx])
                            + "-"
                            + self.reformulate(expression[idx + 1 :])
                            + ") <= "
                            + str(precision)
                            + ")"
                        )
                if (
                    self.params.get("evaluate_quantile", False)
                    and isinstance(item, str)
                    and item.lower() == "quantile"
                ):
                    l = ""
                    for item in expression[:idx]:
                        l += self.reformulate(item)
                    quantile_code = parser.python_code_for_intermediate(
                        flatten(expression[idx : idx + 2])
                    )
                    quantile_result = self.evaluate_code(
                        expressions=quantile_code, dataframe=self.data
                    )[VAR_Z]
                    l += str(np.round(quantile_result, 8))
                    for item in expression[idx + 2 :]:
                        l += self.reformulate(item)
                    return "(" + l + ")"

            l = ""
            for item in expression:
                l += self.reformulate(item)
            return "(" + l + ")"


def flatten_and_sort(expression: str = ""):
    """ """
    if isinstance(expression, str):
        return expression
    else:
        if isinstance(expression[0], str) and expression[0].lower() in ["min", "max"]:
            l = (
                expression[0]
                + "("
                + "".join(sorted([flatten_and_sort(item) for item in expression[1:]]))
                + ")"
            )
        elif all(
            [is_string(item) or is_column(item) or item == "," for item in expression]
        ):
            return "".join(sorted(expression))
        else:
            # find elements to sort, sort then and add sorted to string
            idx_to_sort = set()
            for idx, item in enumerate(expression):
                if isinstance(item, str) and (item in ["==", "!="]):
                    idx_to_sort.add(idx - 1)
                    idx_to_sort.add(idx + 1)
                elif isinstance(item, str) and (item == "*"):
                    idx_to_sort.add(idx - 1)
                    idx_to_sort.add(idx + 1)
                elif (
                    isinstance(item, str) and (item == "+") and ("*" not in expression)
                ):
                    idx_to_sort.add(idx - 1)
                    idx_to_sort.add(idx + 1)
                elif isinstance(item, str) and (item == "&"):
                    idx_to_sort.add(idx - 1)
                    idx_to_sort.add(idx + 1)
                elif (
                    isinstance(item, str) and (item == "|") and ("&" not in expression)
                ):
                    idx_to_sort.add(idx - 1)
                    idx_to_sort.add(idx + 1)
            sorted_items = sorted(
                [flatten_and_sort(expression[i]) for i in list(idx_to_sort)]
            )

            l = ""
            count = 0
            for idx, item in enumerate(expression):
                if idx in idx_to_sort:
                    l += sorted_items[count]
                    count += 1
                else:
                    l += flatten_and_sort(item)
        return "(" + l + ")"


def flatten(expression):
    """ """
    if isinstance(expression, str):
        return expression
    else:
        l = ""
        for item in expression:
            l += flatten(item)
        return "(" + l + ")"


def is_column(s):
    """ """
    return len(s) > 4 and (
        (s[:2] == '{"' and s[-2:] == '"}') or (s[:2] == "{'" and s[-2:] == "'}")
    )


def is_string(s):
    """ """
    return len(s) > 2 and (
        (s[:1] == '"' and s[-1:] == '"') or (s[:1] == "'" and s[-1:] == "'")
    )
