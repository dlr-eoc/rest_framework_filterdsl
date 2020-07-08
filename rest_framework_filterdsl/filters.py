# encoding: utf8

from rest_framework import filters, exceptions as rest_exceptions
from pyparsing import ParseException

from django.core import exceptions as django_exceptions
from django.db.models import Q, F
from rest_framework.serializers import as_serializer_error

from .exceptions import BadQuery
from . import parser


class FilterDSLBackend(filters.BaseFilterBackend):

    # name of the GET parameter used for filtering
    filter_param_name = 'filter'

    # name of the GET parameter used for filtering
    sort_param_name = 'sort'

    def parse_parts(self, parts):
        filters = Q()

        join_op = parser.LogicalOp('and')

        for q in parts:
            if isinstance(q, parser.Statement):
                f = self.parse_parts(q.value)
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
                        right = q.values[0].value

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
                    model_op = 'contains'
                elif op.op == 'icontains':
                    negate = op.negate
                    model_op = 'icontains'
                elif op.op == 'startswith':
                    negate = op.negate
                    model_op = 'startswith'
                elif op.op == 'istartswith':
                    negate = op.negate
                    model_op = 'istartswith'
                elif op.op == 'endswith':
                    negate = op.negate
                    model_op = 'endswith'
                elif op.op == 'iendswith':
                    negate = op.negate
                    model_op = 'iendswith'
                elif op.op == 'isnull':
                    negate = op.negate
                    model_op = 'isnull'
                    right = True # negation happens using ~
                else:
                    raise BadQuery("Unsupported operator: \"{0}\"".format(op.op))

                f = Q(**{
                    "{0}__{1}".format(left.value, model_op): right
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

    def build_filter(self, filter_value_raw):
        filter_parser = parser.build_filter_parser()

        return self.parse_parts(
            filter_parser.parseString(filter_value_raw, parseAll=True).asList(),
        )

    def build_sort(self, sort_value_raw):
        sort_value = []
        sort_parser = parser.build_sort_parser()

        for q in sort_parser.parseString(sort_value_raw, parseAll=True).asList():
            if isinstance(q, parser.SortDirective):
                prefix = ''
                if q.direction.value == '-':
                    prefix = '-'
                sort_value.append("{0}{1}".format(prefix, q.field.name))
        return sort_value

    def filter_queryset(self, request, queryset, view):
        try:
            if self.filter_param_name:
                filter_value_raw = request.GET.get(self.filter_param_name, "")
                if filter_value_raw != "":
                    filter = self.build_filter(filter_value_raw)
                    queryset = queryset.filter(filter)
        except ParseException as e:
            raise BadQuery("Filtering position: {0}".format(e.col))
        except django_exceptions.ValidationError as exc:
            raise rest_exceptions.ValidationError(detail=as_serializer_error(exc))
        except django_exceptions.FieldError as exc:
            raise BadQuery("Bad filter: {0}".format(exc))

        try:
            if self.sort_param_name:
                sort_value_raw = request.GET.get(self.sort_param_name, "")
                if sort_value_raw != "":
                    sort_value = self.build_sort(sort_value_raw)
                    if sort_value:
                        queryset = queryset.order_by(*sort_value)
        except ParseException as e:
            raise BadQuery("Sorting error position: {0}".format(e.col))
        except django_exceptions.FieldError as exc:
            raise BadQuery("Bad sorting: {0}".format(exc))

        #print queryset.query
        return queryset

