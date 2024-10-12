from alang import array, struct, tensor, CodeOptions, float_type

import test_html

def test_tensor_wgsl():
    t = tensor((3, 5, 7, 11), float_type)
    s = struct("StructWithTensor", ("t", t))
    assert s.wgsl_code.strip() == """
struct StructWithTensor {
    t: float3x5x7x11f
}""".strip()

def test_standalone_tensor():
    t = tensor((3, 5, 7, 11), float_type)
    s = struct("StructWithTensor", ("t", t))
    html = test_html.write_standalone_html("test_standalone_tensor", s)
    assert html.index("Float32Array") > 0
