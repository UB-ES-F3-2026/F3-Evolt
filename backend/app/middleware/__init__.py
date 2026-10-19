"""Middleware de l'aplicació (T08.2)."""

from app.middleware.simulation import (
    SimulationMiddleware,
    SimulationSettings,
    load_simulation_settings,
)

__all__ = [
    "SimulationMiddleware",
    "SimulationSettings",
    "load_simulation_settings",
]
