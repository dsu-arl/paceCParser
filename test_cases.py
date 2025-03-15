from .data_classes import *
from dataclasses import dataclass


@dataclass
class Case:
    id: str
    statement: str
    expected: object


#################### VARIABLE TEST CASES ####################
variables_test_cases = [
    Case(
        id='int declaration and initialization',
        statement='int x = 5;',
        expected=Variable(data_type='int', name='x', value=5)
    ),
    Case(
        id='int declaration',
        statement='int age;',
        expected=Variable(data_type='int', name='age', value=None)
    ),
    Case(
        id='int assignment',
        statement='age = 26;',
        expected=Variable(data_type=None, name='age', value=26)
    ),
    Case(
        id='char declaration and initialization',
        statement="char test = 'c';",
        expected=Variable(data_type='char', name='test', value="'c'")
    ),
    Case(
        id='char declaration',
        statement="char letter;",
        expected=Variable(data_type='char', name='letter', value=None)
    ),
    Case(
        id='char assignment',
        statement="test = 'c';",
        expected=Variable(data_type=None, name='test', value="'c'")
    )
]


#################### CONDITIONAL TEST CASES ####################
conditionals_test_cases = [
    Case(
        id='If statement',
        statement='''
        if (a > b) {
            printf("a is greater than b\n");
        }
        ''',
        expected=If(condition='a > b', body=['printf("a is greater than b\n");'])
    ),
    Case(
        id='Else If statement',
        statement='''
        else if (a == b) {
            printf("a is equal to b\n");
        }
        ''',
        expected=ElseIf(condition='a == b', body=['printf("a is equal to b\n");'])
    ),
    Case(
        id='Else statement',
        statement='''
        else {
            print("a is less than b\n");
        }
        ''',
        expected=Else(body=['print("a is less than b\n");'])
    ),
    Case(
        id='If statement with multiple body statements',
        statement='''
        if (a == 5) {
            int b = 10;
            printf("a is equal to 5\n");
        }
        ''',
        expected=If(
            condition='a == 5',
            body=[
                Variable(data_type='int', name='b', value=10),
                'printf("a is equal to 5\n");'
            ]
        )
    ),
    Case(
        id='If statement with condition of 1 (always true)',
        statement='''
        if (1) {
            printf("This statement will always print\n");
        }
        ''',
        expected=If(
            condition='1',
            body=['printf("This statement will always print\n");']
        )
    ),
    Case(
        id='If statement with no curly braces',
        statement='''
        if (x == y)
            printf("x is equal to y\n");
        ''',
        expected=If(
            condition='x == y',
            body=['printf("x is equal to y\n");']
        )
    ),
    Case(
        id='Else If statement with no curly braces',
        statement='''
        else if (x > y)
            printf("x is greater than y\n");
        ''',
        expected=ElseIf(
            condition='x > y',
            body=['printf("x is greater than y\n");']
        )
    ),
    Case(
        id='Else statement with no curly braces',
        statement='''
        else
            printf("x is less than y\n");
        ''',
        expected=Else(body=['printf("x is less than y\n");'])
    )
]


######################### FOR LOOP TEST CASES #########################


######################### WHILE LOOP TEST CASES #########################


######################### FUNCTION TEST CASES #########################
function_test_cases = [
    Case(
        id='Function declaration',
        statement='int sum(int a, int b);',
        expected=FunctionDeclaration(
            return_type='int',
            function_name='sum',
            parameters=[
                Variable(data_type='int', name='a', value=None),
                Variable(data_type='int', name='b', value=None)
            ]
        )
    ),
    Case(
        id='Function definition',
        statement='''
            int subtract(int x, int y) {
                int diff = x - y;
                return diff;
            }
        ''',
        expected=FunctionDefinition(
            return_type='int',
            function_name='subtract',
            parameters=[
                Variable(data_type='int', name='x', value=None),
                Variable(data_type='int', name='y', value=None)
            ],
            body=[
                Variable(data_type='int', name='diff', value='x - y'),
                'return diff;'
            ]
        )
    ),
    Case(
        id='If-Else inside of function definition',
        statement='''
        void compare(int x, int y) {
            if (x >= y) {
                printf("x is greater than or equal to y\n");
            }
            else {
                printf("x less than y\n");
            }
        }
        ''',
        expected=FunctionDefinition(
            return_type='void',
            function_name='compare',
            parameters=[
                Variable(data_type='int', name='x', value=None),
                Variable(data_type='int', name='y', value=None)
            ],
            body=[
                If(
                    condition='x >= y',
                    body=['printf("x is greater than or equal to y\n");']
                ),
                Else(body=['printf("x less than y\n");'])
            ]
        )
    ),
    Case(
        id='If-ElseIf-Else inside of function definition',
        statement='''
        void compare(int x, int y) {
            if (x == y) {
                if (1 == 1) {
                    printf("This is a true statement\n");
                }
                printf("x is equal to y\n");
            }
            else if (x > y) {
                printf("x is greater than y\n");
            }
            else {
                printf("x is less than y\n");
            }
        }
        ''',
        expected=FunctionDefinition(
            return_type='void',
            function_name='compare',
            parameters=[
                Variable(data_type='int', name='x', value=None),
                Variable(data_type='int', name='y', value=None)
            ],
            body=[
                If(
                    condition='x == y',
                    body=[
                        If(
                            condition='1 == 1',
                            body=['printf("This is a true statement\n");']
                        ),
                        'printf("x is equal to y\n");',
                    ]
                ),
                ElseIf(
                    condition='x > y',
                    body=['printf("x is greater than y\n");']
                ),
                Else(body=['printf("x is less than y\n");'])
            ]
        )
    )
]