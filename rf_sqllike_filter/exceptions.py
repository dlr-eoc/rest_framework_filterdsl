# encoding: utf8

from rest_framework import exceptions

class BadQuery(exceptions.ParseError):
    pass

class BadValue(exceptions.ParseError):
    pass
