import pytest

from account import Account


def test_deposit():
    a = Account(10)
    a.deposit(5)
    assert a.balance == 15


def test_deposit_rejects_non_positive():
    with pytest.raises(ValueError):
        Account().deposit(0)
