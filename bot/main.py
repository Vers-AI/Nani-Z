from typing import Optional
from ares import AresBot
from ares.behaviors.combat_manager import CombatManuever
from ares.behaviors.combat.individual import (
    EngageEnemy,
    PathUnitToTarget,
    Retreat,
)

from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Units
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
        # retrieves zerlings and roaches
        zerling: Units = self.units(UnitTypeId.ZERGLING)
        roaches: Units = self.units(UnitTypeId.ROACH)

        # define targets and grids
        enemy_units: Units = self.enemy_units
        ground_grid: np.ndarray = self.mediator.get_ground_grid

        # execute manuevers
        self.do_zerling_engagement(zerling, enemy_units, ground_grid)
        self.do_roach_pylon_attack(roaches, ground_grid)

        def do_zerling_engagement (
            self,
            zerlings: Units,
            enemies: Units,
            grid: np.ndarray,
        ) -> None:
            """Engage enemy units with zerlings

            Parameters
            ----------
            units :
                Zerlings to engage with
            enemies :
                Enemy units to engage
            grid :
                Grid of the ground
            """
            zerling_maneuver = CombatManuever = CombatManuever()
            # engage enemy and retreat if needed
            zergling_maneuver.add(EngageEnemy(units=zerlings, targets=enemies))
            zergling_maneuver.add(Retreat(units=zerlings, grid=grid))
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
                roach_maneuver = CombatManuever= CombatManuever()
                # attack enemy pylons and retreat if needed
                roach_maneuver.add(
                    PathUnitToTarget(
                        units=roaches,
                        grid=grid,
                        target=self.enemy_structures(UnitTypeId.PYLON).first.position
                    )
                )

                self.register_behavior(roach_maneuver)
                
                


        
        

     