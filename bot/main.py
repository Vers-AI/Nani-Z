from typing import Optional
from ares import AresBot
from ares.behaviors.combat import CombatManeuver
from ares.behaviors.combat.individual import (
    AMove,
    PathUnitToTarget,
    StutterUnitBack,
)

from sc2.ids.unit_typeid import UnitTypeId
from sc2.units import Units

import numpy as np


class MyBot(AresBot):
    combat_manager = None

    def __init__(self, game_step_override: Optional[int] = None):
        """Initiate custom bot

        Parameters
        ----------
        game_step_override :
            If provided, set the game_step to this value regardless of how it was
            specified elsewhere
        """
        super().__init__(game_step_override)

    async def on_step(self, iteration: int) -> None:
        # retrieves zergling and roaches
        zerling: Units = self.units(UnitTypeId.ZERGLING)
        roaches: Units = self.units(UnitTypeId.ROACH)

        # define targets and grids
        enemy_units: Units = self.enemy_units
        ground_grid: np.ndarray = self.mediator.get_ground_grid

        # execute manuevers
        self.do_zergling_engagement(zerling, enemy_units, ground_grid)
        self.do_roach_pylon_attack(roaches, ground_grid)

    def do_zergling_engagement(
        self,
        zergling: Units,
        enemies: Units,
        grid: np.ndarray,
    ) -> None:
        """Engage enemy units with zergling

        Parameters
        ----------
        units :
            zergling to engage with
        enemies :
            Enemy units to engage
        grid :
            Grid of the ground
        """
        zergling_maneuver = CombatManeuver = CombatManeuver()
        # engage enemy and retreat if needed
        zergling_maneuver.add(StutterUnitBack(units=zergling, grid=grid))
        zergling_maneuver.add(AMove(units=zergling, targets=enemies))
        self.register_behavior(zergling_maneuver)

    def do_roach_pylon_attack(
        self,
        roaches: Units,
        grid: np.ndarray,
    ) -> None:
        """Attack enemy pylons with roaches

        Parameters
        ----------
        units :
            Roaches to attack with
        grid :
            Grid of the ground
        """
        roach_maneuver = CombatManeuver = CombatManeuver()
        # attack enemy pylons and retreat if needed
        roach_maneuver.add(
            PathUnitToTarget(
                units=roaches,
                grid=grid,
                target=self.enemy_structures(UnitTypeId.PYLON).first.position,
            )
        )

        self.register_behavior(roach_maneuver)
