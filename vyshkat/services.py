"""Бизнес-логика: парк, техосмотр и сценарий приёмки."""

from dataclasses import dataclass
from typing import Protocol

from .domain import EnergyConsumer, InventoryItem, Transport


class ServiceCenter(Protocol):
    """Абстракция техосмотра."""

    def inspect(self, transport: Transport) -> bool:
        ...


class DefaultServiceCenter:
    """Простое правило для учебной модели: исправный транспорт проходит осмотр."""

    def inspect(self, transport: Transport) -> bool:
        return transport.technically_sound


class Fleet:
    """Хранилище активов и вычисляемые отчёты по ним."""

    def __init__(self) -> None:
        self._assets: dict[str, InventoryItem] = {}

    @property
    def assets(self) -> tuple[InventoryItem, ...]:
        return tuple(self._assets.values())

    @property
    def transports(self) -> tuple[Transport, ...]:
        return tuple(item for item in self._assets.values() if isinstance(item, Transport))

    @property
    def non_transport_items(self) -> tuple[InventoryItem, ...]:
        return tuple(item for item in self._assets.values() if not isinstance(item, Transport))

    def contains_inventory_number(self, number: str) -> bool:
        return number.strip() in self._assets

    def add_asset(self, item: InventoryItem) -> None:
        number = item.inventory_number.strip()
        if not number:
            raise ValueError("Инвентарный номер не может быть пустым")
        if number in self._assets:
            raise ValueError(f"Инвентарный номер {number!r} уже используется")
        self._assets[number] = item

    def total_daily_energy_kwh(self) -> float:
        return sum(
            item.daily_energy_kwh
            for item in self._assets.values()
            if isinstance(item, EnergyConsumer)
        )

    def suitable_for_beginners(self, threshold: int = 6) -> tuple[Transport, ...]:
        if not 1 <= threshold <= 10:
            raise ValueError("Порог простоты должен быть от 1 до 10")
        return tuple(item for item in self.transports if item.simplicity >= threshold)


@dataclass(frozen=True, slots=True)
class AcceptanceResult:
    accepted: bool
    message: str


class FleetService:
    """Прикладной сервис, который координирует приёмку и учёт имущества."""

    def __init__(self, fleet: Fleet, service_center: ServiceCenter) -> None:
        self._fleet = fleet
        self._service_center = service_center

    @property
    def fleet(self) -> Fleet:
        return self._fleet

    def accept_transport(self, transport: Transport) -> AcceptanceResult:
        number = transport.inventory_number
        if self._fleet.contains_inventory_number(number):
            return AcceptanceResult(False, f"Номер {number} уже есть на балансе")
        if not self._service_center.inspect(transport):
            return AcceptanceResult(False, f"{number}: техосмотр не пройден; транспорт не принят")
        self._fleet.add_asset(transport)
        return AcceptanceResult(True, f"{number}: транспорт принят")

    def add_item(self, item: InventoryItem) -> None:
        self._fleet.add_asset(item)
