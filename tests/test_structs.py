from alang import struct

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
    assert l.size == 24

def test_nested_struct_layout():
    # https://www.w3.org/TR/WGSL/#structure-member-layout
    s_a = struct(
        "A",
        ("u", "float"),
        ("v", "float"),
        ("w", "vec2f"),
        ("x", "float"),
    )
    s_b = struct(
        "B",
        ("a", "vec2f"),
        ("b", "vec3f"),
        ("c", "float"),
        ("d", "float"),
        # ("e", s_a),
    )
    l = s_b.layout
    fs = l.fields
    assert len(fs) == 4
    assert fs[0].triple == (0, 8, 8)
    assert fs[1].triple == (16, 16, 12)
    assert fs[2].triple == (28, 4, 4)
    assert fs[3].triple == (32, 4, 4)
    # assert fs[4].triple == (40, 8, 24)

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
