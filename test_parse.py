from .parser import _parse_variable, _parse_conditional, _split_c_code, _parse_c_statements, _parse_function
import pytest
from .test_cases import *


@pytest.mark.parametrize(
    'case',
    variables_test_cases,
    ids=[case.id for case in variables_test_cases]
)
def test_variable_parse(case):
    assert _parse_variable(case.statement) == case.expected


@pytest.mark.parametrize(
    'case',
    conditionals_test_cases,
    ids=[case.id for case in conditionals_test_cases]
)
def test_condition_parse(case):
    assert _parse_conditional(case.statement) == case.expected


@pytest.mark.parametrize(
    'case',
    function_test_cases,
    ids=[case.id for case in function_test_cases]
)
def test_function_parse(case):
    assert _parse_function(case.statement) == case.expected