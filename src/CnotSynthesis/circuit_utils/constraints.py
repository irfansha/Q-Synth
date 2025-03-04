# Irfansha Shaik, 31.01.2024, Aarhus

"""
TODO: Some testing is needed.
"""


class Constraints:

    def AtleastOne_constraints(self, vars):
        self.clause_list.append(vars)

    def AtmostOne_constraints(self, vars):
        # binary clauses
        for id1 in range(len(vars)):
            for id2 in range(id1 + 1, len(vars)):
                self.clause_list.append([-vars[id1], -vars[id2]])

    def ExactlyOne_constraints(self, vars):
        self.AtleastOne_constraints(vars)
        self.AtmostOne_constraints(vars)

    # unit clause:
    def unit_clause(self, var):
        self.clause_list.append([var])

    # single clause:
    def or_clause(self, clause):
        self.clause_list.append(clause)

    # equal to clause:
    def eq_clause(self, x1, x2):
        self.clause_list.append([-x1, x2])
        self.clause_list.append([x1, -x2])

    # equal to clause:
    def noteq_clause(self, x1, x2):
        self.clause_list.append([x1, x2])
        self.clause_list.append([-x1, -x2])

    # single implication with the then list:
    def if_then_clause(self, if_var, then_list):
        implication_clause = [-if_var]
        implication_clause.extend(then_list)
        self.clause_list.append(implication_clause)

    # assumes if_vars are from conjunction clause:
    def if_and_then_clause(self, if_vars, then_list):
        if_clause = []
        for var in if_vars:
            if_clause.append(-var)
        if_clause.extend(then_list)
        self.clause_list.append(if_clause)

    # assumes if_vars are from conjunction clauses:
    def if_and_then_equal_clauses(self, if_vars, x1, x2):
        self.if_and_then_clause(if_vars, [-x1, x2])
        self.if_and_then_clause(if_vars, [x1, -x2])

    # assumes if_vars are from conjunction clauses:
    def if_and_then_notequal_clauses(self, if_vars, x1, x2):
        self.if_and_then_clause(if_vars, [-x1, -x2])
        self.if_and_then_clause(if_vars, [x1, x2])

    # single implication with the then list and
    # for each item in list, if apply reverse implication
    def iff_clauses(self, if_var, then_list):
        self.if_then_clause(self, if_var, then_list)
        for var in then_list:
            self.clause_list.append([-var, if_var])

    # one clause for each variable in the then_list:
    def if_then_each_clause(self, if_var, then_list):
        for var in then_list:
            self.clause_list.append([-if_var, var])

    def iff_then_each_clause(self, if_var, then_list):
        self.if_then_each_clause(self, if_var, then_list)
        temp_clause = [if_var]
        for var in then_list:
            temp_clause.append(-var)
        self.clause_list.append(temp_clause)

    # one clause for each negated variable in the then_list:
    def if_then_each_not_clause(self, if_var, then_list):
        for var in then_list:
            self.clause_list.append([-if_var, -var])

    # Takes a list of clause variables and maps to a integer value:
    def generate_binary_format(self, clause_variables, corresponding_number):
        num_variables = len(clause_variables)
        # Representation in binary requires number of variables:
        rep_string = "0" + str(num_variables) + "b"
        bin_string = format(corresponding_number, rep_string)
        cur_variable_list = []
        # Depending on the binary string we set action variables to '+' or '-':
        for j in range(num_variables):
            if bin_string[j] == "0":
                cur_variable_list.append(-clause_variables[j])
            else:
                cur_variable_list.append(clause_variables[j])
        return cur_variable_list

    def __init__(self, clause_list):
        self.clause_list = clause_list
