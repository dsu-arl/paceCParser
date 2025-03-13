from dataclasses import dataclass
from typing import List, Union


@dataclass
class Variable:
    data_type: str
    name: str
    value: Union[str, int, 'FunctionDeclaration'] # using '' for forward reference

@dataclass
class If:
    condition: str
    body: str

@dataclass
class ElseIf:
    condition: str
    body: str

@dataclass
class Else:
    body: str

@dataclass
class FunctionDeclaration:
    return_type: str
    function_name: str
    parameters: List['Variable'] # using '' for forward reference

@dataclass
class FunctionDefinition(FunctionDeclaration):
    body: List[Union[Variable, If, ElseIf, Else, str]]


# Export all dataclasses
__all__ = ['Variable', 'If', 'ElseIf', 'Else', 'FunctionDeclaration', 'FunctionDefinition']