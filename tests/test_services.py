import pytest
from dependency_injector import providers

from vyshkat.container import Container
from vyshkat.domain import ChargingStation, ElectricBicycle, Helmet, Scooter
from vyshkat.services import Fleet, FleetService


class FakeServiceCenter:
    def __init__(self, decision: bool) -> None:
        self.decision = decision
        self.inspected = []

    def inspect(self, transport):
        self.inspected.append(transport)
        return self.decision


def service_with(decision=True):
    fleet = Fleet()
    return fleet, FleetService(fleet, FakeServiceCenter(decision))


def test_successful_inspection_adds_transport():
    fleet, service = service_with()
    result = service.accept_transport(Scooter("S-1", "Самокат", 7, 1.2, True))
    assert result.accepted
    assert [item.inventory_number for item in fleet.transports] == ["S-1"]


def test_failed_inspection_does_not_add_transport():
    fleet = Fleet()
    fake = FakeServiceCenter(False)
    service = FleetService(fleet, fake)
    transport = Scooter("S-2", "Неисправный самокат", 8, 1.0, True)
    result = service.accept_transport(transport)
    assert not result.accepted
    assert fake.inspected == [transport]
    assert fleet.assets == ()


def test_di_container_can_override_inspection_dependency():
    container = Container()
    fake = FakeServiceCenter(False)
    container.service_center.override(providers.Object(fake))
    service = container.fleet_service()
    result = service.accept_transport(Scooter("S-DI", "Самокат", 8, 1.0, True))
    assert not result.accepted
    assert len(fake.inspected) == 1
    assert container.fleet().assets == ()


def test_beginner_threshold_is_inclusive_at_six():
    fleet, service = service_with()
    service.accept_transport(Scooter("S-6", "Пороговый", 6, 1.0, True))
    service.accept_transport(Scooter("S-5", "Сложный", 5, 1.0, True))
    assert [item.inventory_number for item in fleet.suitable_for_beginners()] == ["S-6"]


def test_energy_report_counts_energy_consumers_including_station():
    fleet, service = service_with()
    service.accept_transport(Scooter("S-1", "Самокат", 7, 1.25, True))
    service.accept_transport(ElectricBicycle("E-1", "Электровелосипед", 6, 2.5, True))
    service.add_item(ChargingStation("C-1", daily_energy_kwh=4.0))
    service.add_item(Helmet("H-1"))
    assert fleet.total_daily_energy_kwh() == 7.75
    assert len(fleet.assets) == 4


def test_duplicate_inventory_number_is_rejected_for_all_assets():
    fleet, service = service_with()
    service.add_item(Helmet("DUP"))
    with pytest.raises(ValueError, match="уже используется"):
        service.add_item(Helmet("DUP"))


def test_invalid_domain_values_are_rejected():
    with pytest.raises(ValueError):
        Scooter("S", "Самокат", 11, 1.0, True)
    with pytest.raises(ValueError):
        Scooter("S", "Самокат", 5, -1.0, True)


def test_default_inspection_rejects_unfit_transport():
    from vyshkat.services import DefaultServiceCenter
    assert not DefaultServiceCenter().inspect(Scooter("S", "Самокат", 5, 0.0, False))
