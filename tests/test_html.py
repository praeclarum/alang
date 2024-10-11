from alang import array, struct, CodeOptions

def test_simple_struct():
    s_a = struct(
        "A",
        ("u", "float"),
        ("v", "float"),
        ("w", "vec2f"),
        ("x", "float"),
    )
    assert s_a.html_code.strip().startswith("<h2>A</h2>")
