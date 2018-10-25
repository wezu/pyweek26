from panda3d.core import *
load_prc_file_data("", "sync-video 0")
load_prc_file_data("", "show-frame-rate-meter  1")
load_prc_file_data("", "default-model-extension .bam")
#load_prc_file_data("", "win-size 1280 720")
from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenImage import OnscreenImage

import random

from flow_chart import FlowChart
from sdf_text import SdfText
import level_gen

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.set_background_color(0, 0, 0)
        base.camLens.set_near_far(0.1, 50.0)
        base.disable_mouse()
        base.camera.set_pos(10,0, 2.0)
        base.camera.set_hpr(90,0, 0)

        self.font=loader.load_font('font/mono_font.egg')

        x=base.win.get_x_size()//2
        y=base.win.get_y_size()//2
        if x < 512:
            img=loader.load_texture('texture/logo_small.png')
            scale=(256, 0, 128)#img size//2
            self.logo = OnscreenImage(image = img, scale=scale, pos = (x, 0, -y+128), parent=pixel2d)
            self.logo.set_transparency(TransparencyAttrib.M_alpha)
        else:
            img=loader.load_texture('texture/logo_big.png')
            scale=(512, 0, 256)#img size//2
            self.logo = OnscreenImage(image = img, scale=scale, pos = (x, 0, -y+64), parent=pixel2d)
            self.logo.set_transparency(TransparencyAttrib.M_alpha)

        self.loading=SdfText(self.font)
        self.loading.frame=False
        self.loading.set_text_color((0.8, 0, 0, 1))
        self.loading.set_outline_color((0, 0, 0, 1))
        self.loading.set_outline_strength(1.0)
        self.loading.set_text('Loading...')
        self.loading.reparent_to(aspect2d)
        self.loading.set_pos(0,0,-0.75)
        self.loading.set_scale(0.1)

        base.graphicsEngine.render_frame()
        base.graphicsEngine.render_frame()
        base.graphicsEngine.render_frame()

        self.tutorial_chart={
                            'start':{'txt':'Do you understand flow charts?\n (use the keys written next to the lines)',
                                    'left':('No', 'inst_1',None),
                                    'right':('Yes','play', None)},
                            'play':{'txt':'Good, lets play!',
                                    'up':('Start game', None, self.start_game)},
                            'inst_1':{'txt':'Okay. You see the box labeled "Yes"? ',
                                    'right':('Yes', 'inst_2',None),
                                    'left':('No', 'inst_5',None)},
                            'inst_2':{'txt':'...and you can see the ones labeled "No"?',
                                        'right':('Yes', 'inst_3',None),
                                        'left':('No', 'inst_9',None)},
                            'inst_3':{'txt':'Good, there could be different labels but the principle is always the same.',
                                        'up':('Ok', 'start',None)},
                            'inst_4':{'txt':'Pressing the key shown next to the line will move you to that node',
                                        'up':('Ok', 'start',None)},
                            'inst_5':{'txt':'But you see the ones labeled "No"',
                                        'left':('No', 'inst_6',None),
                                        'right':('Yes', 'inst_8',None)},
                            'inst_6':{'txt':'Listen.',
                                        'left':('No', 'inst_7',self.troll),
                                        'right':('Ok...', 'play',None)},
                            'inst_7':{'txt':'I hate you.'},
                            'inst_8':{'txt':'Wait, What?',
                                        'up':('What?', 'start',None)},
                            'inst_9':{'txt':'But you just followed them twice!',
                                        'right':('Yes', 'inst_10',None),
                                        'left':('No', 'inst_10',None)},
                            'inst_10':{'txt':"(That wasn't a question.)",
                                        'up':('Screw it', 'inst_6',None)}
                            }


        self.current_chart=self.tutorial_chart
        self.current_chart_node='start'


        base.accept('w', self.move)
        base.accept('a', self.rotate_left)
        base.accept('d', self.rotate_right)
        self.key_lock=False

        self.tiles_description={
                                'wall':('You see a wall',),
                                (False,False,False):('You see a dead end',),
                                (False,True,False):('You see a tunel leading straight ahead',),
                                (True,False,False):('You see a tunel leading left',),
                                (False,False,True):('You see a tunel leading right',),
                                (True,True,False):('You see a tunel with a side passage going left',),
                                (False,True,True):('You see a tunel with a side passage going right',),
                                (True, False, True):('The tunel before you goes left and right',),
                                (True, True, True):('You came to a junction',)
                                }

        print('loading tiles...')
        self.set_loading_txt('Loading tiles...')
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
        self.set_loading_txt('Building level...')
        self.level, self.map = level_gen.generate_level(self.tileset, num_tiles=250, seed=2)
        #self.level.reparent_to(render)
        #self.level.analyze()
        print('ready!')
        self.set_loading_txt('')

        self.chart=FlowChart(self)
        self.chart.update()

    def troll(self):
        self.logo.hide()
        trollolo =loader.load_sfx("music/troll.ogg")
        trollolo.set_loop(True)
        trollolo.play()
        x=base.win.get_x_size()//2
        y=base.win.get_y_size()//2
        if x < 512:
            img=loader.load_texture('texture/troll_small.png')
            scale=(256, 0, 128)#img size//2
            troll_img = OnscreenImage(image = img, scale=scale, pos = (x, 0, -y+128), parent=pixel2d)
            troll_img.set_transparency(TransparencyAttrib.M_alpha)
        else:
            img=loader.load_texture('texture/troll_big.png')
            scale=(512, 0, 256)#img size//2
            troll_img = OnscreenImage(image = img, scale=scale, pos = (x, 0, -y+64), parent=pixel2d)
            troll_img.set_transparency(TransparencyAttrib.M_alpha)

    def set_loading_txt(self, txt):
        if txt:
            self.loading.set_text(txt)
            base.graphicsEngine.render_frame()
            base.graphicsEngine.render_frame()
            base.graphicsEngine.render_frame()
        else:
            self.loading.geom.hide()

    def start_game(self):
        self.logo.hide()
        self.current_chart=None
        self.level.reparent_to(render)
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

    def can_move(self, map_pos=None, h=None):
        if map_pos is None:
            pos=base.camera.get_pos(render)
            map_pos=(int(round(pos.x*0.1)), int(round(pos.y*0.1)))
        if h is None:
            h=round(base.camera.get_h()%360)//90
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

    def get_left_text(self):
        if self.current_chart is None:
            return 'Turn left'
        else:
            if 'left' in self.current_chart[self.current_chart_node]:
                last_node=self.current_chart_node
                return self.current_chart[last_node]['left'][0]
            else:
                return None

    def get_right_text(self):
        if self.current_chart is None:
            return 'Turn right'
        else:
            if 'right' in self.current_chart[self.current_chart_node]:
                last_node=self.current_chart_node
                return self.current_chart[last_node]['right'][0]
            else:
                return None

    def get_up_text(self):
        if self.current_chart is None:
            return 'Move forward'
        else:
            if 'up' in self.current_chart[self.current_chart_node]:
                last_node=self.current_chart_node
                return self.current_chart[last_node]['up'][0]
            else:
                return None

    def get_forward_text(self, direction=0, offset=1):
        if self.current_chart is None:
            pos=base.camera.get_pos(render)
            h=round(base.camera.get_h()%360)//90
            map_pos=(int(round(pos.x*0.1)), int(round(pos.y*0.1)))
            if direction ==0 and offset==2:
                if not self.can_move():
                    return random.choice(self.tiles_description['wall'])

                forward_pos=(
                        (map_pos[0],map_pos[1]+1),
                        (map_pos[0]-1,map_pos[1]),
                        (map_pos[0],map_pos[1]-offset),
                        (map_pos[0]+1,map_pos[1])
                        )[h]
                if not self.can_move(forward_pos, h):
                    return random.choice(self.tiles_description['wall'])

            h=(h+direction)%4
            forward_pos=(
                        (map_pos[0],map_pos[1]+offset),
                        (map_pos[0]-offset,map_pos[1]),
                        (map_pos[0],map_pos[1]-offset),
                        (map_pos[0]+offset,map_pos[1])
                        )[h]
            if forward_pos in self.map:
                if offset==1:
                    if not (map_pos in self.map[forward_pos] or forward_pos in self.map[map_pos]):
                        return random.choice(self.tiles_description['wall'])
                exits=(
                        self.can_move(forward_pos, (h+1)%4),
                        self.can_move(forward_pos, h),
                        self.can_move(forward_pos, (h-1)%4)
                        )
                return random.choice(self.tiles_description[exits])
            else:
                return random.choice(self.tiles_description['wall'])
        else:
            return self.current_chart[self.current_chart_node]['txt']

    def rotate_left(self):
        if self.key_lock:
            return
        self.key_lock=True
        if self.current_chart is None:
            h=base.camera.get_h()
            s=Sequence()
            s.append(LerpHprInterval(base.camera, 0.8, (h+72,-2,-4)))
            s.append(LerpHprInterval(base.camera, 0.2, (h+90,0,0)))
            s.append(Wait(0.1))
            s.append(Func(self.unlock_keys))
            s.start()
        else:
            if 'left' in self.current_chart[self.current_chart_node]:
                cmd=self.current_chart[self.current_chart_node]['left'][2]
                self.current_chart_node=self.current_chart[self.current_chart_node]['left'][1]
                if cmd:
                    cmd()
            else:
                self.key_lock=False
                return
            s=Sequence()
            s.append(Wait(1.1))
            s.append(Func(self.unlock_keys))
            s.start()
        self.chart.move_left()

    def rotate_right(self):
        if self.key_lock:
            return
        self.key_lock=True
        if self.current_chart is None:
            h=base.camera.get_h()
            s=Sequence()
            s.append(LerpHprInterval(base.camera, 0.8, (h-72,-2,4)))
            s.append(LerpHprInterval(base.camera, 0.2, (h-90,0,0)))
            s.append(Wait(0.1))
            s.append(Func(self.unlock_keys))
            s.start()
        else:

            if 'right' in self.current_chart[self.current_chart_node]:
                cmd=self.current_chart[self.current_chart_node]['right'][2]
                self.current_chart_node=self.current_chart[self.current_chart_node]['right'][1]
                if cmd:
                    cmd()
            else:
                self.key_lock=False
                return
            s=Sequence()
            s.append(Wait(1.1))
            s.append(Func(self.unlock_keys))
            s.start()

        self.chart.move_right()


    def move(self):
        if self.key_lock:
            return
        self.key_lock=True
        if self.current_chart is None:
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
        else:
            if 'up' in self.current_chart[self.current_chart_node]:
                cmd=self.current_chart[self.current_chart_node]['up'][2]
                self.current_chart_node=self.current_chart[self.current_chart_node]['up'][1]
                if cmd:
                    cmd()
            else:
                self.key_lock=False
                return
            s=Sequence()
            s.append(Wait(1.1))
            s.append(Func(self.unlock_keys))
            s.start()
        self.chart.move_up()

game = Game()
game.run()
