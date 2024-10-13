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
