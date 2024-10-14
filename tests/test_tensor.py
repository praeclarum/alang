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
alias float3x5x7x11 = array<f32, 1155>;
struct StructWithTensor {
    t: float3x5x7x11
}""".strip()

def test_3x5_times_5x7_type():
    t1 = tensor_type((3, 5), int_type)
    t2 = tensor_type((5, 7), int_type)
    t3 = t1 @ t2
    assert t3.shape == (3, 7)

def test_1x2_matmul_2x1():
    at = tensor_type((1, 2), int_type)
    bt = tensor_type((2, 1), int_type)
    ot = at @ bt
    f = define("f").param("a", at).param("b", bt).ret("a @ b")
    write_standalone_html("test_1x2_times_2x1", f)
    code = f.wgsl_code
    assert code.strip() == """
alias int1x2 = array<i32, 2>;
alias int2x1 = array<i32, 2>;
fn mul_int1x2_int2x1(a: int1x2, b: int2x1) -> int1x1 {
    var o: int1x1;
    for (var out_r: i32 = 0; out_r < 1; out_r++) {
        for (var out_c: i32 = 0; out_c < 1; out_c++) {
            o[((out_r * 1) + out_c)] = ((a[(out_r * 2)] * b[out_c]) + (a[((out_r * 2) + 1)] * b[(1 + out_c)]));
        }
    }
    return o;
}
alias int1x1 = array<i32, 1>;
fn f(a: int1x2, b: int2x1) -> int1x1 {
    return mul_int1x2_int2x1(a, b);
}""".strip()

def test_3x5_matmul_5x7():
    t1 = tensor_type((3, 5), int_type)
    t2 = tensor_type((5, 7), int_type)
    t3 = t1 @ t2
    f = define("f").param("a", t1).param("b", t2).ret("a @ b")
    write_standalone_html("test_3x5_times_5x7", f)
    code = f.wgsl_code
    assert code.strip() == """
alias int3x5 = array<i32, 15>;
alias int5x7 = array<i32, 35>;
fn mul_int3x5_int5x7(a: int3x5, b: int5x7) -> int3x7 {
    var o: int3x7;
    for (var out_r: i32 = 0; out_r < 3; out_r++) {
        for (var out_c: i32 = 0; out_c < 7; out_c++) {
            o[((out_r * 7) + out_c)] = (((((a[(out_r * 5)] * b[out_c]) + (a[((out_r * 5) + 1)] * b[(7 + out_c)])) + (a[((out_r * 5) + 2)] * b[(14 + out_c)])) + (a[((out_r * 5) + 3)] * b[(21 + out_c)])) + (a[((out_r * 5) + 4)] * b[(28 + out_c)]));
        }
    }
    return o;
}
alias int3x7 = array<i32, 21>;
fn f(a: int3x5, b: int5x7) -> int3x7 {
    return mul_int3x5_int5x7(a, b);
}""".strip()

def test_standalone_tensor():
    t = tensor_type((3, 5, 7, 11), float_type)
    s = struct("StructWithTensor", ("t", t))
    html = write_standalone_html("test_standalone_tensor", s)
    assert html.index("Float32Array") > 0

def test_const_flat_index():
    t = tensor_type((3, 5, 7, 11), float_type)
    def tt(index, expected):
        fi = t.get_flat_index(index)
        assert fi.node_type == "constant"
        assert fi.value == expected
    tt((0, 0, 0, 0), 0)
    tt((0, 0, 0, 1), 1)
    tt((1, 0, 0, 0), 1 * 5 * 7 * 11)
    tt((1, 2, 3, 4), 1 * 5 * 7 * 11 + 2 * 7 * 11 + 3 * 11 + 4)
    tt((2, 4, 6, 10),  2 * 5 * 7 * 11 + 4 * 7 * 11 + 6 * 11 + 10)

def test_const_flat_index():
    t = tensor_type((3, 5, 7, 11), float_type)
    def tt(index, expected):
        fi = t.get_flat_index(index)
        fi_code: str = fi.wgsl_code
        e_index = fi_code.find("//")
        if e_index > 0:
            fi_code = fi_code[:e_index].strip()
        assert fi_code == expected
    tt((0, 0, 0, 0), "0")
    tt((0, 0, 0, 1), "1")
    tt((0, 0, 0, "x"), "x")
    tt(("y", 0, 0, 0), "(y * 385)")
    tt(("y", 0, 0, "x"), "((y * 385) + x)")
