# encoding: utf8

from pyparsing import *

from .exceptions import BadQuery
from .base import BOOLEAN_TRUE_VALUES, BOOLEAN_FALSE_VALUES

import itertools

def fail(msg):
    raise BadQuery(msg)

class Token(object):
    value = None
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.value)

    def get(self):
        return self.value()

class Field(Token):
    @property
    def name(self):
        return self.value.lower()

class Operator(Token):
    @property
    def op(self):
        return self.value.lower()

class Value(Token):
    def __repr__(self):
        return self.value

class String(Value):
    pass

class Integer(Value):
    pass

class Float(Value):
    pass

class Boolean(Value):
    pass

class LogicalOp(Token):
    @property
    def op(self):
        return self.value.lower()

class Comparison(Token):
    tokens = []

    def __init__(self, tokens):
        self.tokens = list(itertools.chain(*tokens))

    def __repr__(self):
        return "{0}({1})".format(
                self.__class__.__name__,
                ' '.join([repr(t) for t in self.tokens])
        )

    def _filter_class(self, token_class):
        return [t for t in self.tokens if isinstance(t, token_class)]

    @property
    def fields(self):
        return self._filter_class(Field)

    @property
    def operator(self):
        for t in self.tokens:
            if isinstance(t, Operator):
                return t

    @property
    def values(self):
        return self._filter_class(Value)


def _build_field_expr(field_names):
    field = MatchFirst([CaselessKeyword(field_name) for field_name in field_names])
    field.setParseAction(lambda x: Field(x[0]))
    return field

def build_filter_parser(field_names):
    field = _build_field_expr(field_names)

    comparison_operator = (
            Keyword('=')
            | Keyword('!=')
            | Keyword('>=')
            | Keyword('<=')
            | Keyword('<')
            | Keyword('>')
            | CaselessKeyword('contains')
            | CaselessKeyword('icontains')
            | CaselessKeyword('startswith')
            | CaselessKeyword('istartswith')
            | CaselessKeyword('endswith')
            | CaselessKeyword('iendswith')
        )
    comparison_operator.setParseAction(lambda x: Operator(x[0]))

    num_integer = Word(nums)
    num_integer.setParseAction(lambda x: Integer(x[0]))

    num_float = Combine(
            Word(nums) + '.' + Word(nums)
    )
    num_float.setParseAction(lambda x: Float(x[0]))

    quoted_string = (
            QuotedString("'")
            ^ QuotedString('"')
    )
    quoted_string.setParseAction(lambda x: String(x[0]))

    boolean = Or(
            [CaselessKeyword(v) for v in BOOLEAN_TRUE_VALUES+BOOLEAN_FALSE_VALUES]
        )
    boolean.setParseAction(lambda x: Boolean(x[0]))

    value = (
            quoted_string
            ^ num_integer
            ^ boolean
    )

    comparison = Group(
            (field + comparison_operator + value)
            ^ (value + comparison_operator + field)
            ^ (field + comparison_operator + field)
    )
    comparison.setParseAction(lambda x: Comparison(x))

    invalid_comparison = Group(
            (
                value
                + comparison_operator 
                + value
            ).setParseAction(lambda x: fail("Value may not be compared with values: {0}".format(' '.join(x))))
    )

    logical_op = Group(
            CaselessKeyword("and")
            | CaselessKeyword("or")
    )
    logical_op.setParseAction(lambda x: LogicalOp(x[0][0]))

    statement = (comparison | invalid_comparison) + ZeroOrMore(
                logical_op + (comparison | invalid_comparison)
    )
    return statement


#result = statement.parseString("'2333' = name or is_bird = true and age >= 34", parseAll=True)


#print result.asList()
