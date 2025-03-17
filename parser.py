from pathlib import Path
import re
import subprocess

# Allow it to be used with unit tests
try:
    from .data_classes import *
except ImportError:
    from data_classes import *


__all__ = ['compile_program', 'run_program', 'verify_initial_checks', 'parse_file']

RED_TEXT_CODE = '\033[31m'
GREEN_TEXT_CODE = '\033[32m'
RESET_TEXT_CODE = '\033[0m'


# --------------------- Public API ---------------------

def compile_program(c_file, output_file='a.out'):
    '''Compiles a given C program.

    Args:
        c_file (str): Path to the C source file.
        output_file (str): Name of the compiled executable (default: 'a.out').
    
    Returns:
        bool: Status of compilation, True if compiled successfully, False if not.
    '''
    compile_process = subprocess.run(
        ['gcc', c_file, '-o', output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if compile_process.returncode != 0:
        print('Program failed to compile')
        print(compile_process.stderr.decode())
        return False

    return True


def run_program(executable_file='a.out'):
    '''Executes a given executable.

    Args:
        executable_file (str): Name of the executable to be run (default: 'a.out').
    
    Returns:
        Optional[str]: Program output as a string, or None if run fails.
    '''
    run_process = subprocess.run(
        [f'./{executable_file}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if run_process.returncode != 0:
        print('Runtime error:')
        print(run_process.stderr.decode())
        return None
    
    return run_process.stdout.decode()


def verify_initial_checks(filename):
    '''Verify initial requirements before performing challenge specific checks.

    Args:
        filename (str): Path to the C file.
    
    Returns:
        bool: True if all checks pass, False otherwise.
    '''
    # Check file extension
    path = Path(filename)
    if path.suffix.lower() != '.c':
        print('Provided file is not C file')
        return False

    # Attempt to compile program before looking through C file
    # If it doesn't compile then don't open C file since something isn't working
    if not compile_program(filename):
        return False

    return True


def parse_file(filename):
    '''Parse a C file into a list of formatted functions to be used with challenge verification.

    Args:
        filename (str): Path to the C file.
    
    Returns:
        Optional[List]: List of parsed functions and headers, or None if failed to open file.
    '''
    try:
        with open(filename, 'r') as file:
            file_contents = file.read()
    except FileNotFoundError:
        print(f'Error: File {filename} not found')
        return None

    formatted_lines = _get_headers(file_contents)
    for header in formatted_lines:
        file_contents = file_contents.replace(header, '')

    split_lines = _split_c_code(file_contents)
    for line in split_lines:
        formatted_lines.append(_parse_function(line))

    return formatted_lines


# --------------------- Private Helpers ---------------------

def _split_c_code(code):
    '''Splits a string of C code into a list of C statements.

    Args:
        code (str): C code to be split into statements.
    
    Returns:
        List: List of C statements.
    '''
    statements = []
    current_statement = ''
    brace_count = 0

    for i in range(len(code)):
        char = code[i]
        current_statement += char

        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        
        # Check if end of if statement or else statement
        if (char == '}' and brace_count == 0) or (char == ';' and brace_count == 0):
            statements.append(current_statement.strip())
            current_statement = ''

    return statements


def _parse_variable(statement):
    '''Identifies if the given statement is a variable declaration and parses it if so.

    Args:
        statement (str): C code statement
    
    Returns:
        Optional[Variable]: If a match is found, returns Variable. Otherwise, returns None.
    '''
    pattern = r'^\s*(int|float|char|double|long|short|unsigned|signed|void)?\s*([\w*]+)(\s*=\s*([^;]+))?\s*;'
    match = re.match(pattern, statement)
    if not match:
        return None

    data_type = match.group(1)
    var_name = match.group(2)
    if match.group(3):
        # Value will be in the format ' = 10' so this removes the = and spaces
        var_value = match.group(3).split('=')[-1].strip()
        try:
            var_value = int(var_value)
        except ValueError:
            pass
    else:
        var_value = None
    return Variable(data_type=data_type, name=var_name, value=var_value)


def _extract_condition_body(conditional_type, statement):
    '''Extracts the code body from the given conditional and parses it into a list of C statements.

    Args:
        conditional_type (str): Type of conditional (if, else if, else)
        statement (str): C code statement
    
    Returns:
        List: List of parsed C statements.
    '''
    if conditional_type in ('if', 'else if'):
        # iterate through string until closing brace 
        # find first ( and then iterate until first ( is closed
        start = statement.find('(')
        if start == -1:
            return -1
    
        count = 1
        for i in range(start + 1, len(statement)):
            if statement[i] == '(':
                count += 1
            elif statement[i] == ')':
                count -= 1
                if count == 0:
                    start_index = i
                    break
    else:
        # get index after 'else' keyword and get everything after that
        start_index = statement.find('else') + len('else')
    
    # grab everything after starting_idx
    start_index += 1
    condition_body = statement[start_index:].strip()

    # Remove starting { and ending }
    if condition_body[0] == '{' and condition_body[-1] == '}':
        condition_body = condition_body[1:-1].strip()

    split_condition_body = _split_c_code(condition_body)
    parsed_condition_body = _parse_c_statements(split_condition_body)

    return parsed_condition_body


def _parse_conditional(statement):
    '''Identifies if the given statement is a variable declaration and parses it if so.

    Args:
        statement (str): C code statement
    
    Returns:
        Optional[Variable]: If a match is found, returns Variable. Otherwise, returns None.
    '''
    conditional_regex = re.compile(
        # r"\b(if|else\s+if|else)\s*(?:\(([^)]*)\))?\s*\{([^}]*)\}",
        r"\b(if|else\s+if|else)\s*(?:\(([^)]*)\))?\s*(?:\{([^}]*)\}|([^;{]*);)",
        re.DOTALL
    )

    match = conditional_regex.search(statement)
    if not match:
        # Throws an error if you try to return either a tuple or None
        return None

    conditional_type = match[1]
    condition = match[2] if match[2] else None

    parsed_body = _extract_condition_body(conditional_type, statement.strip())

    if conditional_type == 'if':
        return If(condition, body=parsed_body)
    if conditional_type == 'else if':
        return ElseIf(condition, body=parsed_body)
    if conditional_type == 'else':
        return Else(body=parsed_body)


def _parse_c_statements(c_statements):
    '''Parses a list of C statements into their appropriate data types.

    Args:
        c_statements (List[str]): List of C statement strings to be parsed.
    
    Returns:
        List: List of parsed C statements.
    '''
    parsed_statements = []

    for statement in c_statements:
        # Check if statement is a variable
        variable = _parse_variable(statement)
        # if variable, then value will not be None
        if variable:
            parsed_statements.append(variable)
            continue

        # Check if statement is a condition
        conditional = _parse_conditional(statement)
        if conditional:
            # body_statements = _split_c_code(body)
            # body_statements = _parse_c_statements(body_statements)
            # conditional.body = body_statements
            parsed_statements.append(conditional)
            continue

        # If not variable or conditional, then function call (treat just as string for now)
        parsed_statements.append(statement)

    return parsed_statements


def _get_headers(file_contents):
    '''Retrieves all headers from file contents and returns them as a list of strings.

    Args:
        file_contents (str): C file contents.
    
    Returns:
        List[str]: List of headers in C file.
    '''
    pattern = r'#include [<"]([^>"]+)[>"]'
    matches = re.finditer(pattern, file_contents)
    headers = []
    for match in matches:
        headers.append(match.group(0))
    return headers


def _extract_function_body(code):
    '''Identifies and parses any code contained in the body of a conditional, loop, function, etc.

    Args:
        code (str): C code as a string to retrieve body from.
    
    Returns:
        List: List of C statements from the body.
    '''
    body_start = code.index('{') + 1
    brace_count = 1
    i = body_start

    while i < len(code) and brace_count > 0:
        if code[i] == '{':
            brace_count += 1
        elif code[i] == '}':
            brace_count -= 1
        i += 1
    
    function_body = code[body_start:i-1].strip()
    function_statements = _split_c_code(function_body)
    formatted_function_body = _parse_c_statements(function_statements)

    return formatted_function_body


def _extract_function_parameters(parameters):
    '''Retrieves and parses a list of parameters from a function.

    Args:
        parameters (str): Function parameters represented as a string.
    
    Returns:
        List[Variable]: List of function parameters parsed into Variable type
    '''
    parameters = parameters.strip().split(',')
    parameters = [param for param in parameters if param] # removes all empty strings
    for i in range(len(parameters)):
        data_type, var_name = parameters[i].strip().split(' ')
        if var_name[0] == '*':
            data_type += '*'
            var_name = var_name[1:]

        parameters[i] = Variable(data_type=data_type, name=var_name, value=None)
    return parameters


def _parse_function(code):
    '''Parses a function into the appropriate function data type (Function or FunctionDefinition).

    Args:
        code (str): C function code to be parsed.
    
    Returns:
        FunctionDefinition: If the code is a function definition (contains '{...}').

        Function: If the code is a function declaration (ends with ';').
        
        None: If the code does not match a valid function pattern.
    '''
    code = code.strip()
    if '{' in code or '}' in code:
        # function definition
        pattern = r'^\s*([a-zA-Z_][\w\s\*]+)\s+([a-zA-Z_]\w*)\s*\(([^)]*?)\)\s*\{([\s\S]*?)\}\s*$' # can be used with newlines and tabs present
        match = re.match(pattern, code)
        if not match:
            return None

        # Store return type and function name into variables
        return_type = match.group(1)
        function_name = match.group(2)

        # Split function parameters into Variable types
        parameters = _extract_function_parameters(match.group(3))

        # Extract function body, split into list of C statements, and parse into appropriate type
        function_body = _extract_function_body(code)

        return FunctionDefinition(return_type=return_type, function_name=function_name, parameters=parameters, body=function_body)
        
    elif ';' in code:
        # function declaration
        pattern = r'(\w+)\s+(\w+)\s*\(([^)]*)\)\s*;'
        match = re.match(pattern, code)
        if not match:
            return None

        # Store return type and function name into variables
        return_type = match.group(1)
        function_name = match.group(2)
        
        # Split function parameters into Variable types
        parameters = _extract_function_parameters(match.group(3))

        return FunctionDeclaration(return_type=return_type, function_name=function_name, parameters=parameters)
    
    else:
        print('Unknown function type')
