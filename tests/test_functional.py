import pytest

from src.models import Parameters
from src.manager import Manager


def test_tenants_settlements_sum_equals_apartment_costs():
    manager = Manager(Parameters())

    apartment_key = 'apart-polanka'
    year, month = 2025, 1

    apartment_settlement = manager.get_settlement(apartment_key, year, month)
    assert apartment_settlement is not None

    tenants_settlements = manager.create_tenants_settlements(apartment_settlement)
    assert len(tenants_settlements) > 0

    tenants_total = sum(s.total_due_pln for s in tenants_settlements)
    apartment_costs = manager.get_apartment_costs(apartment_key, year, month)

    assert apartment_costs == 910.0
    assert tenants_total == pytest.approx(apartment_costs)
    assert tenants_total == pytest.approx(apartment_settlement.total_due_pln)


def test_get_debtors():
    manager = Manager(Parameters())

    assert manager.get_debtors('apart-polanka', 1, 2025) == []
    assert manager.get_debtors('apart-polanka', 2, 2025) == ['Jan Nowak', 'Adam Kowalski', 'Ewa Adamska']
    assert manager.get_debtors('nie-ma', 1, 2025) is None
    with pytest.raises(ValueError):
        manager.get_debtors('apart-polanka', 13, 2025)
