from alang import array, struct, CodeOptions

def test_simple_struct():
    # https://www.w3.org/TR/WGSL/#structure-member-layout
    s_a = struct(
        "A",
        ("u", "float"),
        ("v", "float"),
        ("w", "vec2f"),
        ("x", "float"),
    )
    assert s_a.js_code.strip() == """
class A {
    constructor(buffer, index, length) {
        if (buffer instanceof ArrayBuffer) {
            this.buffer = buffer;
            this.index = index || 0;
            this.length = length || 24;
            if (this.length < 24) throw new Error(`Buffer too small. "A" requires at least 24 bytes, got ${this.length}`);
            if (this.index + this.length >= buffer.byteLength) throw new Error(`Buffer overflow. "A" requires ${this.length} bytes starting at ${this.index}, but the buffer is only ${buffer.byteLength} bytes long`);
        } else {
            this.buffer = new ArrayBuffer(24);
            this.index = 0;
            this.length = 24;
        }
    }
}
""".strip()
