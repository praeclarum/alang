from alang.nodes import define
from alang.typs import struct_type, tensor_type, Tensor, float_type, int_type, looks_like_tensor

from alang.vals import TensorValue
from test_html import write_standalone_html

def test_tensor_from_element_type():
    t = tensor_type((3, 5, 7, 11), int_type)
    assert t.element_type.name == "int"

def test_tensor_from_str_element_type():
    t = tensor_type((3, 5, 7, 11), "short")
    assert t.element_type.name == "short"

def test_tensor_from_str_element_type():
    s = struct_type("S", ("t", "byte42x69x7"))
    t: Tensor = s.fields[0].field_type
    assert t.node_type == "tensor"
    assert t.element_type.name == "byte"

def test_tensor_wgsl():
    t = tensor_type((3, 5, 7, 11), float_type)
    s = struct_type("StructWithTensor", ("t", t))
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
    s = struct_type("StructWithTensor", ("t", t))
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

def test_doesnt_look_like_tensor():
    assert looks_like_tensor(0) == False
    assert looks_like_tensor("hello") == False
    assert looks_like_tensor(None) == False

def test_custom_tensor_looks_like_tensor():
    class T:
        def __init__(self):
            self.dtype = "int"
            self.shape = (1, 2, 3)
    assert looks_like_tensor(T())

def do_test_serialize(ct):
    t = ct([0x00, 0x11, 0x22])
    tv = TensorValue(None, t)
    bs = tv.serialize()
    assert bs == b"\x00\x00\x00\x00\x11\x00\x00\x00\x22\x00\x00\x00"

def do_test_serialize_view(ct):
    t = ct([
        [0x0100, 0x0111, 0x0122],
        [0x0200, 0x0211, 0x0222],
        [0x0300, 0x0311, 0x0322],
        [0x0400, 0x0411, 0x0422],
    ])
    tt = t.T
    ttt = tt[1:2, 2:4]
    tv = TensorValue(None, ttt)
    bs = tv.serialize()
    # print([hex(x) for x in ttt.flatten()])
    assert bs == b"\x11\x03\x00\x00\x11\x04\x00\x00"

# def test_serialize_numpy_array():
#     import numpy as np
#     ct = lambda x: np.array(x, dtype=np.int32)
#     do_test_serialize(ct)
#     do_test_serialize_view(ct)

# def test_serialize_torch_tensor():
#     import torch
#     ct = lambda x: torch.tensor(x, dtype=torch.int32)
#     do_test_serialize(ct)
#     do_test_serialize_view(ct)

# def test_torch_tensor_looks_like_tensor():
#     import torch
#     assert looks_like_tensor(torch.tensor([1.0, 2.0, 3.0]))
#     assert looks_like_tensor(torch.tensor([1.0, 2.0, 3.0], dtype=torch.float32))
#     assert looks_like_tensor(torch.tensor(0))
#     assert looks_like_tensor(torch.tensor(1) + torch.tensor(1))
#     assert not looks_like_tensor(torch.nn.Module())

# def test_tensor_type_from_torch_tensor():
#     import torch
#     t3f = tensor_type(torch.tensor([1.0, 2.0, 3.0]))
#     assert t3f is not None
#     assert t3f.shape == [3,]
#     assert t3f.element_type.name == "float"
#     t3l = tensor_type(torch.tensor([1, 2, 3], dtype=torch.int64))
#     assert t3l is not None
#     assert t3l.shape == [3,]
#     assert t3l.element_type.name == "long"

# def test_numpy_array_looks_like_tensor():
#     import numpy as np
#     assert looks_like_tensor(np.array([1.0, 2.0, 3.0]))
#     assert looks_like_tensor(np.array([1.0, 2.0, 3.0], dtype=np.float32))
#     assert looks_like_tensor(np.array(0))

# def test_tensor_type_from_numpy_array():
#     import numpy as np
#     t3f = tensor_type(np.array([1.0, 2.0, 3.0]))
#     assert t3f is not None
#     assert t3f.shape == [3,]
#     assert t3f.element_type.name == "double"
#     t3l = tensor_type(np.array([1, 2, 3], dtype=np.int64))
#     assert t3l is not None
#     assert t3l.shape == [3,]
#     assert t3l.element_type.name == "long"
