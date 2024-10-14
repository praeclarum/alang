import os
from alang import define, struct, CodeOptions, get_language, Module

html_lang = get_language("html")

tests_dir = os.path.dirname(os.path.abspath(__file__))
proj_dir = os.path.dirname(tests_dir)
test_out_dir = os.path.join(proj_dir, "test_out")
os.makedirs(test_out_dir, exist_ok=True)

def write_standalone_html(mod_name, node):
    path = os.path.join(test_out_dir, f"{mod_name}.html")
    mod = node
    if mod.node_type != "module":
        mod = Module(mod_name)
        mod.append_any(node)
    mod.write_code(path, "html", CodeOptions(standalone=True, auto_entry_points=True))
    with open(path, "r") as f:
        return f.read()

def test_just_struct():
    s_a = struct(
        "TestStruct",
        ("u", "float"),
        ("v", "float"),
        ("w", "vec2f"),
        ("x", "float"),
    )
    assert s_a.html_code.strip().startswith("<h2>TestStruct</h2>")

def test_standalone_struct():
    s_a = struct(
        "TestStruct",
        ("u", "float"),
        ("v", "float"),
        ("w", "vec2f"),
        ("x", "float"),
    )
    html = write_standalone_html("test_standalone_struct", s_a)
    assert html.index("<h2>TestStruct</h2>") > 0

def test_standalone_function():
    f = define("f", ("x", "int")).ret("x")
    html = write_standalone_html("test_standalone_function", f)
    assert html.index("<h2>f</h2>") > 0
