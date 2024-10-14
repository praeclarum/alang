from alang import define, struct, tensor_type, Tensor, CodeOptions, float_type, int_type

from test_html import write_standalone_html

def test_call():
    f = define("f").param("x", int_type).call("do_something", "x")
    code = f.wgsl_code
    assert code.strip() == """
fn f(x: i32) {
    do_something(x);
}
// ERROR! Name do_something not found (name (name='do_something'))""".strip()

def test_loop():
    f = define("f").loop("i", 10)
    code = f.wgsl_code
    assert code.strip() == """
fn f() {
    for (var i: i32 = 0; i < 10; i++) {
    }
}
""".strip()
    write_standalone_html("test_loop", f)
