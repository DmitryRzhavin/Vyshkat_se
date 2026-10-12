"""Точка сборки зависимостей приложения."""

from dependency_injector import containers, providers

from .services import DefaultServiceCenter, Fleet, FleetService


class Container(containers.DeclarativeContainer):
    fleet = providers.Singleton(Fleet)
    service_center = providers.Factory(DefaultServiceCenter)
    fleet_service = providers.Factory(
        FleetService,
        fleet=fleet,
        service_center=service_center,
    )
