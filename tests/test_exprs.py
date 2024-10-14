from alang.exprs import Constant

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
