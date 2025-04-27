import psip

def reset():
    psip.op_stack.clear()
    psip.dict_stack = [{}]

def test_add():
    reset()
    psip.process_input("1")
    psip.process_input("2")
    psip.process_input("add")
    assert psip.op_stack == [3]

def test_def_and_lookup():
    reset()
    psip.process_input("/x")
    psip.process_input("10")
    psip.process_input("def")
    psip.process_input("x")
    assert psip.op_stack == [10]

def test_exch():
    reset()
    psip.process_input("1")
    psip.process_input("2")
    psip.process_input("exch")
    assert psip.op_stack == [2, 1]

def test_pop():
    reset()
    psip.process_input("1")
    psip.process_input("2")
    psip.process_input("pop")
    assert psip.op_stack == [1]

def test_copy():
    reset()
    psip.process_input("1")
    psip.process_input("2")
    psip.process_input("2")
    psip.process_input("copy")
    assert psip.op_stack == [1, 2, 1, 2]

def test_dup():
    reset()
    psip.process_input("1")
    psip.process_input("dup")
    assert psip.op_stack == [1, 1]

def test_clear():
    reset()
    psip.process_input("1")
    psip.process_input("2")
    psip.process_input("clear")
    assert psip.op_stack == []

def test_count():
    reset()
    psip.process_input("1")
    psip.process_input("2")
    psip.process_input("count")
    assert psip.op_stack == [1, 2, 2]  

def test_length_string():
    reset()
    psip.op_stack.append("Hello")
    psip.process_input("length")
    assert psip.op_stack == [5]

def test_eq():
    reset()
    psip.process_input("5")
    psip.process_input("5")
    psip.process_input("eq")
    assert psip.op_stack == [True]

def test_ne():
    reset()
    psip.process_input("5")
    psip.process_input("3")
    psip.process_input("ne")
    assert psip.op_stack == [True]

def test_if_true():
    reset()
    psip.op_stack.append(True)
    psip.op_stack.append(["1", "2", "add"])
    psip.process_input("if")
    assert psip.op_stack == [3]

def test_ifelse_false():
    reset()
    psip.op_stack.append(False)
    psip.op_stack.append(["999"])  
    psip.op_stack.append(["42"])   
    psip.process_input("ifelse")
    assert psip.op_stack == [42]

def test_repeat():
    reset()
    psip.op_stack.append(3)
    psip.op_stack.append(["1"])
    psip.process_input("repeat")
    assert psip.op_stack == [1, 1, 1]

def test_for():
    reset()
    psip.op_stack.append(1)  
    psip.op_stack.append(1)  
    psip.op_stack.append(3)  
    psip.op_stack.append(["dup"])
    psip.process_input("for")
    assert psip.op_stack == [1, 1, 2, 2, 3, 3]

def test_dict_operations():
    reset()
    psip.process_input("1")
    psip.process_input("dict")
    assert isinstance(psip.op_stack[-1], dict)

def test_begin_end():
    reset()
    psip.process_input("1")
    psip.process_input("dict")
    psip.process_input("begin")
    psip.process_input("/y")
    psip.process_input("100")
    psip.process_input("def")
    psip.process_input("end")
    psip.process_input("y")
    assert psip.op_stack == [100]

def test_print(capsys):
    reset()
    psip.process_input("123")
    psip.process_input("print")
    captured = capsys.readouterr()
    assert captured.out.strip() == "123"
