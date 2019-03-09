# encoding: utf8
import decimal

from dateutil.parser import parse as date_parser

from .exceptions import BadValue
from .base import BOOLEAN_TRUE_VALUES, BOOLEAN_FALSE_VALUES

def make_simple_cast(cast_func, name):
    def cast(value, field):
        try:
            return cast_func(value.strip())
        except ValueError as e:
            raise BadValue("Can not parse {0} value \"{1}\" for field \"{2}\": {3}".format(
                        name,
                        value,
                        field.name,
                        e.message
            ))
    return cast

cast_int = make_simple_cast(lambda v: int(float(v)), 'integer')
cast_float = make_simple_cast(float, 'float')
cast_date = make_simple_cast(date_parser, 'date')
cast_time = make_simple_cast(date_parser, 'time')
cast_datetime = make_simple_cast(date_parser, 'datetime')
cast_decimal = make_simple_cast(lambda v: decimal.Decimal(v), 'decimal')
cast_text = lambda v,f: v

def cast_boolean(value, field):
    if value.lower() in BOOLEAN_TRUE_VALUES:
        return True
    elif value.lower() in BOOLEAN_FALSE_VALUES:
        return False
    else:
        raise BadValue("Can not understand boolean value \"{0}\" for field {1}".format(
                    value, field.name))
