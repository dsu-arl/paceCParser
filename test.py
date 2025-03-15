from parser import _parse_conditional
from data_classes import If, ElseIf,  Else

statement='''
    else {
        print("a is less than b\n");
    }
'''
expected=Else(body=['print("a is less than b\n");'])

conditional = _parse_conditional(statement)

assert type(conditional) == type(expected)
assert conditional.body == expected.body