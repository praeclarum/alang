from alang import array

def test_is_fixed():
    a = array("int", 10)
    assert a.is_fixed_size
    assert not a.is_runtime_sized
    assert a.num_elements == 10

def test_is_runtime():
    a = array("int")
    assert not a.is_fixed_size
    assert a.is_runtime_sized
    assert a.num_elements is None

# https://www.w3.org/TR/WGSL/#array-layout-examples

def test_small_stride():
    a = array("float", 8)
    l = a.layout
    assert l.align == 4
    assert l.element_stride == 4
    assert l.byte_size == 32

def test_bigger_stride():
    a = array("vec3f", 8)
    l = a.layout
    assert l.align == 16
    assert l.element_stride == 16
    assert l.byte_size == 128

def test_runtime_sized_nobuffer():
    a = array("float")
    l = a.layout
    assert l.align == 4
    assert l.element_stride == 4
    assert l.byte_size == 0

def test_runtime_sized_floats():
    a = array("float")
    l = a.get_layout(8)
    assert l.align == 4
    assert l.element_stride == 4
    assert l.num_elements == 2
    assert l.byte_size == 8

def test_runtime_sized_float3s_not_enough_buffer():
    a = array("vec3f")
    l = a.get_layout(8)
    assert l.align == 16
    assert l.element_stride == 16
    assert l.num_elements == 0
    assert l.byte_size == 0

def test_runtime_sized_float3s():
    a = array("vec3f")
    l = a.get_layout(48)
    assert l.align == 16
    assert l.element_stride == 16
    assert l.num_elements == 3
    assert l.byte_size == 48

def test_runtime_truncation():
    # https://www.w3.org/TR/WGSL/#buffer-binding-determines-runtime-sized-array-element-count
    a = array("float")
    assert a.get_layout(1024).num_elements == 256
    assert a.get_layout(1025).num_elements == 256
    assert a.get_layout(1026).num_elements == 256
    assert a.get_layout(1027).num_elements == 256
    assert a.get_layout(1028).num_elements == 257
