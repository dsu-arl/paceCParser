# pace-c-parser
Submodule to help verify C programs


## Example Use
C file to verify
```C
// example.c
#include <stdio.h>

int sum(int a, int b) {
    int sum = a + b;
    return sum;
}

int main() {
    int x = 10;

    if (x >= 10) {
        int test = 23;
        printf("This statement is true\n");
    }

    return 0;
}
```

Python verification script
```python
# verify.py
from paceCParser.data_classes import Variable
from paceCParser.parser import parse_file, retrieve_function_body


filename = 'example.c'
file_contents = parse_file(filename)

main_function = {
    'function_name': 'main',
    'return_type': 'int',
    'parameters': []
}
main_function_body = retrieve_function_body(file_contents, **main_function)
print('Main function:')
for line in main_function_body:
    print('\t', line)

sum_function = {
    'function_name': 'sum',
    'return_type': 'int',
    'parameters': [
        Variable(data_type='int', name='a', value=None),
        Variable(data_type='int', name='b', value=None)
    ]
}
sum_function_body = retrieve_function_body(file_contents, **sum_function)
print('Sum function:')
for line in sum_function_body:
    print('\t', line)
```

Output:
```commandline
Main function:
    Variable(data_type='int', name='x', value=10)
    If(condition='x >= 10', body=[Variable(data_type='int', name='test', value=23), 'printf("This statement is true\\n");'])
    return 0;
Sum function:
    Variable(data_type='int', name='sum', value='a + b')
    return sum;
```