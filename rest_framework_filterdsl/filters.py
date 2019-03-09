# encoding: utf8

from rest_framework import filters
from pyparsing import ParseException

from django.db.models import Q, F, fields as model_fields

from .exceptions import BadQuery
from . import casts, parser


class FilterDSLBackend(filters.BaseFilterBackend):

    # name of the GET parameter used for filtering
    filter_param_name = 'filter'

    # name of the GET parameter used for filtering
    sort_param_name = 'sort'

    # cast functions for the different types of database model fields
    value_casts = {
        model_fields.EmailField: casts.cast_text,
        model_fields.IntegerField: casts.cast_int,
        model_fields.SmallIntegerField: casts.cast_int,
        model_fields.PositiveIntegerField: casts.cast_int,
        model_fields.PositiveSmallIntegerField: casts.cast_int,
        model_fields.AutoField: casts.cast_int,
        model_fields.FloatField: casts.cast_float,
        model_fields.DateField: casts.cast_date,
        model_fields.DateTimeField: casts.cast_datetime,
        model_fields.TextField: casts.cast_text,
        model_fields.CharField: casts.cast_text,
        model_fields.BooleanField: casts.cast_boolean,
        model_fields.TimeField: casts.cast_time,
        model_fields.DecimalField: casts.cast_decimal,
    }
    lookups = {
        model_fields.DateField: {
            'year': model_fields.IntegerField,
            'month': model_fields.IntegerField,
            'day': model_fields.IntegerField,
            'week': model_fields.IntegerField,
            'week_day': model_fields.IntegerField,
        },
        model_fields.DateTimeField: {
            'date': model_fields.DateField,
            'year': model_fields.IntegerField,
            'month': model_fields.IntegerField,
            'day': model_fields.IntegerField,
            'week': model_fields.IntegerField,
            'week_day': model_fields.IntegerField,
            'time': model_fields.TimeField,
            'hour': model_fields.IntegerField,
            'minute': model_fields.IntegerField,
            'second': model_fields.IntegerField,
        },
        model_fields.TimeField: {
            'hour': model_fields.IntegerField,
            'minute': model_fields.IntegerField,
            'second': model_fields.IntegerField,
        }
    }

    def get_filterable_fields(self, model):
        """Returns all fields of the model accessible to the filtering.

        The default is using all fields for which casts are defined. This method
        may be overriden in subclasses to implement any other field selection"""
        fields = dict([(f.name, f) for f in model._meta.fields if f.__class__ in self.value_casts])

        lookup_fields = {}
        for field_name, field in fields.items():
            lookups = self.lookups.get(field.__class__, {})
            for lookup_name, cast_type in lookups.items():
                lookup_fields['{}__{}'.format(field_name, lookup_name)] = cast_type
        fields.update(
            lookup_fields,
            **getattr(model, 'filtering_lookups', {}),
        )

        return fields

    def _value_cast(self, field, value):
        """Cast the value for a field using the defined value_casts.

        When no cast is defined, the value will be returned in its
        original form."""
        try:
            cast_callable = self.value_casts[type(field)]
        except KeyError:
            return value
        return cast_callable(value, field)

    def parse_parts(self, parts, fields):
        filters = Q()

        def require_text_fields(parser_fields, operator_name):
            for pf in parser_fields:
                if type(fields[pf.name]) not in (model_fields.TextField, model_fields.CharField, model_fields.EmailField):
                    raise BadQuery("The operator \"{0}\" is only allowed with text fields".format(operator_name))

        join_op = parser.LogicalOp('and')

        for q in parts:
            if isinstance(q, parser.Statement):
                f = self.parse_parts(q.value, fields)
                if join_op.op == 'or':
                    filters |= f
                elif join_op.op == 'and':
                    filters &= f
                else:
                    raise BadQuery(
                        "Unsupported logical operator \"{0}\"".format(
                            join_op.op))
            elif isinstance(q, parser.Comparison):
                q_fields = q.fields
                left = q_fields[0]
                op = q.operator

                right = None
                if len(q_fields) > 1:
                    right = F(q_fields[1].name)
                else:
                    if len(q.values) != 0:
                        right = self._value_cast(fields[left.name], q.values[0].value)

                # find the matching operator in djangos ORM syntax
                model_op = None
                negate = False
                if op.op == "=":
                    model_op = "exact"
                elif op.op == "!=":
                    model_op = "exact"
                    negate = True
                elif op.op in (">", "gt"):
                    model_op = "gt"
                elif op.op in (">=", "gte"):
                    model_op = "gte"
                elif op.op in ("<", "lt"):
                    model_op = "lt"
                elif op.op in ("<=", "lte"):
                    model_op = "lte"
                elif op.op == "eq":
                    negate = op.negate
                    model_op = "exact"
                elif op.op == 'contains':
                    negate = op.negate
                    require_text_fields(q_fields, 'contains')
                    model_op = 'contains'
                elif op.op == 'icontains':
                    negate = op.negate
                    require_text_fields(q_fields, 'icontains')
                    model_op = 'icontains'
                elif op.op == 'startswith':
                    negate = op.negate
                    require_text_fields(q_fields, 'startswith')
                    model_op = 'startswith'
                elif op.op == 'istartswith':
                    negate = op.negate
                    require_text_fields(q_fields, 'istartswith')
                    model_op = 'istartswith'
                elif op.op == 'endswith':
                    negate = op.negate
                    require_text_fields(q_fields, 'endswith')
                    model_op = 'endswith'
                elif op.op == 'iendswith':
                    negate = op.negate
                    require_text_fields(q_fields, 'iendswith')
                    model_op = 'iendswith'
                elif op.op == 'isnull':
                    negate = op.negate
                    model_op = 'isnull'
                    right = True # negation happens using ~
                else:
                    raise BadQuery("Unsupported operator: \"{0}\"".format(op.op))

                f = Q(**{
                    "{0}__{1}".format(left.name, model_op): right
                })
                if negate:
                    f = ~f

                # add the new filter to the existing filterset
                # "or" has precedence over "and"
                if join_op.op == 'or':
                    filters |= f
                elif join_op.op == 'and':
                    filters &= f
                else:
                    raise BadQuery("Unsupported logical operator \"{0}\"".format(join_op.op))
            elif isinstance(q, parser.LogicalOp):
                join_op = q
            else:
                raise BadQuery("Unsupported element: \"{0}\"".format(type(q)))
        return filters

    def build_filter(self, fields, filter_value_raw):
        filter_parser = parser.build_filter_parser(fields.keys())

        return self.parse_parts(
            filter_parser.parseString(filter_value_raw, parseAll=True).asList(),
            fields,
        )

    def build_sort(self, fields, sort_value_raw):
        sort_value = []
        sort_parser = parser.build_sort_parser(fields.keys())

        for q in sort_parser.parseString(sort_value_raw, parseAll=True).asList():
            if isinstance(q, parser.SortDirective):
                prefix = ''
                if q.direction.value == '-':
                    prefix = '-'
                sort_value.append("{0}{1}".format(prefix, q.field.name))
        return sort_value

    def filter_queryset(self, request, queryset, view):
        fields = self.get_filterable_fields(queryset.model)

        try:
            if self.filter_param_name:
                filter_value_raw = request.GET.get(self.filter_param_name, "")
                if filter_value_raw != "":
                    filter = self.build_filter(fields, filter_value_raw)
                    queryset = queryset.filter(filter)
        except ParseException as e:
            raise BadQuery("Filtering position: {0}".format(e.col))

        try:
            if self.sort_param_name:
                sort_value_raw = request.GET.get(self.sort_param_name, "")
                if sort_value_raw != "":
                    sort_value = self.build_sort(fields, sort_value_raw)
                    if sort_value:
                        queryset = queryset.order_by(*sort_value)
        except ParseException as e:
            raise BadQuery("Sorting error position: {0}".format(e.col))

        #print queryset.query
        return queryset

