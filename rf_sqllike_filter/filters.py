# encoding: utf8

from rest_framework import filters
import sqlparse
from sqlparse.sql import Where
from sqlparse import tokens as T


def make_token_keyword_filter(excluded_keywords=[]):
    def do_filter(tokens):
        def do_keep(token):
            return token.ttype not in (T.Whitespace, T.Punctuation, T.Newline) \
                    and not (token.ttype == T.Keyword and t.value.lower() in excluded_keywords)
        return [t for t in tokens if do_keep(t)]
    return do_filter

class SQLLikeFilterBackend(filters.BaseFilterBackend):
    where_param_name = 'filter'
    sort_param_name = 'sort'

    parsed_where = []
    parsed_sort = []

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

    def to_queryset(self):
        pass

    def filter_queryset(self, request, queryset, view):
        self.from_request(request)
        print self.parsed_where
        print self.parsed_sort
        return queryset

