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
    write_standalone_html("test_3x5_times_5x7", f)
    code = f.wgsl_code
    assert code.strip() == """
fn mul_int3x5_int5x7(a: int3x5, b: int5x7) -> int3x7 {
for (var out_c: i32 = 0; out_c < 7; ++out_c) {
for (var out_r: i32 = 0; out_r < 3; ++out_r) {
o[((out_r * 7) + out_c)] = ((((a[0] + a[1]) + a[2]) + a[3]) + a[4]);
}
}
}
fn f(a: int3x5, b: int5x7) -> int3x7 {
    return mul_int3x5_int5x7(a, b);
}""".strip()

def test_standalone_tensor():
    t = tensor_type((3, 5, 7, 11), float_type)
    s = struct("StructWithTensor", ("t", t))
    html = write_standalone_html("test_standalone_tensor", s)
    assert html.index("Float32Array") > 0

def test_flat_index():
    t = tensor_type((3, 5, 7, 11), float_type)
    assert t.get_flat_index((0, 0, 0, 0)) == 0
    assert t.get_flat_index((0, 0, 0, 1)) == 1
    assert t.get_flat_index((1, 0, 0, 0)) == 1 * 5 * 7 * 11
    assert t.get_flat_index((1, 2, 3, 4)) == 1 * 5 * 7 * 11 + 2 * 7 * 11 + 3 * 11 + 4
    assert t.get_flat_index((2, 4, 6, 10)) == 2 * 5 * 7 * 11 + 4 * 7 * 11 + 6 * 11 + 10
