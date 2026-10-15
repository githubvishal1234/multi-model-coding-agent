import pytest

from account import Account


@pytest.mark.parametrize("amount", [0, -5, 100.01, 101])
def test_invalid_withdraw_raises_and_keeps_balance(amount):
    a = Account(100)
    with pytest.raises(ValueError):
        a.withdraw(amount)
    assert a.balance == 100


@pytest.mark.parametrize("amount,left", [(30, 70), (100, 0)])
def test_valid_withdraw(amount, left):
    a = Account(100)
    a.withdraw(amount)
    assert a.balance == left


def test_deposit_unchanged():
    a = Account(10)
    a.deposit(5)
    assert a.balance == 15
    with pytest.raises(ValueError):
        a.deposit(-1)
