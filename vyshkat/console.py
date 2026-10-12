"""Интерактивный текстовый интерфейс; бизнес-правила остаются в services.py."""

from typing import Callable, TextIO

from .domain import Bicycle, ChargingStation, ElectricBicycle, Helmet, Scooter, Transport
from .services import FleetService

Input = Callable[[str], str]

# Вид транспорта -> модель. При добавлении типа транспорта расширяется эта таблица,
# а доменные отчёты и правила приёмки менять не нужно.
TRANSPORT_TYPES: dict[str, type[Transport]] = {
    "1": Scooter,
    "2": Bicycle,
    "3": ElectricBicycle,
}
TRANSPORT_LABELS = {"1": "Электросамокат", "2": "Велосипед", "3": "Электровелосипед"}


class ConsoleApp:
    def __init__(self, service: FleetService, input_fn: Input = input, output: TextIO | None = None) -> None:
        self._service = service
        self._input = input_fn
        self._output = output

    def _print(self, text: str = "") -> None:
        if self._output is None:
            print(text)
        else:
            print(text, file=self._output)

    def _ask_int(self, prompt: str, minimum: int, maximum: int) -> int:
        while True:
            raw = self._input(prompt).strip()
            try:
                value = int(raw)
                if minimum <= value <= maximum:
                    return value
            except ValueError:
                pass
            self._print(f"Введите целое число от {minimum} до {maximum}.")

    def _ask_float(self, prompt: str, minimum: float = 0.0) -> float:
        while True:
            raw = self._input(prompt).strip().replace(",", ".")
            try:
                value = float(raw)
                if value >= minimum:
                    return value
            except ValueError:
                pass
            self._print(f"Введите число не меньше {minimum}.")

    def _add_transport(self) -> None:
        self._print("Вид транспорта: 1 — электросамокат, 2 — велосипед, 3 — электровелосипед")
        kind = str(self._ask_int("Выберите вид: ", 1, 3))
        inventory_number = self._input("Инвентарный номер: ").strip()
        name = self._input("Наименование/модель: ").strip()
        simplicity = self._ask_int("Простота для новичка (1–10): ", 1, 10)
        energy = self._ask_float("Суточный расход, кВт·ч: ")
        sound = self._input("Транспорт исправен? (д/н): ").strip().lower()
        while sound not in {"д", "да", "н", "нет"}:
            sound = self._input("Введите «д» или «н»: ").strip().lower()
        transport_type = TRANSPORT_TYPES[kind]
        transport = transport_type(
            inventory_number=inventory_number,
            name=name,
            simplicity=simplicity,
            daily_energy_kwh=energy,
            technically_sound=sound in {"д", "да"},
        )
        result = self._service.accept_transport(transport)
        self._print(result.message)

    def _add_item(self) -> None:
        self._print("Вещь: 1 — шлем, 2 — зарядная станция")
        kind = self._ask_int("Выберите вид вещи: ", 1, 2)
        number = self._input("Инвентарный номер: ").strip()
        if kind == 1:
            item = Helmet(number)
        else:
            energy = self._ask_float("Суточный расход станции, кВт·ч: ")
            item = ChargingStation(number, daily_energy_kwh=energy)
        try:
            self._service.add_item(item)
            self._print(f"{item.name} [{item.inventory_number}] добавлен(а) на баланс.")
        except ValueError as error:
            self._print(f"Не удалось добавить вещь: {error}")

    def _show_summary(self) -> None:
        fleet = self._service.fleet
        self._print(f"Всего единиц на балансе: {len(fleet.assets)}")
        self._print(f"Транспортных средств: {len(fleet.transports)}")
        self._print(f"Вещей: {len(fleet.non_transport_items)}")
        self._print(f"Суточное потребление: {fleet.total_daily_energy_kwh():.2f} кВт·ч")

    def _show_beginners(self) -> None:
        items = self._service.fleet.suitable_for_beginners()
        self._print("Техника для новичков (простота ≥ 6):")
        if not items:
            self._print("  Подходящей техники пока нет.")
        for item in items:
            self._print(f"  {item.name} [{item.inventory_number}], простота {item.simplicity}/10")

    def _show_assets(self) -> None:
        items = self._service.fleet.assets
        self._print("Имущество на балансе:")
        if not items:
            self._print("  Парк пока пуст.")
        for item in items:
            self._print(f"  {item.name} [{item.inventory_number}]")

    def run(self) -> None:
        actions = {
            "1": self._add_transport,
            "2": self._add_item,
            "3": self._show_summary,
            "4": self._show_beginners,
            "5": self._show_assets,
        }
        self._print("ВышКат — система учёта парка")
        while True:
            self._print("\n1 — принять транспорт | 2 — добавить вещь | 3 — сводка | 4 — техника для новичков | 5 — всё имущество | 0 — выход")
            choice = self._input("Ваш выбор: ").strip()
            if choice == "0":
                self._print("Работа завершена.")
                return
            action = actions.get(choice)
            if action is None:
                self._print("Неизвестная команда. Выберите пункт меню от 0 до 5.")
                continue
            try:
                action()
            except ValueError as error:
                self._print(f"Некорректные данные: {error}")
