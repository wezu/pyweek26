from panda3d.core import *
load_prc_file_data("", "sync-video 1")
load_prc_file_data("", "show-frame-rate-meter  0")
load_prc_file_data("", "default-model-extension .bam")
load_prc_file_data("", "win-size 1280 720")
from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import *

from flow_chart import FlowChart

import level_gen

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.disable_mouse()
        base.set_background_color(0, 0, 0)
        #base.camLens.set_near_far(0.01, 500.0)
        base.camera.set_pos(0,0, 2.0)
        base.camera.set_hpr(90,0, 0)
        #base.cam.look_at(0,0,0)
        '''
        0,0   0,1   0,2
        1,0   1,1   1,2
        2,0   2,1   2,2
        '''
        plan={
               (0,0):'You are at 0,0',
               (0,1):'You are at 0,1',
               (0,2):'You are at 0,2',
               (1,0):'You are at 1,0',
               (1,1):'You are at 1,1',
               (1,2):'You are at 1,2',
               (2,0):'You are at 2,0',
               (2,1):'You are at 2,1',
               (2,2):'You are at 2,2'
               }
        self.chart=FlowChart(plan, (0,1))
        base.accept('w', self.move)
        base.accept('a', self.rotate_left)
        base.accept('d', self.rotate_right)

        print('loading tiles...')
        self.tileset=level_gen.Tileset('model/tile/dungeon_')
        self.tileset.add_tile('wne_0', 8)
        self.tileset.add_tile('we_0', 1)
        self.tileset.add_tile('ne_0', 1)
        self.tileset.add_tile('wn_0', 1)
        self.tileset.add_tile('e_0', 5)
        self.tileset.add_tile('w_0', 5)
        self.tileset.add_tile('n_0', 20)
        self.tileset.add_wall('wall')
        print('building level...')
        self.level=level_gen.generate_level(self.tileset, num_tiles=250, seed=2)
        self.level.reparent_to(render)
        #self.level.analyze()
        print('ready!')

    def rotate_left(self):
        h=base.camera.get_h()+90
        LerpHprInterval(base.camera, 1.0, (h,0,0)).start()
        self.chart.move_left()

    def rotate_right(self):
        h=base.camera.get_h()-90
        LerpHprInterval(base.camera, 1.0, (h,0,0)).start()
        self.chart.move_right()

    def move(self):
        pos=base.camera.get_pos(render)
        h=round(base.camera.get_h()%360)//90
        x,y=((0,2), (-2,0), (0,-2), (2,0))[h]
        s=Sequence()
        for i in range(5):
            if i==4:
                z=0
            elif i%2:
                z=0.1
            else:
                z=-0.1
            s.append(LerpPosInterval(base.camera, 0.2, pos+Point3(x*(i+1), y*(i+1), z)))

        s.start()
        self.chart.move_up()

game = Game()
game.run()
