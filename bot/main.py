from typing import Optional
from ares import AresBot
from ares.behaviors.combat import CombatManeuver
from ares.cython_extensions.units_utils import cy_closest_to
from ares.behaviors.combat.individual import (
    AMove,
    PathUnitToTarget,
    StutterUnitBack,
)

from sc2.ids.unit_typeid import UnitTypeId
from sc2.units import Units

import numpy as np
from sc2.units import Units


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

    async def on_step(self, iteration: int):
        
        # retrieves zergling and roaches
        zerglings = self.units(UnitTypeId.ZERGLING)
        roaches = self.units(UnitTypeId.ROACH)

        #define targets and grid
        enemy_units = self.enemy_units
        ground_grid = np.ndarray = self.game_info.pathing_grid

      #call the engagement for zergling and pylon attack for roaches
        self.do_zergling_engagement(zerglings, enemy_units, ground_grid)
        self.do_roach_pylon_attack(roaches, enemy_units, ground_grid) 
        
    
    def do_zergling_engagement(
        self,
        zergling: Units,
        enemies: Units,
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
        zergling_maneuver: CombatManeuver = CombatManeuver()
        # engage enemy and retreat if needed
        zergling_maneuver.add(StutterUnitBack(unit=zergling, target=enemies))
        zergling_maneuver.add(AMove(unit=zergling, target=enemies))
        self.register_behavior(zergling_maneuver)

    def do_roach_pylon_attack(
        self,
        roaches: Units,
        grid: np.ndarray,
    ) -> None:
        """Attack move towards the enemy pylon and when it sees it prioritize it"""
        roach_maneuver: CombatManeuver = CombatManeuver()
        # move towards the enemy and once it sees the pylon prioritize it
        roach_maneuver.add(
            PathUnitToTarget(
                unit=roaches,
                grid=grid,
                target=self.enemy_start_locations[0],
                success_at_distance=5.0,
            )
        )
        # roach_maneuver.add(AttackTarget(unit=roaches, target=self.enemy_structures.first))

        self.register_behavior(roach_maneuver)
