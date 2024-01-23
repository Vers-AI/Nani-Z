from typing import Optional
from ares.consts import UnitRole
from ares import AresBot
from ares.behaviors.combat import CombatManeuver
from ares.cython_extensions.units_utils import cy_closest_to, cy_distance_to
from ares.behaviors.combat.individual import (
    AMove,
    PathUnitToTarget,
    StutterUnitBack,
    AttackTarget,
)

from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units

import numpy as np

class MyBot(AresBot):
    combat_manager = None

    def __init__(self, game_step_override: Optional[int] = None):
        
        super().__init__(game_step_override)
        
        #add attribute to remember assigning zergling harass
        self._assigned_ling_harass: bool = False

    async def on_step(self, iteration: int):
        await super(MyBot, self).on_step(iteration)
        # retrieves zergling and roaches
        zerglings = self.units(UnitTypeId.ZERGLING)
        roaches = self.units(UnitTypeId.ROACH)

        #defines the role of the units
        zergling_roach_force = Units = self.mediator.get_units_from_role(role=UnitRole.ATTACKING)
        zergling_harass_force = Units = self.mediator.get_units_from_role(role=UnitRole.HARASSING)


        # define targets and grid
        enemy_units = self.enemy_units
        ground_grid = self.mediator.get_ground_grid

        # call the pylon attack for zergling and engagement for roaches
        self.do_zergling_pylon_attack(zerglings, ground_grid)
        self.do_roach_engagement(roaches, enemy_units, ground_grid)

    def do_zergling_pylon_attack(self, zerglings: Units, grid: np.ndarray):
        enemy_pylon = self._close_enemy_pylon()
        enemy_start_location = self.enemy_start_locations[0]

        for zergling in zerglings:
            zergling_maneuver = CombatManeuver()
            if enemy_pylon and cy_distance_to(zergling.position, enemy_pylon.position) < 15.0:
                zergling_maneuver.add(AttackTarget(zergling, enemy_pylon))
            else:
                zergling_maneuver.add(PathUnitToTarget(zergling, grid, enemy_start_location, success_at_distance=5.0))
            self.register_behavior(zergling_maneuver)

    def do_roach_engagement(self, roaches: Units, enemies: Units, grid: np.ndarray):
        for roach in roaches:
            roach_maneuver = CombatManeuver()
            if enemies:
                closest_enemy: Unit = cy_closest_to(roach.position, enemies)
                roach_maneuver.add(StutterUnitBack(roach, closest_enemy))
            else:
                roach_maneuver.add(AMove(roach, self.game_info.map_center))
            self.register_behavior(roach_maneuver)

    def _close_enemy_pylon(self) -> Unit:
        pylons = self.enemy_structures(UnitTypeId.PYLON)
        if pylons:
            return pylons.closest_to(self.game_info.map_center)
        return None
