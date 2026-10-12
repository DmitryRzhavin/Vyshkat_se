"""Доменные модели и небольшие структурные интерфейсы."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class InventoryItem(Protocol):
    """Инвентаризируемый объект на балансе."""

    inventory_number: str
    name: str


@runtime_checkable
class EnergyConsumer(Protocol):
    """Объект с суточным потреблением энергии в кВт·ч."""

    daily_energy_kwh: float


@dataclass(slots=True)
class Transport:
    inventory_number: str
    name: str
    simplicity: int
    daily_energy_kwh: float
    technically_sound: bool

    def __post_init__(self) -> None:
        self.inventory_number = self.inventory_number.strip()
        self.name = self.name.strip()
        if not self.inventory_number:
            raise ValueError("Инвентарный номер не может быть пустым")
        if not self.name:
            raise ValueError("Наименование не может быть пустым")
        if not 1 <= self.simplicity <= 10:
            raise ValueError("Простота для новичка должна быть от 1 до 10")
        if self.daily_energy_kwh < 0:
            raise ValueError("Расход энергии не может быть отрицательным")


@dataclass(slots=True)
class Scooter(Transport):
    """Электросамокат."""


@dataclass(slots=True)
class Bicycle(Transport):
    """Велосипед."""


@dataclass(slots=True)
class ElectricBicycle(Transport):
    """Электровелосипед."""


@dataclass(slots=True)
class Helmet:
    inventory_number: str
    name: str = "Шлем"

    def __post_init__(self) -> None:
        self.inventory_number = self.inventory_number.strip()
        if not self.inventory_number:
            raise ValueError("Инвентарный номер не может быть пустым")


@dataclass(slots=True)
class ChargingStation:
    inventory_number: str
    name: str = "Зарядная станция"
    daily_energy_kwh: float = 0.0

    def __post_init__(self) -> None:
        self.inventory_number = self.inventory_number.strip()
        if not self.inventory_number:
            raise ValueError("Инвентарный номер не может быть пустым")
        if self.daily_energy_kwh < 0:
            raise ValueError("Расход энергии не может быть отрицательным")
