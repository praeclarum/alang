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

def simple_array_layout():
    s_a = array(
        "A",
        ("u", "float"),
        ("v", "float"),
        ("w", "vec2f"),
        ("x", "float"),
    )
    l = s_a.layout
    fs = l.fields
    assert len(fs) == 4
    assert fs[0].triple == (0, 4, 4)
    assert fs[1].triple == (4, 4, 4)
    assert fs[2].triple == (8, 8, 8)
    assert fs[3].triple == (16, 4, 4)
    assert l.align == 8
    assert l.size == 24
