import operator

from pyparsing import infixNotation, opAssoc, Word, alphanums, Literal

from dispatch.exceptions import InvalidFilterPolicy


def contains(a: str, b: list) -> bool:
    """Simple infix 'in' operator"""
    return a in b


def build_parser():
    operators = (
        Literal("=")
        | Literal("==")
        | Literal("eq")
        | Literal("<")
        | Literal("lt")
        | Literal(">")
        | Literal("gt")
        | Literal("<=")
        | Literal("le")
        | Literal(">=")
        | Literal("ge")
        | Literal("!=")
        | Literal("ne")
        | Literal("in")
        | Literal("and")
        | Literal("or")
    )
    field = Word(alphanums)
    value = Word(alphanums)
    comparison = field + operators + value
    query = infixNotation(
        comparison,
        [
            ("and", 2, opAssoc.LEFT, NestedExpr),
            ("or", 2, opAssoc.LEFT, NestedExpr),
            ("in", 2, opAssoc.LEFT, NestedExpr),
        ],
    )

    comparison.addParseAction(ComparisonExpr)
    return query


def operatorOperands(tokenlist: list) -> tuple:
    """Generator to extract operators and operands in pairs."""
    it = iter(tokenlist)
    while 1:
        try:
            yield (next(it), next(it))
        except StopIteration:
            break


class FilterPolicy(object):
    binary_operators = {
        "=": operator.eq,
        "==": operator.eq,
        "eq": operator.eq,
        "<": operator.lt,
        "lt": operator.lt,
        ">": operator.gt,
        "gt": operator.gt,
        "<=": operator.le,
        "le": operator.le,
        ">=": operator.ge,
        "ge": operator.ge,
        "!=": operator.ne,
        "ne": operator.ne,
        "in": contains,
    }

    multiple_operators = {"or": any, "∨": any, "and": all, "∧": all}

    def __init__(self, tree):
        self._eval = self.build_evaluator(tree)

    def __call__(self, **kwargs):
        return self._eval(kwargs)

    def build_evaluator(self, tree):
        try:
            operator, nodes = list(tree.items())[0]
        except Exception as e:
            raise InvalidFilterPolicy(f"Unable to parse tree: {tree} reason: {e}")
        try:
            op = self.multiple_operators[operator]
        except KeyError:
            try:
                op = self.binary_operators[operator]
            except KeyError:
                raise InvalidFilterPolicy(f"Unknown operator: {operator}")
            assert len(nodes) == 2  # binary operators take 2 values

            def _op(values):
                return op(values[nodes[0]], nodes[1])

            return _op
        # Iterate over every item in the list of the value linked
        # to the logical operator, and compile it down to its own
        # evaluator.
        elements = [self.build_evaluator(node) for node in nodes]
        return lambda values: op((e(values) for e in elements))


# ExampleFilter = FilterPolicy({"or": ({"eq": ("term", "bar")}, {"eq": ("term", "baz")})})


class NestedExpr(object):
    def __init__(self, tokens):
        self.value = tokens[0]

    def eval(self):
        val1 = self.value[0].eval()  # noqa
        for op, val in operatorOperands(self.value[1:]):
            print(op)
            print(val.eval())
        return True


class ComparisonExpr:
    def __init__(self, tokens):
        self.tokens = tokens

    def __str__(self):
        return str({self.tokens[1]: (self.tokens[0], self.tokens[2])})

    __repr__ = __str__
