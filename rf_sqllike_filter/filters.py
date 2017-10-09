# encoding: utf8

from rest_framework import filters, exceptions
import sqlparse
from sqlparse.sql import Where
from sqlparse import tokens as T, sql

from django.db.models import Q, F, fields

from .exceptions import BadQuery
from . import casts

def make_token_keyword_filter(excluded_keywords=[]):
    def do_filter(tokens):
        def do_keep(token):
            return token.ttype not in (T.Whitespace, T.Punctuation, T.Newline) \
                    and not (token.ttype == T.Keyword and t.value.lower() in excluded_keywords)
        return [t for t in tokens if do_keep(t)]
    return do_filter

def dump(token, level = 0):
    if type(token) in (list, tuple):
        for t in token:
            dump(t, level+1)
    else:
        print("{0}{1}[{2}]: {3}".format(
                    level * "  ",
                    type(token),
                    token.ttype,
                    token.value
        ))
        if type(token) in (sql.Comparison, sql.Parenthesis):
            for t in make_token_keyword_filter()(token.tokens):
                dump(t, level+1)

class SQLLikeFilterBackend(filters.BaseFilterBackend):
    where_param_name = 'filter'
    sort_param_name = 'sort'

    parsed_where = []
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
    }

    def __init__(self):
        pass

    def from_request(self, request):
        # sqlparse can parse subsets of a complete query, so there is no need to 
        # build a complete query
        where_value = request.GET.get(self.where_param_name, "").strip()
        if where_value != "":
            self.parsed_where = make_token_keyword_filter()(sqlparse.parse(where_value)[0].tokens)

        sort_value = request.GET.get(self.sort_param_name, "").strip()
        if sort_value != "":
            self.parsed_sort = make_token_keyword_filter()(sqlparse.parse(sort_value)[0].tokens)

    def get_filterable_fields(self, model):
        return dict([(f.name, f) for f in model._meta.fields if f.__class__ in self.value_casts])

    def _value_cast(self, field, value):
        try:
            cast_callable = self.value_casts[type(field)]
        except KeyError:
            return value
        return cast_callable(value, field)

    def _to_filter(self, token, fields):
        if type(token) in (tuple, list):
            f = []
            end = len(token) - 1
            i = 0
            while i <= end:
                if token[i].ttype == T.Keyword:
                    keyword = token[i].value.lower()
                    if keyword == "and":
                        f.append(self._to_filter(token[i+1], fields))
                        i += 1
                    elif keyword == "not":
                        f.append(~self._to_filter(token[i+1], fields))
                        i += 1
                    elif keyword == "or":
                        if len(f) == 0:
                            raise BadQuery("Can not start query with \"{0}\"".format(token[i].value))
                        f[len(f)-1] = f[len(f)-1] | self._to_filter(token[i+1], fields)
                        i += 1
                else:
                    f.append(self._to_filter(token[i], fields))
                i += 1
            return f
        else:
            if isinstance(token, sql.Comparison):
                subtokens = make_token_keyword_filter()(token.tokens)
                c_fields = []
                c_op = None
                c_values = []
                for st in subtokens:
                    if st.ttype == T.Literal.String.Single:
                        c_values.append(st.value.strip("'"))
                    elif st.ttype in T.Literal.Number:
                        c_values.append(st.value)
                    elif st.ttype == T.Operator.Comparison:
                        # implements part of the field lookups documented under
                        # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#field-lookups
                        if st.value == "=":
                            c_op = "exact"
                        elif st.value == ">":
                            c_op = "gt"
                        elif st.value == ">=":
                            c_op = "gte"
                        elif st.value == "<":
                            c_op = "lt"
                        elif st.value == "<=":
                            c_op = "lte"
                        else:
                            raise BadQuery("Unsupported operator: \"{0}\"".format(st.value))
                    elif st.ttype == T.Operator.Comment:
                        pass
                    elif isinstance(st, sql.Identifier):
                        if st.value in fields:
                            c_fields.append(st.value)
                        else:
                            raise BadQuery("Unknown identifier \"{0}\"".format(st.value))
                    else:
                        raise BadQuery("Comparisons do not allow the subexpression \"{0}\"".format(st.value))

                if len(c_values) > 1 or len(c_fields) < 1:
                    raise BadQuery("Can not just compare values in \"{0}\"".format(token.value))

                query_key = "{0}__{1}".format(c_fields[0], c_op)
                query_value = F(c_fields[1]) if len(c_fields) >= 2 else self._value_cast(fields[c_fields[0]], c_values[0])
                return Q(**{query_key:query_value})

            elif isinstance(token, sql.Parenthesis):
                raise BadQuery("Nesting with parenthesises is not supported: {0}".format(token.value))
            else:
                raise BadQuery("Unsupported part of query: {0}".format(token.value))

    def build_filter(self, model):
        fields = self.get_filterable_fields(model)
        #dump(self.parsed_where)
        return self._to_filter(self.parsed_where, fields)

    def filter_queryset(self, request, queryset, view):
        self.from_request(request)
        f = self.build_filter(queryset.model)

        if type(f) == list:
            return queryset.filter(*f)
        return queryset.filter(f)

