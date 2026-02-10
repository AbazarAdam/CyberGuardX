"""Services package for CyberGuardX."""
from .breach_checker import get_breach_checker, BreachCheckerService

__all__ = ["get_breach_checker", "BreachCheckerService"]
