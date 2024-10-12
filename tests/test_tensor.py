from alang import array, struct, tensor, CodeOptions, typs

def test_tensor_wgsl():
    t = tensor((3, 5, 7, 11), typs.float_type)
    s = struct("StructWithTensor", ("t", t))
    assert s.wgsl_code.strip() == """
struct StructWithTensor {
    t: float3x5x7x11f
}""".strip()
