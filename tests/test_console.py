from io import StringIO

from vyshkat.console import ConsoleApp
from vyshkat.services import Fleet, FleetService


class AcceptAll:
    def inspect(self, transport):
        return True


def test_console_accepts_user_entered_transport_and_shows_reports():
    answers = iter([
        "1", "1", "SAM-101", "Городской самокат", "8", "1.4", "д",
        "3", "4", "5", "0",
    ])
    output = StringIO()
    fleet = Fleet()
    app = ConsoleApp(FleetService(fleet, AcceptAll()), input_fn=lambda _prompt: next(answers), output=output)

    app.run()

    result = output.getvalue()
    assert "SAM-101: транспорт принят" in result
    assert "Всего единиц на балансе: 1" in result
    assert "Суточное потребление: 1.40 кВт·ч" in result
    assert "Городской самокат [SAM-101]" in result


def test_console_can_add_item_and_handle_unknown_menu_command():
    answers = iter(["99", "2", "1", "HELM-1", "5", "0"])
    output = StringIO()
    fleet = Fleet()
    ConsoleApp(FleetService(fleet, AcceptAll()), input_fn=lambda _prompt: next(answers), output=output).run()

    assert "Неизвестная команда" in output.getvalue()
    assert len(fleet.assets) == 1
    assert fleet.assets[0].inventory_number == "HELM-1"
