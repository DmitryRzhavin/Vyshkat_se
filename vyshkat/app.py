"""Запуск интерактивного консольного приложения."""

from .container import Container
from .console import ConsoleApp


def main() -> None:
    container = Container()
    ConsoleApp(container.fleet_service()).run()


if __name__ == "__main__":
    main()
