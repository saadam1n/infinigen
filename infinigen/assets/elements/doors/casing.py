# Copyright (c) Princeton University.

# Authors: Lingjie Mei
import bpy
import numpy as np
from numpy.random import uniform

from infinigen.assets.materials import wood, metal
from infinigen.assets.utils.decorate import read_edge_center, read_edge_direction
from infinigen.assets.utils.mesh import bevel
from infinigen.assets.utils.object import new_cube
from infinigen.core.constraints.example_solver.room import constants
from infinigen.core.placement.factory import AssetFactory

from infinigen.core.util import blender as butil
from infinigen.core.util.math import FixedSeed


class DoorCasingFactory(AssetFactory):
    def __init__(self, factory_seed, coarse=False):
        super(DoorCasingFactory, self).__init__(factory_seed, coarse)
        with FixedSeed(self.factory_seed):
            self.extrude = uniform(.02, .08)
            self.bevel_all_sides = uniform() < .3
            self.surface = np.random.choice([metal, wood])
            self.metal_color = metal.sample_metal_color()

    def create_asset(self, **params) -> bpy.types.Object:
        obj = new_cube()
        obj.location = 0, 0, 1
        butil.apply_transform(obj, True)
        w = constants.DOOR_WIDTH
        s = constants.DOOR_SIZE
        obj.scale = w / 2 + self.margin, constants.WALL_THICKNESS / 2 + self.extrude, \
            s / 2 + self.margin / 2
        butil.apply_transform(obj)
        cutter = new_cube()
        cutter.location = 0, 0, 1 - 1e-3
        butil.apply_transform(cutter, True)
        cutter.scale = w / 2 - 1e-3, constants.WALL_THICKNESS + self.extrude, s / 2
        butil.apply_transform(cutter)
        butil.modify_mesh(obj, 'BOOLEAN', object=cutter, operation='DIFFERENCE')
        butil.delete(cutter)

        x, y, z = read_edge_center(obj).T
        x_, y_, z_ = read_edge_direction(obj).T

        if self.bevel_all_sides:
            selection = (np.abs(z_) > .5) | (np.abs(x_) > .5)
        else:
            selection = ((np.abs(z_) > .5) & (np.abs(x) < w / 2 + self.margin / 2)) | (
                (np.abs(x_) > .5) & (z < s + self.margin / 2))
        obj.data.edges.foreach_set('bevel_weight', selection)
        bevel(obj, self.extrude, limit_method='WEIGHT')
        return obj

    def finalize_assets(self, assets):
        self.surface.apply(assets, metal_color=self.metal_color)
