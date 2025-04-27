import logging
logging.basicConfig(level=logging.INFO)

USE_LEXICAL_SCOPING = False

op_stack = []
dict_stack = [{}]


class ParseFailed(Exception): pass
class TypeMismatch(Exception): pass


def process_boolean(token):
    if token == "true":
        return True
    elif token == "false":
        return False
    raise ParseFailed()

def process_number(token):
    try:
        num = float(token)
        return int(num) if num.is_integer() else num
    except ValueError:
        raise ParseFailed()

def process_code_block(token):
    if token.startswith("{") and token.endswith("}"):
        return token[1:-1].split()
    raise ParseFailed()

def process_name_constant(token):
    if token.startswith("/"):
        return token
    raise ParseFailed()

PARSERS = [process_boolean, process_number, process_code_block, process_name_constant]

def process_constants(token):
    for parser in PARSERS:
        try:
            result = parser(token)
            op_stack.append(result)
            return
        except ParseFailed:
            continue
    raise ParseFailed(f"Unknown constant: {token}")

# Processing input
def process_input(token):
    try:
        process_constants(token)
        return
    except ParseFailed:
        pass

    if token in BUILTIN_OPS:
        BUILTIN_OPS[token]()
        return

    try:
        lookup_in_dictionary(token)
    except ParseFailed as e:
        logging.error(f"Unknown token: {token} — {e}")


def lookup_in_dictionary(name):
    if USE_LEXICAL_SCOPING:
        if name.startswith("/"):
            name = name[1:]
        for d in reversed(dict_stack):
            if name in d:
                val = d[name]
                if callable(val):
                    val()
                elif isinstance(val, list):
                    for token in val:
                        process_input(token)
                else:
                    op_stack.append(val)
                return
        raise ParseFailed(f"Name '{name}' not found in dictionaries")
        return dynamic_lookup(name)
    else:
        return dynamic_lookup(name)


def dynamic_lookup(name):
    for d in reversed(dict_stack):
        if name in d:
            val = d[name]
            if callable(val):
                val()
            elif isinstance(val, list):
                for token in val:
                    process_input(token)
            else:
                op_stack.append(val)
            return
    raise ParseFailed(f"Name '{name}' not found")


def op_exch():
    if len(op_stack) < 2: raise TypeMismatch()
    a, b = op_stack.pop(), op_stack.pop()
    op_stack.append(a)
    op_stack.append(b)

def op_pop():
    if not op_stack: raise TypeMismatch()
    op_stack.pop()

def op_copy():
    if not op_stack: raise TypeMismatch()
    n = op_stack.pop()
    if not isinstance(n, int) or n < 0 or len(op_stack) < n:
        raise TypeMismatch("error")
    op_stack.extend(op_stack[-n:])

def op_dup():
    if not op_stack: raise TypeMismatch()
    op_stack.append(op_stack[-1])

def op_clear():
    op_stack.clear()

def op_count():
    op_stack.append(len(op_stack))



# THis is jsut a helper function to help with the operations to minimize code
def helper(fn):
    if len(op_stack) < 2: 
        raise TypeMismatch() 
    b, a = op_stack.pop(), op_stack.pop()
    op_stack.append(fn(a, b))

def op_add(): 
    helper(lambda x, y: x + y)
def op_sub(): 
    helper(lambda x, y: x - y)
def op_mul(): 
    helper(lambda x, y: x * y)
def op_div(): 
    helper(lambda x, y: x / y if y != 0 else float('inf'))
def op_mod(): 
    helper(lambda x, y: x % y)

def op_eq(): 
    helper(lambda x, y: x == y)
def op_ne(): 
    helper(lambda x, y: x != y)
def op_gt(): 
    helper(lambda x, y: x > y)
def op_lt(): 
    helper(lambda x, y: x < y)

def op_and(): 
    helper(lambda x, y: x and y)
def op_or(): 
    helper(lambda x, y: x or y)
def op_not():
    if not op_stack: 
        raise TypeMismatch()
    op_stack.append(not op_stack.pop())


def op_dict():
    if not op_stack: raise TypeMismatch()
    op_stack.pop()  
    op_stack.append({})

def op_def():
    if len(op_stack) < 2:
        raise TypeMismatch("Not enough elements for def operation")
    val, name = op_stack.pop(), op_stack.pop()
    if not isinstance(name, str) or not name.startswith("/"):
        raise TypeMismatch("Name must start with '/'")
    
    if isinstance(val, list):
        dict_stack[-1][name[1:]] = {
            'code': val,
            'static_link': dict_stack[-1]
        }
    else:
        dict_stack[-1][name[1:]] = val




def op_begin():
    if not op_stack or not isinstance(op_stack[-1], dict):
        raise TypeMismatch()
    new_dict = op_stack.pop()
    new_dict['__parent__'] = dict_stack[-1]   
    dict_stack.append(new_dict)


def op_end():
    if len(dict_stack) <= 1:
        raise TypeMismatch("Cannot pop global dictionary")
    dict_stack.pop()

