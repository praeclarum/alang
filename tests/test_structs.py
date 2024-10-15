from io import BytesIO
from alang.typs import array_type, struct_type
from alang.nodes import CodeOptions
from alang.vals import StructValue

def test_simple_struct_layout():
    # https://www.w3.org/TR/WGSL/#structure-member-layout
    s_a = struct_type(
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
    assert l.byte_size == 24

def test_nested_struct_layout():
    # https://www.w3.org/TR/WGSL/#structure-member-layout
    s_a = struct_type(
        "A",
        ("u", "float"),
        ("v", "float"),
        ("w", "vec2f"),
        ("x", "float"),
    )
    a = array_type(s_a, 3)
    s_b = struct_type(
        "B",
        ("a", "vec2f"),
        ("b", "vec3f"),
        ("c", "float"),
        ("d", "float"),
        ("e", s_a),
        ("f", "vec3f"),
        ("g", a),
        ("h", "int"),
    )
    l = s_b.layout
    fs = l.fields
    assert len(fs) == 8
    assert fs[0].triple == (0, 8, 8)
    assert fs[1].triple == (16, 16, 12)
    assert fs[2].triple == (28, 4, 4)
    assert fs[3].triple == (32, 4, 4)
    assert fs[4].triple == (40, 8, 24)
    assert fs[5].triple == (64, 16, 12)
    assert a.layout.element_stride == 24
    assert fs[6].triple == (80, 8, 72)
    assert fs[7].triple == (152, 4, 4)
    assert l.align == 16
    assert l.byte_size == 160

def test_struct_a():
    s = struct_type("Point", ("x", "int"), ("y", "int"))
    assert s.code.strip() == """
struct Point:
    x: int
    y: int
    """.strip()

def test_struct_wgsl():
    s = struct_type(
        "Ray",
        ("id", "int"),
        ("position", "vec3f"),
        ("direction", "vec3f"),
    )
    assert s.wgsl_code.strip() == """
struct Ray {
    id: i32,
    position: vec3<f32>,
    direction: vec3<f32>
}""".strip()

def test_runtime_sized():
    # https://www.w3.org/TR/WGSL/#buffer-binding-determines-runtime-sized-array-element-count
    point_light = struct_type(
        "PointLight",
        ("position", "vec3f"),
        ("color", "vec3f"),
    )
    light_storage = struct_type(
        "LightStorage",
        ("pointCount", "uint"),
        ("point", array_type(point_light)),
    )
    pl = point_light.layout
    assert pl.align == 16
    assert pl.byte_size == 32
    
    def test_buffer_size(buffer_size, expected_point_count):
        sl = light_storage.get_layout(buffer_size)
        fl = sl.fields[-1]
        assert sl.align == 16
        assert fl.num_elements == expected_point_count

    test_buffer_size(1024, 31)
    test_buffer_size(1025, 31)
    test_buffer_size(1039, 31)
    test_buffer_size(1040, 32)

def test_annotations():
    # https://www.w3.org/TR/WGSL/#structure-member-layout
    s_a = struct_type(
        "A",
        ("u", "float"),
        ("v", "float"),
        ("w", "vec2f"),
        ("x", "float"),
    )
    assert s_a.get_code("wgsl", CodeOptions(struct_annotations=True)).strip() == """
struct A {                                     //             align(8)  size(24)
    u: f32,                                    // offset(0)   align(4)  size(4)
    v: f32,                                    // offset(4)   align(4)  size(4)
    w: vec2<f32>,                              // offset(8)   align(8)  size(8)
    x: f32                                     // offset(16)  align(4)  size(4)
}
""".strip()
    
def test_create_struct():
    st = struct_type("Point", ("x", "int"), ("y", "int"))
    s: StructValue = st.create()
    assert s.type.name == "Point"

def test_init_struct():
    st = struct_type("Point", ("x", "int"), ("y", "int"))
    s: StructValue = st.create(x=42, y=69)
    assert s.x == 42
    assert s.y == 69
    s.x = 100
    assert s.x == 100

def test_mutate_struct():
    st = struct_type("Point", ("x", "int"), ("y", "int"))
    s: StructValue = st.create()
    assert s.x == 0
    assert s.y == 0
    s.x = 100
    assert s.x == 100
    s.y = 200
    assert s.y == 200

def test_cant_set_nonfield():
    st = struct_type("Point", ("x", "int"), ("y", "int"))
    s: StructValue = st.create()
    try:
        s.z = 42
        assert False
    except AttributeError:
        pass

def test_write():
    st = struct_type("Point", ("x", "int"), ("y", "int"))
    s: StructValue = st.create()
    sl = st.layout
    bs = BytesIO()
    s.write(bs)
    bs = bs.getvalue()
    assert len(bs) == sl.byte_size
    assert bs == b"\x00\x00\x00\x00\x00\x00\x00\x00"

def test_serialize_padding():
    st = struct_type("NeedsPadding", ("x", "int"), ("y", "vec4f"))
    s: StructValue = st.create()
    sl = st.layout
    bs = s.serialize()
    assert len(bs) == sl.byte_size

def test_serialize_struct_in_struct():
    inner_st = struct_type("Inner", ("x", "int"), ("y", "int"))
    outer_st = struct_type("Outer", ("a", "int"), ("b", inner_st))
    s: StructValue = outer_st.create()
    s.a = 0x42
    s.b.x = 0x69
    s.b.y = 0x96
    sl = outer_st.layout
    bs = s.serialize()
    assert len(bs) == sl.byte_size
    assert bs == b"\x42\x00\x00\x00\x69\x00\x00\x00\x96\x00\x00\x00"

def test_serialize_array_in_struct():
    at = array_type("int", 2)
    st = struct_type("Outer", ("a", at), ("b", "int"))
    s: StructValue = st.create()
    s.a[0] = 0x42
    s.a[1] = 0x69
    s.b = 0x96
    sl = st.layout
    bs = s.serialize()
    assert len(bs) == sl.byte_size
    assert bs == b"\x42\x00\x00\x00\x69\x00\x00\x00\x96\x00\x00\x00"

def test_serialize_struct_in_array():
    inner_st = struct_type("Inner", ("x", "int"), ("y", "int"))
    at = array_type(inner_st, 2)
    s: StructValue = at.create()
    s[0].x = 0x42
    s[0].y = 0x69
    s[1].x = 0x96
    s[1].y = 0x23
    sl = at.layout
    bs = s.serialize()
    assert len(bs) == sl.byte_size
    assert bs == b"\x42\x00\x00\x00\x69\x00\x00\x00\x96\x00\x00\x00\x23\x00\x00\x00"

def test_serialize_struct_in_array_in_struct():
    inner_st = struct_type("Inner", ("x", "int"), ("y", "int"))
    at = array_type(inner_st, 2)
    outer_st = struct_type("Outer", ("a", at), ("b", "int"))
    s: StructValue = outer_st.create()
    s.a[0].x = 0x42
    s.a[0].y = 0x69
    s.a[1].x = 0x96
    s.a[1].y = 0x23
    s.b = 0x96
    sl = outer_st.layout
    bs = s.serialize()
    assert len(bs) == sl.byte_size
    assert bs == b"\x42\x00\x00\x00\x69\x00\x00\x00\x96\x00\x00\x00\x23\x00\x00\x00\x96\x00\x00\x00"
