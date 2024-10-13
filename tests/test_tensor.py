from alang import define, struct, tensor_type, Tensor, CodeOptions, float_type, int_type

from test_html import write_standalone_html

def test_tensor_from_element_type():
    t = tensor_type((3, 5, 7, 11), int_type)
    assert t.element_type.name == "int"

def test_tensor_from_str_element_type():
    t = tensor_type((3, 5, 7, 11), "short")
    assert t.element_type.name == "short"

def test_tensor_from_str_element_type():
    s = struct("S", ("t", "byte42x69x7"))
    t: Tensor = s.fields[0].field_type
    assert t.node_type == "tensor"
    assert t.element_type.name == "byte"

def test_tensor_wgsl():
    t = tensor_type((3, 5, 7, 11), float_type)
    s = struct("StructWithTensor", ("t", t))
    assert s.wgsl_code.strip() == """
struct StructWithTensor {
    t: float3x5x7x11
}""".strip()

def test_3x5_times_5x7_type():
    t1 = tensor_type((3, 5), int_type)
    t2 = tensor_type((5, 7), int_type)
    t3 = t1 @ t2
    assert t3.shape == (3, 7)

def test_3x5_times_5x7():
    t1 = tensor_type((3, 5), int_type)
    t2 = tensor_type((5, 7), int_type)
    t3 = t1 @ t2
    f = define("f").param("a", t1).param("b", t2).ret("a @ b")
    code = f.wgsl_code
    assert code.strip() == """
fn mul_int3x5_int5x7(a: int3x5, b: int5x7) -> int3x7 {
for (var out_r: i32 = 0; out_r < 3; ++out_r) {
for (var out_c: i32 = 0; out_c < 7; ++out_c) {
}
}
}
fn f(a: int3x5, b: int5x7) -> int3x7 {
    return mul_int3x5_int5x7(a, b);
}""".strip()
    write_standalone_html("test_3x5_times_5x7", f)

def test_standalone_tensor():
    t = tensor_type((3, 5, 7, 11), float_type)
    s = struct("StructWithTensor", ("t", t))
    html = write_standalone_html("test_standalone_tensor", s)
    assert html.index("Float32Array") > 0
