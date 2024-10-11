from alang import array, struct, CodeOptions

def test_simple_struct_layout():
    # https://www.w3.org/TR/WGSL/#structure-member-layout
    s_a = struct(
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
    s_a = struct(
        "A",
        ("u", "float"),
        ("v", "float"),
        ("w", "vec2f"),
        ("x", "float"),
    )
    a = array(s_a, 3)
    s_b = struct(
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
    s = struct("Point", ("x", "int"), ("y", "int"))
    assert s.code.strip() == """
struct Point:
    x: int
    y: int
    """.strip()

def test_struct_wgsl():
    s = struct(
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
    point_light = struct(
        "PointLight",
        ("position", "vec3f"),
        ("color", "vec3f"),
    )
    light_storage = struct(
        "LightStorage",
        ("pointCount", "uint"),
        ("point", array(point_light)),
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
    s_a = struct(
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
