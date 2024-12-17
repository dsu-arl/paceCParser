from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import List, Union


@dataclass
class Variable:
    data_type: str
    name: str
    value: Union[str, 'Function'] # using '' for forward reference


@dataclass
class Function:
    return_type: str
    function_name: str
    parameters: List['Variable'] # using '' for forward reference


# define function call as Variable = Function
# for example: int total = sum(5, 10);
# Variable(data_type='int', name='total', value=Function(return_type='int', ))

######################### GET FILE CONTENTS #########################
def get_file_contents(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f'Error: File {filename} not found')
        return None


######################### COMPILE PROGRAM #########################
def compile_program(c_file, output_file='a.out'):
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


######################### RUN PROGRAM #########################
def run_program(c_file, output_file='a.out'):
    if not compile_program(c_file, output_file):
        print('Program failed to compile')
        return None

    run_process = subprocess.run(
        [f'./{output_file}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if run_process.returncode != 0:
        print('Runtime error:')
        print(run_process.stderr.decode())
        return None
    
    return run_process.stdout.decode()


######################### EXTRACT LINES #########################
def extract_lines(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        lines = []
    
    lines = [line.replace('\n', '') for line in lines]
    
    imports = []
    for line in lines:
        if '#include' in imports:
            imports.append(line)


######################### EXTRACT FUNCTION PARAMETERS #########################
def extract_function_parameters(parameters):
    if parameters == '':
        return []

    parameters = parameters.split(',')
    parameters = [param.strip() for param in parameters]
    clean_params = []
    for param in parameters:
        data_type, param_name = param.split(' ')
        if param_name[0] == '*':
            data_type += '*'
            param_name = param_name[1:]
        parameter = Variable(data_type=data_type, name=param_name, value=None)
        clean_params.append(parameter)
    
    return clean_params


######################### FORMAT FUNCTION DECLARATION #########################
def format_func_declar(func_str):
    pattern = r"^(\S+(?:\s+\S+)*)\s+(\w+)\s*\(([^)]*)\)$"
    match = re.match(pattern, func_str)
    
    if not match:
        print('Function declaration not found')
        return None
    
    return_type, function_name, parameters = match.groups()
    
    # Deal with pointer return types for functions as well (int* sum() vs int *sum())
    if function_name[0] == '*':
        return_type += '*'
        function_name = function_name[1:]

    # Extract function parameters
    clean_parameters = extract_function_parameters(parameters)
    function = Function(return_type, function_name, clean_parameters)
    return function


######################### FIND FUNCTIONS #########################
def find_functions(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f'Error: File {filename} not found')
        return None

    function_regex = re.compile(
        r"""
        ^\s*                          # Start of the line, optional leading whitespace
        ([a-zA-Z_][\w\s\*]+)\s+       # Return type (e.g., int, void, char*)
        ([a-zA-Z_]\w*)\s*             # Function name (C identifier)
        \(\s*                         # Opening parenthesis for parameters
        ([^)]*)\s*                    # Parameter list (non-greedy match)
        \)\s*                         # Closing parenthesis
        (?:;|{)                       # End with a semicolon (prototype) or opening brace (definition)
        """,
        re.VERBOSE | re.MULTILINE
    )

    # Find all function declarations
    matches = function_regex.findall(content)
    print('Matches:', matches)

    functions = []
    for match in matches:
        return_type, function_name, parameters = match
        function_str = f'{return_type} {function_name}({parameters})'
        clean_func_declar = format_func_declar(function_str)
        functions.append(clean_func_declar)

    return functions


######################### GET FUNCTION CONTENTS #########################
def get_function_contents(content, function):
    # Extract details from the dictionary
    return_type = function.return_type
    func_name = function.function_name
    params = function.parameters

    # Build the parameter string
    param_str = ', '.join(f"{param.data_type} {param.name}" for param in params)
    
    # Construct the function signature regex dynamically
    func_pattern = re.compile(rf'^\s*{return_type}\s+{func_name}\s*\({param_str}\)\s*\{{')

    found_function = False
    inside_function = False
    brace_count = 0
    function_body = []
    
    for line in content.splitlines():
        # If we've found the start of the function, start tracking braces
        if not inside_function:
            match = func_pattern.match(line)
            if match:
                found_function = True
                inside_function = True
                brace_count = 1  # We've found the opening brace
                function_body.append(line.strip())
                continue
        
        # If we are inside the function, track braces
        if inside_function:
            for char in line:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
            function_body.append(line.strip())
            
            # Once we reach the closing brace, end the function capture
            if brace_count == 0:
                inside_function = False
                break

    if not found_function:
        return None

    return list(filter(None, function_body[1:-1]))


######################### EXTRACT FUNCTION VARIABLES #########################
def extract_function_variables(function_contents):
    pattern = r'^\s*(int|float|char|double|long|short|unsigned|signed|void)\s+([\w*]+)(\s*=\s*([^;]+))?\s*;'
    # pattern = r'^\s*(int|float|char|double|long|short|unsigned|signed|void)\s+([\w*]+)(\s*=\s*(.*))?\s*\(.*\)\s*;'

    variables = []
    for line in function_contents:
        match = re.match(pattern, line)
        if match:
            print('Match:', match)
            data_type = match.group(1)
            var_name = match.group(2)
            if match.group(3):
                # Value will be in the format ' = 10' so this removes the = and spaces
                var_value = match.group(3).split('=')[-1].strip()
                # check if var_value is a function call
                func_pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*'
                match = re.match(func_pattern, var_value)
                if match:
                    print(match.group(1))
                    print(match.group(2))
            else:
                var_value = None
            print(Variable(data_type=data_type, name=var_name, value=var_value))
            variables.append(Variable(data_type=data_type, name=var_name, value=var_value))

    return variables


######################### VERIFY INITIAL CHECKS #########################
def verify_initial_checks(filename):
    # Check file extension
    path = Path(filename)
    if path.suffix.lower() != '.c':
        print('Provided file is not C file')
        return False

    # Attempt to compile program before looking through C file
    # If it doesn't compile then don't open C file since something isn't working
    if not compile_program(filename):
        return False

    # Retrieve contents of C file
    contents = get_file_contents(filename)

    # Has 'return 0;' as the last line in main()
    # Compilation will fail if main function doesn't exist
    main_function = format_func_declar('int main()')
    function_contents = get_function_contents(contents, main_function)
    if function_contents is not None:
        # Check if 'return 0;' is last line in main()
        if 'return 0;' != function_contents[-1]:
            print("Missing 'return 0;' statement at end of main()")
            return False

    return True
