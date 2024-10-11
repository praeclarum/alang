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
    constructor(buffer, byteOffset, byteLength) {
        byteOffset = byteOffset || 0;
        byteLength = byteLength || 24;
        if (byteLength < 24) throw new Error(`Buffer too small. "A" requires at least 24 bytes, got ${byteLength}`);
        if (buffer instanceof ArrayBuffer) {
            this.buffer = buffer;
        } else {
            this.buffer = new ArrayBuffer(byteLength);
            byteOffset = 0;
        }
        if (byteOffset + byteLength >= this.buffer.byteLength) throw new Error(`Buffer overflow. "A" requires ${byteLength} bytes starting at ${byteOffset}, but the buffer is only ${this.buffer.byteLength} bytes long`);
        this.view = new DataView(this.buffer, byteOffset, byteLength);
        this.byteLength = byteLength;
        this.gpuBuffer = null;
        this.isDirty = false;
    }
    dirty() { this.isDirty = true; }
    get u() { return this.view.getFloat32(0); }
    set u(value) { return this.view.setFloat32(0, value); this.dirty(); }
    get v() { return this.view.getFloat32(4); }
    set v(value) { return this.view.setFloat32(4, value); this.dirty(); }
    get x() { return this.view.getFloat32(16); }
    set x(value) { return this.view.setFloat32(16, value); this.dirty(); }
}
""".strip()
