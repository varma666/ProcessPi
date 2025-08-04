from abc import ABC, abstractmethod
class Component(ABC):
    """
    Base class for a chemical component.
    Each subclass must define its own physical and chemical properties.
    """

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def formula(self):
        pass

    @property
    @abstractmethod
    def molecular_weight(self):
        pass

    @abstractmethod
    def density(self, temperature: float) -> float:
        """Return density in kg/m3 as a function of temperature in °C"""
        pass

    @abstractmethod
    def specific_heat(self, temperature: float) -> float:
        """Return specific heat in kJ/kg.K as a function of temperature in °C"""
        pass