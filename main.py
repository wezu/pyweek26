from panda3d.core import *
load_prc_file_data("", "sync-video 0")
load_prc_file_data("", "show-frame-rate-meter  1")
load_prc_file_data("", "default-model-extension .bam")
#load_prc_file_data("", "win-size 1280 720")
from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import *

from flow_chart import FlowChart

import level_gen

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.set_background_color(0, 0, 0)
        base.camLens.set_near_far(0.1, 50.0)
        base.disable_mouse()        
        base.camera.set_pos(0,0, 2.0)
        base.camera.set_hpr(90,0, 0)
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
        self.chart=FlowChart(self, plan, (0,0))
        base.accept('w', self.move)
        base.accept('a', self.rotate_left)
        base.accept('d', self.rotate_right)
        self.key_lock=False
        
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
        self.level, self.map = level_gen.generate_level(self.tileset, num_tiles=250, seed=2)
        self.level.reparent_to(render)
        #self.level.analyze()    
        print('ready!')
        
    def rotate_left(self):
        if self.key_lock:
            return
        self.key_lock=True
        h=base.camera.get_h()
        s=Sequence()
        s.append(LerpHprInterval(base.camera, 0.8, (h+72,-2,-4)))
        s.append(LerpHprInterval(base.camera, 0.2, (h+90,0,0)))       
        s.append(Wait(0.1))
        s.append(Func(self.unlock_keys))    
        s.start()        
        self.chart.move_left()
        
    def rotate_right(self): 
        if self.key_lock:
            return
        self.key_lock=True
        h=base.camera.get_h()
        s=Sequence()
        s.append(LerpHprInterval(base.camera, 0.8, (h-72,-2,4)))
        s.append(LerpHprInterval(base.camera, 0.2, (h-90,0,0)))       
        s.append(Wait(0.1))
        s.append(Func(self.unlock_keys))    
        s.start()
        self.chart.move_right()
    
    def can_move(self):
        pos=base.camera.get_pos(render)
        h=round(base.camera.get_h()%360)//90
        map_pos=(int(round(pos.x*0.1)), int(round(pos.y*0.1)))        
        forward_pos=(
                    (map_pos[0],map_pos[1]+1),
                    (map_pos[0]-1,map_pos[1]),
                    (map_pos[0],map_pos[1]-1),
                    (map_pos[0]+1,map_pos[1])
                    )[h]        
        #print(map_pos, h, forward_pos)
        test1=False
        test2=False
        if forward_pos in self.map:
            test1=map_pos in self.map[forward_pos]
            #print('self.map[forward_pos]', self.map[forward_pos])
        if map_pos in self.map:
            test2=forward_pos in self.map[map_pos]
            #print('self.map[map_pos]', self.map[map_pos])
        #print('Can move:',map_pos, test1 or test2)    
        #print('debug', map_pos, self.debug[map_pos])
        return test1 or test2
    
    def unlock_keys(self):
        self.key_lock=False
        
    def move(self):
        if self.key_lock:
            return
        if self.can_move():
            self.key_lock=True
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
            s.append(Wait(0.1))                
            s.append(Func(self.unlock_keys))    
            s.start()
            self.chart.move_up()

game = Game()
game.run()
