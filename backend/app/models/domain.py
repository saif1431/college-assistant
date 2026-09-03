"""Internal domain types — shared by the graph and service layers.

Kept separate from `schemas/` (the API boundary) on purpose: the API
contract and the internal domain model are allowed to evolve independently.
"""

from enum import Enum


class Programme(str, Enum):
    COMPUTER_SCIENCE = "Computer Science"
    ELECTRICAL_ENGINEERING = "Electrical Engineering"
    MECHANICAL_ENGINEERING = "Mechanical Engineering"
    CIVIL_ENGINEERING = "Civil Engineering"
    CHEMICAL_ENGINEERING = "Chemical Engineering"
    SOFTWARE_ENGINEERING = "Software Engineering"


class QueryType(str, Enum):
    ACADEMIC = "academic"
    FEE = "fee"
    GENERAL = "general"
