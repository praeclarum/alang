from alang import define, struct, tensor_type, Tensor, CodeOptions, float_type, int_type

import test_html

def test_call():
    f = define("f").param("x", int_type).call("do_something", "x")
    code = f.wgsl_code
    assert code.strip() == """
fn f(x: i32) -> void {
do_something(x);
}
// ERROR! Name do_something not found (name (name='do_something'))""".strip()

def test_forloop():
    f = define("f").forloop("i=0", "i < 10", "i+=1")
    code = f.wgsl_code
    assert code.strip() == """
fn f() -> void {
for (0; (i < 10); 1) {
}
}
// ERROR! Name i not found (name (name='i'))
""".strip()
