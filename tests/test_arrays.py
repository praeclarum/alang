from alang import array

def test_is_fixed():
    a = array("int", 10)
    assert a.is_fixed_size
    assert not a.is_runtime_sized
    assert a.length == 10

def test_is_runtime():
    a = array("int")
    assert not a.is_fixed_size
    assert a.is_runtime_sized
    assert a.length is None

def test_small_stride():
    # https://www.w3.org/TR/WGSL/#array-layout-examples
    a = array("float", 8)
    l = a.layout
    assert l.align == 4
    assert l.element_stride == 4
    assert l.size == 32

def test_bigger_stride():
    # https://www.w3.org/TR/WGSL/#array-layout-examples
    a = array("vec3f", 8)
    l = a.layout
    assert l.align == 16
    assert l.element_stride == 16
    assert l.size == 128
