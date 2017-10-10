# encoding: utf8

from rest_framework import filters, exceptions

from django.db.models import Q, F, fields

from .exceptions import BadQuery
from . import casts, parser


class SQLLikeFilterBackend(filters.BaseFilterBackend):
    filter_param_name = 'filter'
    sort_param_name = 'sort'

    parsed_filter = []
    parsed_sort = []

    # cast functions for the different types of database model fields
    value_casts = {
        fields.IntegerField: casts.cast_int,
        fields.AutoField: casts.cast_int,
        fields.FloatField: casts.cast_float,
        fields.DateField: casts.cast_date,
        fields.DateTimeField: casts.cast_datetime,
        fields.TextField: casts.cast_text,
        fields.CharField: casts.cast_text,
        fields.BooleanField: casts.cast_boolean,
    }

    def __init__(self):
        pass

    def get_filterable_fields(self, model):
        return dict([(f.name, f) for f in model._meta.fields if f.__class__ in self.value_casts])

    def _value_cast(self, field, value):
        try:
            cast_callable = self.value_casts[type(field)]
        except KeyError:
            return value
        return cast_callable(value, field)


    def build_filter(self, model, filter_value_raw):
        filters = []
        fields = self.get_filterable_fields(model)
        filter_parser = parser.build_filter_parser(fields.keys())

        join_op = parser.LogicalOp('and')
        for q in filter_parser.parseString(filter_value_raw, parseAll=True).asList():
            if isinstance(q, parser.Comparison):
                q_fields = q.fields
                left = q_fields[0]
                op = q.operator
                negate = False

                right = None
                if len(q_fields) > 1:
                    right = F(q_fields[1].name)
                else:
                    right = self._value_cast(fields[left.name], q.values[0].value)

                # find the matching operator in djangos ORM syntax
                model_op = None
                if op.op == "=":
                    model_op = "exact"
                elif op.op == "!=":
                    model_op = "exact"
                    negate = True
                elif op.op == ">":
                    model_op = "gt"
                elif op.op == ">=":
                    model_op = "gte"
                elif op.op == "<":
                    model_op = "lt"
                elif op.op == "<=":
                    model_op = "lte"
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
                    filters[-1] = filters[-1] | f
                elif join_op.op == 'and':
                    filters.append(f)
                else:
                    raise BadQuery("Unsupporteed logical operator \"{0}\"".format(join_op.op))
            elif isinstance(q, parser.LogicalOp):
                join_op = q
            else:
                raise BadQuery("Unsupported element: \"{0}\"".format(type(q)))

        return filters

    def filter_queryset(self, request, queryset, view):

        filter_value_raw = request.GET.get(self.filter_param_name, "")
        if filter_value_raw != "":
            filters = self.build_filter(queryset.model, filter_value_raw)
            #print filters
            queryset = queryset.filter(*filters)

        #print queryset.query
        return queryset

