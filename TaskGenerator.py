import random
from pathlib import Path
import json
import re


# expand items from lists
def ravel(items):
    for item in items:
        if isinstance(item, list):
            for subItem in ravel(item):
                yield subItem
        else:
            yield item


def expansion(start, rules):
    result = []
    for element in start:
        if element in rules:
            loc = start.index(element)
            start[loc] = random.choice(rules[element])
        result = [item for item in ravel(start)]

    for item in result:
        if not isinstance(item, list):
            if item in rules:
                result = expansion(result, rules)

    return result


undeclared_variable_regex = re.compile("^name \'(.*)\' ")


def finalize(result, local_variables):
    global undeclared_variable_regex
    res = []
    for item in result:
        try:
            res.append(str(eval(item[1:])) if item.startswith('$') else item)
        except NameError as err:
            matched = undeclared_variable_regex.match(err.args[0])
            if len(matched.groups()) != 1:
                raise RuntimeError(f"Failed to parse variable name from {err.args[0]}")

            if matched.groups()[0] not in local_variables:
                raise

            locals()[matched.groups()[0]] = local_variables[matched.groups()[0]]
            res.append(str(eval(item[1:])) if item.startswith('$') else item)

    return res


def final_expand(result, rules, iteration_limit=100):
    global undeclared_variable_regex
    to_eval = []

    done = False
    iterations = 0
    while not done and iterations < iteration_limit:
        iterations += 1
        try:
            if len(to_eval) != 0:
                eval_expr = random.choice(rules[to_eval[-1]])
                if not eval_expr.startswith('$'):
                    expanded = expansion([eval_expr], rules)[0]

                    if not expanded.startswith('$'):
                        locals()[to_eval[-1]] = expanded
                        to_eval.pop()
                        continue
                    else:
                        eval_expr = expanded

                eval_expr = eval_expr[1:]
                exec(to_eval[-1] + "= " + eval_expr)
                var = to_eval.pop()
                continue
            else:
                result = finalize(result, locals())
            done = True
        except NameError as err:
            matched = undeclared_variable_regex.match(err.args[0])
            if len(matched.groups()) != 1:
                raise RuntimeError(f"Failed to parse variable name from {err.args[0]}")

            to_eval.append(matched.groups()[0])

    assert iterations < iteration_limit, f'Iterations limit ({iteration_limit}) exceeded. ' \
                                         f'Looks like expansion will never end'

    return result


class TaskGenerator:
    def __init__(self, random_seed: int = 0):
        random.seed(random_seed)

    def import_module(self, module_name: str):
        from importlib import import_module
        globals()[module_name] = import_module(module_name)

    def json_rules_to_str(self, json_path: Path, root_state: str) -> (str, dict):
        with open(json_path, 'r') as f:
            rules = json.load(f)

        result = [root_state]
        result = expansion(result, rules)
        result = final_expand(result, rules)
        variables = {key: value for key, value in zip(rules[root_state][0], result) if key in rules}
        return ' '.join(result), variables
