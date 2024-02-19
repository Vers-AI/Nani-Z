from typing import Optional
from ares.consts import UnitRole
from ares import AresBot
from ares.behaviors.combat import CombatManeuver
from cython_extensions import cy_closest_to, cy_distance_to
from ares.behaviors.combat.individual import (
    AMove,
    PathUnitToTarget,
    StutterUnitBack,
    AttackTarget,
)

from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2

import numpy as np

class MyBot(AresBot):
    combat_manager = None
    ZERG_UNIT_TYPE: set[UnitTypeId] = { UnitTypeId.ZERGLING, UnitTypeId.ROACH }


    def __init__(self, game_step_override: Optional[int] = None):
        
        super().__init__(game_step_override)
        
        #add attribute to remember assigning zergling harass
        self._assigned_harass_force: bool = False

    async def on_step(self, iteration: int):
        await super(MyBot, self).on_step(iteration)

        # define targets and grid
        enemy_units = self.enemy_units
        ground_grid = self.mediator.get_ground_grid

        #retrieve units based on the role of the unit
        main_attack_force = Units = self.mediator.get_units_from_role(role=UnitRole.ATTACKING)
        zergling_roach_harass_force = Units = self.mediator.get_units_from_role(role=UnitRole.HARASSING)

        #if we have a zergling attack force, assign it to harass
        if main_attack_force:
            if not self._assigned_harass_force:
                self._assign_harass_force(main_attack_force)
                self._assigned_harass_force = True

            attack_target =  self.enemy_start_locations[0]
            self._main_army_attack(main_attack_force, attack_target, ground_grid)
                
        if zergling_roach_harass_force:
            self._micro_army_harassers(zergling_roach_harass_force, enemy_units, ground_grid)  

    
    
    async def on_unit_created(self, unit: Unit) -> None:
        await super(MyBot, self).on_unit_created(unit)

        # assign all units to ATTACKING role by default
        if unit.type_id in self.ZERG_UNIT_TYPE:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.ATTACKING
            )
    # assign the zergling attack force to the harass role
    def _assign_harass_force(self, main_attack_force: Units) -> None:
         # get all roaches from our force
        roaches: list[Unit] = [u for u in main_attack_force if u.type_id == UnitTypeId.ROACH]

        # iterate through all roaches and assign them to the harass role
        for roach in roaches:
            self.mediator.assign_role(tag=roach.tag, role=UnitRole.HARASSING)
        # get all zerglings from our force
        zerglings: list[Unit] = [u for u in main_attack_force if u.type_id == UnitTypeId.ZERGLING]
        # iterate through zerglings
        for i, zergling in enumerate(zerglings):
            # if the zergling is even, assign it to the harass role
            if i % 2 == 0:
                self.mediator.assign_role(tag=zergling.tag, role=UnitRole.HARASSING)

    
    
    def _main_army_attack(self, main_attack_force: Unit, attack_target: Point2, ground_grid: np.ndarray) -> None:
        enemy_pylon = self._close_enemy_pylon()
        enemy_start_location = self.enemy_start_locations[0]

        for Unit in main_attack_force:
            main_maneuver = CombatManeuver()
            # avoid the enemy units to attack the pylons
            if enemy_pylon and cy_distance_to(Unit.position, enemy_pylon.position) < 15.0:
                main_maneuver.add(AttackTarget(Unit, enemy_pylon))
            else:
                main_maneuver.add(PathUnitToTarget(Unit, ground_grid, attack_target, success_at_distance=5.0))
            self.register_behavior(main_maneuver)
            

    def _micro_army_harassers(self, zergling_roach_harass_force: Units, enemy_units: Units, ground_grid: np.ndarray) -> None:
        for unit in zergling_roach_harass_force:
            # attack the enemy start location unless near an enemy then stutter step back using combat maneuver
            harrass_maneuvers = CombatManeuver()
            if enemy_units:
                closet_enemy: Unit = cy_closest_to(unit.position, enemy_units)
                harrass_maneuvers.add(StutterUnitBack(unit, closet_enemy))
            else:
                harrass_maneuvers.add(AMove(unit, self.enemy_start_locations[0]))
            self.register_behavior(harrass_maneuvers)
            
    def _close_enemy_pylon(self) -> Unit:
        pylons = self.enemy_structures(UnitTypeId.PYLON)
        if pylons:
            return pylons.closest_to(self.game_info.map_center)
        return None