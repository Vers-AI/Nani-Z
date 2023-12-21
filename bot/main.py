from typing import Optional
from ares import AresBot
from ares.behaviors.combat import CombatManeuver
from ares.cython_extensions.combat_utils import cy_pick_enemy_target
from ares.cython_extensions.units_utils import cy_closest_to
from ares.behaviors.combat.individual import (
    AMove,
    PathUnitToTarget,
    StutterUnitBack,
    AttackTarget,
)

from sc2.ids.unit_typeid import UnitTypeId
from sc2.units import Units
from sc2.unit import Unit
from sc2.position import Point2

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
        print(f"Game Loop Iteration: {iteration}")
        # retrieves zergling and roaches
        zerglings = self.units(UnitTypeId.ZERGLING)
        roaches = self.units(UnitTypeId.ROACH)

        # define targets and grid
        enemy_units = self.enemy_units
        ground_grid = np.ndarray = self.mediator.get_ground_grid

        # call the engagement for zergling and pylon attack for roaches
        self.do_zergling_engagement(zerglings, enemy_units, ground_grid)
        self.do_roach_pylon_attack(roaches, ground_grid) 
        
    
    def do_zergling_engagement(
        self,
        zerglings: Units,
        enemies: Units,
        grid: np.ndarray,
    ):
        print(f"Executing do_zergling_engagement with {len(zerglings)} zerglings")
        # map center as teh default A-move target
        target = self.game_info.map_center

        """Engage enemy units with zerglings and use stutter step behavior.

        Parameters
        ----------
        zerglings : Units
            Zerglings to engage with.
        enemies : Units
            Enemy units to engage.
        grid : np.ndarray
            The ground grid for pathing information.
        """
        print(enemies)
        for zergling in zerglings:
            zergling_maneuver = CombatManeuver()

            # If there are enemies, find the closest one and stutter step towards it
            if enemies:
                closest_enemy: Unit = cy_closest_to(zergling.position, enemies)  # Use zergling.position
                if closest_enemy:
                    zergling_maneuver.add(StutterUnitBack(zergling, closest_enemy))
                    
                    zergling_maneuver.add(AMove(zergling, target))
                    self.register_behavior(zergling_maneuver)

    def do_roach_pylon_attack(
        self,
        roaches: Units,
        grid: np.ndarray,
    ):
        print(f"Executing do_roach_pylon_attack with {len(roaches)} roaches")
        """Direct roaches to move towards the enemy start location and attack the pylon once in range.

        Parameters
        ----------
        roaches : Units
            Roaches to perform the attack.
        grid : np.ndarray
            The ground grid for pathing information.
        """
        enemy_start_location = self.enemy_start_locations[0]
        enemy_pylon = self._find_enemy_pylon()

        for roach in roaches:
            roach_maneuver = CombatManeuver()
            # Path to the enemy start location
            roach_maneuver.add(
                PathUnitToTarget(
                    roach, grid, enemy_start_location, success_at_distance=5.0
                )
            )

            # If a pylon is found, attack it
            if enemy_pylon:
                roach_maneuver.add(AttackTarget(roach, enemy_pylon))

            self.register_behavior(roach_maneuver)

    def _find_enemy_pylon(self) -> Unit:
        """Find the enemy pylon to target."""
        pylons = self.enemy_structures(UnitTypeId.PYLON)
        if pylons:
            return pylons.closest_to(self.enemy_start_locations[0])
        return None
