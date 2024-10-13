from alang import define, struct, tensor_type, Tensor, CodeOptions, float_type, int_type

from alang.exprs import Constant

from test_html import write_standalone_html

def test_constant_mul():
    assert Constant(42).mul(Constant(69)).value == 42 * 69
    assert (Constant(42) * Constant(69)).value == 42 * 69
    assert (Constant(42) * 69).value == 42 * 69
    assert (Constant(42) * "23 * 3").value == 42 * 69

def test_constant_add():
    assert Constant(42).add(Constant(69)).value == 42 + 69
    assert (Constant(42) + Constant(69)).value == 42 + 69
    assert (Constant(42) + 69).value == 42 + 69
    assert (Constant(42) + "60 + 9").value == 42 + 69

def test_constant_sub():
    assert Constant(42).sub(Constant(69)).value == 42 - 69
    assert (Constant(42) - Constant(69)).value == 42 - 69
    assert (Constant(42) - 69).value == 42 - 69
    assert (Constant(42) - "72 - 3").value == 42 - 69
