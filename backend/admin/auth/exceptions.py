"""
Module contain exceptions for flask jwt authentication package
"""


# JWTAuthenticationRules Exceptions
class InvalidDefaultKeyType(Exception):
    pass


class JWTRulesEmpty(Exception):
    pass


class DefaultRuleDoesNotExist(Exception):
    pass


class InvalidJWTRule(Exception):
    pass


class JWTFieldValueError(Exception):
    pass
