from types import MappingProxyType
from typing import Dict
from parsimonious import Grammar, NodeVisitor
from parsimonious.nodes import RegexNode
from parsimonious.exceptions import IncompleteParseError
from itertools import chain
from pyspectrum.attributes import attr_name_to_id


__all__ = ["parse_filter"]


_OPERATORS = MappingProxyType(
    {
        "=": "equals-ignore-case",  # equals exactly
        "!=": "does-not-equal",  # does not equal
        "~": "has-substring-ignore-case",  # string contains
        "!~": "does-not-have-substring-ignore-case",  # string does not contain
        "=~": "has-pcre-ignore-case",  # match regular expression
        "^=": "has-prefix-ignore-case",
        "=$": "has-suffix-ignore-case",
        "<": "less-than",  # less than
        "<=": "less-than-or-equals",  # less than or equal to
        ">": "greater-than",  # greater than
        ">=": "greater-than-or-equals",  # greather than or equal to
    }
)

FILTER_GRAMMER = r"""
#
# Expression parts
#
filter_expr         = group_expr / simple_expr
group_expr          = group_tok ws "(" ws group_list_expr ws ")"
group_list_item     = group_expr / simple_expr
group_list_expr     = group_list_item ws ("," ws group_list_item)+
#
#
simple_expr         = attr ws oper ws value_tok
#
# Token parts
#
attr            = ~"[a-z0-9_\-]+"i
sq_words        = ~"[^']+"
dq_words        = ~"[^\"]+"
ws              = ~"\s*"
sq              = "'"
dq              = "\""
word            = ~r"[\\a-z0-9\.\/_\-]+"i
group_tok       = 'and' / 'or' / 'not'
oper            = '!=' / '=~' / '=$' / '=' / '!~' / '~' / '^=' / '<=' / '>=' / '<' / '>'
value_tok       = sq_tok / dq_tok / word
sq_tok          = sq sq_words sq
dq_tok          = dq dq_words dq
"""

_grammer = Grammar(FILTER_GRAMMER)


class _FilterConstructor(NodeVisitor):
    """ parsimouneous node visitor for handling the FILTER_GRAMMER """

    def visit_group_expr(self, node, vc):  # noqa
        """ create a group_expr item """
        group_tok, _, _, _, filter_list, *_ = vc
        return {group_tok: filter_list}

    def visit_group_list_expr(self, node, vc):  # noqa
        """ create a list of group_expr items """
        expr_1, _, expr_n = vc
        expr_list = [
            expr_1,
            *(
                expr
                for expr in chain.from_iterable(expr_n)
                if isinstance(expr, dict)
            ),
        ]
        return expr_list

    def visit_group_list_item(self, node, vc):  # noqa
        return vc[0]

    def visit_simple_expr(self, node, vc):  # noqa
        """ return a filter dictionary """
        attr, _, oper, _, value_tok, *_ = vc
        attr_id = attr_name_to_id(attr.text)
        return {oper: (hex(attr_id), value_tok)}

    # -------------------------------------------------------------------------
    #                      Token Expressions
    # -------------------------------------------------------------------------

    def visit_group_tok(self, node, vc):  # noqa
        """ returns the group operator (and, or, not) value """
        return node.text

    def visit_value_tok(self, node, vc):  # noqa
        """ children will either be a single node-value or a quoted-value """
        vc = vc.pop(0)

        # Single node-value
        if isinstance(vc, RegexNode):
            return vc.text

        # Remove the single or double quotes from a Quoted value
        return node.text[1:-1]

    # -------------------------------------------------------------------------
    #                      Operator Nodes
    # -------------------------------------------------------------------------

    def visit_oper(self, node, vc):  # noqa
        """ returns the string operator in IPF API form """
        return _OPERATORS[node.text]

    def generic_visit(self, node, visited_children):
        """ pass through for nodes not explicility visited """
        return visited_children or node


_filter_builder = _FilterConstructor()


def parse_filter(expr: str) -> dict:
    """
    This function is used to convert a filter expression, as a string in the
    form of FILTER_GRAMMER, and return a Spectrum compatible XML string which
    will be inserted into the payload of a POST request.

    Parameters
    ----------
    expr
        The filter expression, for example "model_name ~ FW"
    """

    # Parse the expression against the defined Grammer
    res = _grammer.parse(expr.strip().replace("\n", ""))

    # Return the parsed expression as a filter dictionary
    return _filter_builder.visit(res)[0]