def op_length():
    if not op_stack: raise TypeMismatch()
    obj = op_stack.pop()
    if not isinstance(obj, (str, list, dict)):
        raise TypeMismatch("Object must be string/list/dict")
    op_stack.append(len(obj))


def op_get():
    if len(op_stack) < 2: raise TypeMismatch()
    index, obj = op_stack.pop(), op_stack.pop()
    if isinstance(obj, (str, list)) and isinstance(index, int):
        op_stack.append(obj[index])
    else:
        raise TypeMismatch()

def op_getinterval():
    if len(op_stack) < 3: raise TypeMismatch()
    count, start, obj = op_stack.pop(), op_stack.pop(), op_stack.pop()
    if isinstance(obj, (str, list)):
        op_stack.append(obj[start:start+count])
    else:
        raise TypeMismatch()

def op_putinterval():
    if len(op_stack) < 3: raise TypeMismatch()
    insert, start, base = op_stack.pop(), op_stack.pop(), op_stack.pop()
    if isinstance(base, str) and isinstance(insert, str):
        base = base[:start] + insert + base[start+len(insert):]
        op_stack.append(base)
    else:
        raise TypeMismatch()


#control flow
def op_if():
    if len(op_stack) < 2: raise TypeMismatch()
    code, cond = op_stack.pop(), op_stack.pop()
    if cond and isinstance(code, list):
        for token in code:
            process_input(token)

def op_ifelse():
    if len(op_stack) < 3: raise TypeMismatch()
    else_blk, then_blk, cond = op_stack.pop(), op_stack.pop(), op_stack.pop()
    code = then_blk if cond else else_blk
    if isinstance(code, list):
        for token in code:
            process_input(token)

def op_repeat():
    if len(op_stack) < 2: raise TypeMismatch()
    code, count = op_stack.pop(), op_stack.pop()
    if isinstance(code, list) and isinstance(count, int):
        for _ in range(count):
            for token in code:
                process_input(token)
    else:
        raise TypeMismatch()

def op_for():
    if len(op_stack) < 4: raise TypeMismatch()
    code, end, step, start = op_stack.pop(), op_stack.pop(), op_stack.pop(), op_stack.pop()
    if isinstance(code, list):
        i = start
        while (step > 0 and i <= end) or (step < 0 and i >= end):
            op_stack.append(i)
            for token in code:
                process_input(token)
            i += step

def lookup_in_dictionary(name):
    if name.startswith("/"):
        name = name[1:]

    if USE_LEXICAL_SCOPING:
        return lexical_lookup(name)
    else:
        return dynamic_lookup(name)

def lexical_lookup(name):
    current_dict = dict_stack[-1]
    while current_dict:
        if name in current_dict:
            val = current_dict[name]
            if isinstance(val, dict) and 'code' in val and 'static_link' in val:
                execute_lexical_code(val)
            else:
                op_stack.append(val)
            return
        current_dict = current_dict.get('__parent__', None)
    raise ParseFailed(f"Lexical lookup failed for {name}")



def execute_lexical_code(val):
    old_stack = dict_stack.copy()
    dict_stack.append(val['static_link'])
    for token in val['code']:
        process_input(token)
    dict_stack.clear()
    dict_stack.extend(old_stack)


# --------------- Misc ---------------
def op_print():
    print(op_stack.pop())

def op_quit():
    exit()

def toggle():
    global USE_LEXICAL_SCOPING
    USE_LEXICAL_SCOPING = not USE_LEXICAL_SCOPING
    mode = "Lexical (Static)" if USE_LEXICAL_SCOPING else "Dynamic"
    print(f"Switched to {mode} scoping.")


BUILTIN_OPS = {
    # stack operatio s
    "exch": op_exch, "pop": op_pop, "copy": op_copy, "dup": op_dup, "clear": op_clear, "count": op_count,
    # Arithmetic ops
    "add": op_add, "sub": op_sub, "mul": op_mul, "div": op_div, "mod": op_mod,
    # Boolean oeprations
    "eq": op_eq, "ne": op_ne, "gt": op_gt, "lt": op_lt, "and": op_and, "or": op_or, "not": op_not,
    # Dict operation
    "def": op_def, "dict": op_dict, "begin": op_begin, "end": op_end, "length": op_length,
    # String/List operations
    "get": op_get, "getinterval": op_getinterval, "putinterval": op_putinterval,
    # Flow operation
    "if": op_if, "ifelse": op_ifelse, "repeat": op_repeat, "for": op_for,
    "print": op_print, "=": op_print, "quit": op_quit,

    "toggle": toggle,

}

def repl():
    while True:
        try:
            line = input("REPL> ").strip()
            if not line:
                continue
            tokens = line.split()
            for token in tokens:
                process_input(token)
            if op_stack:
                print(f"[stack]: {op_stack}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("PostScript Interpreter REPL\nType 'quit' to exit.")
    try:
        repl()
    except KeyboardInterrupt:
        print("\nExiting REPL.")