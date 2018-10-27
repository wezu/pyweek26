from panda3d.core import *
load_prc_file('options.prc')
load_prc_file_data('','framebuffer-srgb 0')
load_prc_file_data('','textures-power-2 None')
load_prc_file_data("", "default-model-extension .bam")

from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.actor.Actor import Actor

import random
import builtins

from flow_chart import FlowChart
from sdf_text import SdfText
import level_gen
from deferred_render import *
from options import Options

#set the window decoration before we start
wp = WindowProperties.getDefault()
wp.set_title("Chart of Flowrock, PyWeek 26  wezu.dev@gmail.com")
wp.set_icon_filename('texture/icon.ico')
WindowProperties.setDefault(wp)

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.set_background_color(0, 0, 0)
        #base.camLens.set_near_far(0.1, 50.0)
        base.disable_mouse()
        base.camera.set_pos(10,0, 1.8)
        base.camera.set_hpr(90,-5, 0)
        self.potato_mode=ConfigVariableBool('potato-mode', False).get_value()

        if not self.potato_mode:
            options=Options('presets/minimal.ini')
            DeferredRenderer(**options.get())
            #set some other options...
            deferred_renderer.set_near_far(0.01,50.0)
            deferred_renderer.set_cubemap('texture/cube/sky_#.png')
        else:
            base.camLens.set_near_far(0.01, 50.0)
            deferred_render=render
            builtins.deferred_render = render

        self.font=loader.load_font('font/mono_font')

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
                                    'right':('Yes','setup', None)},
                            'setup':{'txt':'Good, lets play!',
                                    'up':('Setup', 'setup_quality', None)},
                            'play':{'txt':'All done, lets play!',
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
                                        'right':('Ok...', 'inst_1',None)},
                            'inst_7':{'txt':'I hate you.',
                                      'left':('Troll', 'inst_7',None),
                                       'right':('lolol', 'inst_7',None)},
                            'inst_8':{'txt':'Wait, What?',
                                        'up':('What?', 'start',None)},
                            'inst_9':{'txt':'But you just followed them twice!',
                                        'right':('Yes', 'inst_10',None),
                                        'left':('No', 'inst_10',None)},
                            'inst_10':{'txt':"(That wasn't a question.)",
                                        'up':('Screw it', 'inst_6',None)},
                            'setup_quality':{'txt':'Select the graphic quality level (check options.prc for more options).',
                                            'left':('Bad','setup_shadows', self.quality_minimal),
                                            'up':('Best','setup_shadows', self.quality_full),
                                            'right':('Medium','setup_shadows', self.quality_medium),
                                            },
                            'setup_shadows':{'txt':'Do you want shadows? (may cause problems)',
                                            'left':('No','play', self.no_shadows ),
                                            'right':('Yes','play', self.use_shadows),
                                            },
                            'potato':{'txt':'You are in Potato Mode - no shaders, no light, no effects. Set "potato-mode 0" in options.prc to enable shaders',
                                    'up':('Ok.','play', None)}
                            }

        if self.potato_mode:
            self.tutorial_chart['setup_quality']=self.tutorial_chart['potato']

        self.zombi_state='idle'

        self.combat_chart={'start':{'txt':'Your turn. What do you want to do?',
                            'left':('Stab','result',self.stab),
                            'right':('Slash','result',self.slash),
                            'up':('Block','result',self.block)},

                           'zombie_turn':{'txt':'Enemy turn.',
                                        'up':('OK', 'start', None)
                                        },
                            'result':{'txt':'inser text',
                                    'up':('OK.','zombie_turn',self.zombie_turn )}
                           }

        self.current_chart=self.tutorial_chart
        self.current_chart_node='start'


        base.accept('w', self.move)
        base.accept('a', self.rotate_left)
        base.accept('d', self.rotate_right)

        self.bias=0.0035
        base.accept('=', self.set_bias,[0.0001])
        base.accept('-', self.set_bias,[-0.0001])


        self.key_lock=0
        self.block=False

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
        self.set_loading_txt('Loading actors...')

        #self.zombie=loader.load_model('actor/m_zombie',)

        self.zombie= Actor('actor/m_zombie',
                          {'idle':'actor/a_zombie_idle',
                          'interrupt':'actor/a_zombie_interrupt',
                          'ready':'actor/a_zombie_ready',
                          'stabbed':'actor/a_zombie_stabbed',
                          'strike':'actor/a_zombie_strike',
                          'block':'actor/a_zombie_block',
                          'die':'actor/a_zombie_die',
                          'attack':'actor/a_zombie_attack'})
        self.zombie.set_hpr(90, 0, 0)
        self.zombie.set_scale(0.03)
        self.zombie.loop('idle')
        if not self.potato_mode:
            self.zombie.set_blend(frameBlend = True)
            attr = ShaderAttrib.make(Shader.load(Shader.SLGLSL, 'shader/actor_v.glsl', 'shader/geometry_f.glsl'))
            attr = attr.setFlag(ShaderAttrib.F_hardware_skinning, True)
            self.zombie.set_attrib(attr)
            loader._setTextureInputs(self.zombie)
        self.zombie.set_transparency(TransparencyAttrib.MNone, 1)

        self.sword=loader.load_model('actor/m_sword')
        self.sword= Actor('actor/m_sword',
                          {'idle':'actor/a_sword_idle',
                          'stab':'actor/a_sword_stab',
                          'slash':'actor/a_sword_slash',
                          'block':'actor/a_sword_block',
                          })
        if not self.potato_mode:
            self.sword.set_attrib(attr)
            loader._setTextureInputs(self.sword)
            self.sword.set_transparency(TransparencyAttrib.MNone, 1)

        self.set_loading_txt('Loading models...')
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
        self.level, self.map = level_gen.generate_level(self.tileset, num_tiles=250, seed=33)
        #self.level.reparent_to(render)
        #self.level.analyze()
        print('ready!')
        self.set_loading_txt('Loading music...')
        self.menu_music=loader.load_music('music/violin_drums.ogg')
        self.menu_music.set_loop(True)
        self.game_music=loader.load_music('music/oppressive_gloom.ogg')
        self.game_music.set_loop(True)
        self.combat_music=loader.load_music('music/oppressive_gloom.ogg')
        self.combat_music.set_loop(True)
        self.set_loading_txt('Loading sounds...')
        self.sounds={'footsteps':loader.load_sfx('sound/footsteps.ogg'),
                     'turn':loader.load_sfx('sound/turn.ogg'),
                     'click':loader.load_sfx('sound/click.ogg'),
                     'zombie_attack':loader.load_sfx('sound/zombie-attack1.ogg'),
                     'zombie_attack_hit':loader.load_sfx('sound/zombie-attack-hit.ogg'),
                     'zombie_attack_block':loader.load_sfx('sound/zombie-attack-block.ogg'),
                     'block':loader.load_sfx('sound/block.ogg'),
                     'stab':loader.load_sfx('sound/stab.ogg'),
                     'stab_hit':loader.load_sfx('sound/stab-hit.ogg'),
                     'slash':loader.load_sfx('sound/slash-hit.ogg'),
                    }
        self.set_loading_txt('')


        base.musicManager.setVolume(0.5)

        self.chart=FlowChart(self)
        self.chart.update()
        self.menu_music.play()


        #print(self.map)
        self.zombie_map=set()

        #find a place to put the zombie in
        for x,y in ((0,1), (0,-1), (1,0), (-1,0)):
            if (x,y) in self.map:
                for (z,w) in ((x,y+1), (x,y-1), (x+1,y), (x-1,y)):
                    if (z,w) in self.map and (z,w)!=(x,y) and (z,w)!=(0,0):
                        print(z,w, ' zombie can go here!')
                        self.zombie.set_pos(z*10, w*10, 0)
                        self.zombie_map.add((z,w))
                        break

        self.accept('tab', base.bufferViewer.toggleEnable)
        self.accept('9',aspect2d.hide)
        self.accept('0',aspect2d.show)

    def zombie_turn(self):
        if self.zombi_state == 'recover':
            self.zombi_anim('idle')
            self.combat_chart['zombie_turn']['txt']='After your attack the zombie takes no action.'
            self.zombi_state = 'idle'
            return

        if self.zombi_state == 'ready':
            self.zombi_anim('strike')
            if self.block:
                self.sounds['zombie_attack_block'].play()
                self.sword_anim('block', 0.1)
                self.block=False
                self.combat_chart['zombie_turn']['txt']='The zombie attacks, you try to block, but the attack is just too powerful - it still hurts.'
            else:
                self.combat_chart['zombie_turn']['txt']='The zombie delivers a powerful attacks. It hurts!'
            self.zombi_state = 'idle'
            return

        r=random.randint(0,1)
        if r==0: #charge attack
            self.zombi_anim('ready', hold=True)
            self.combat_chart['zombie_turn']['txt']='The zombie gets ready for a powerful attack!'
            self.zombi_state = 'ready'
        elif r==1: #quick attack
            self.zombi_anim('attack', rate=1.8)
            if self.block:
                self.sounds['zombie_attack_block'].play()
                self.sword_anim('block',0.2)
                self.block=False
                self.combat_chart['zombie_turn']['txt']='The zombie attacks, but you are ready and block its attack.'
            else:
                self.sounds['zombie_attack_hit'].play()
                self.combat_chart['zombie_turn']['txt']='The zombie attacks!'
        else: #idle
            self.zombi_anim('idle')
            self.combat_chart['zombie_turn']['txt']='The zombie takes no action.'

    def stab(self):
        self.block=False
        self.key_lock+=1
        self.sword_anim('stab')
        if self.zombi_state == 'ready':
            self.sounds['stab'].play()
            self.sounds['zombie_attack_hit'].play()
            self.zombi_anim('strike')
            self.combat_chart['result']['txt']="You stabbed the zombie, but that did not stop the zombies attack!"
            self.zombi_state = 'recover'
        else:
            self.sounds['stab_hit'].play()
            self.zombi_anim('stabbed', 0.2)
            self.combat_chart['result']['txt']='You stabbed the zombie! It is not happy.'

    def slash(self):
        self.block=False
        self.key_lock+=1
        self.sword_anim('slash')
        if self.zombi_state == 'ready':
            self.zombi_anim('interrupt', 0.8)
            self.sounds['slash'].play()
            self.combat_chart['result']['txt']="You strike the zombie knocking it off balance!"
            self.zombi_state = 'recover'
        elif self.zombi_state == 'idle':
            self.sounds['block'].play()
            self.zombi_anim('block', 0.2)
            self.combat_chart['result']['txt']='You try to strike the zombie, but it blocks easily.'
        else:
            self.zombi_anim('interrupt')
            self.combat_chart['result']['txt']='You strike the zombie'

    def block(self):
        self.block=True
        self.combat_chart['result']['txt']='You get ready to block.'
        #self.sword_anim('block')

    def sword_anim(self, anim, delay=0.0):
        s=Sequence(Wait(delay), self.sword.actorInterval(anim, playRate=1.3), Func(self.sword.loop, 'idle'))
        s.start()

    def zombi_anim(self, anim, delay=0.0, rate=1.0, hold=False):
        if anim == 'idle':
            self.zombie.loop('idle')
        else:
            s=Sequence(Wait(delay),
                      self.zombie.actorInterval(anim, playRate=rate),
                      Func(self.unlock_keys))
            if not hold:
                s.append(Func(self.zombie.loop, 'idle'))
            s.start()

    def no_shadows(self):
        if not self.potato_mode:
            #point light, attached to camera
            self.light_1 = SphereLight(color=(0.6,0.4,0.2), pos=(0,0,3), radius=25.0, shadow_size=0, shadow_bias=0.0035)
            self.light_1.attach_to(base.camera, Point3(-2.0, 2.0, 0.5))
            taskMgr.add(self.update, 'main_update_tsk')

    def use_shadows(self):
        if not self.potato_mode:
            #point light, attached to camera
            self.light_1 = SphereLight(color=(0.6,0.4,0.2), pos=(0,0,3), radius=25.0, shadow_size=512, shadow_bias=0.0035)
            self.light_1.attach_to(base.camera, Point3(-2.0, 2.0, 0.5))
            taskMgr.add(self.update, 'main_update_tsk')

    def quality_minimal(self):
        if not self.potato_mode:
            options=Options('presets/minimal.ini')
            deferred_renderer.reset_filters(**options.get())

    def quality_full(self):
        if not self.potato_mode:
            options=Options('presets/full.ini')
            deferred_renderer.reset_filters(**options.get())

    def quality_medium(self):
        if not self.potato_mode:
            options=Options('presets/medium.ini')
            deferred_renderer.reset_filters(**options.get())

    def update(self, task):
        self.sword.set_pos(base.camera.get_pos(render))
        h=base.camera.get_h(render)
        self.sword.set_hpr(h, -5,0)
        dt = globalClock.getDt()
        if int(globalClock.get_frame_time()*100) % 8 ==0:
            self.light_1.set_color(Vec3(0.6,0.4,0.2)*random.uniform(0.75, 1.0))
        return task.again

    def set_bias(self, amount):
        self.bias+=amount
        print( self.bias)
        self.light_1.geom.setShaderInput('bias', self.bias)

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
            troll_img = OnscreenImage(image = img, scale=scale, pos = (x, 0, -y+64), parent=pixel2d)
            troll_img.set_transparency(TransparencyAttrib.M_alpha)
        else:
            img=loader.load_texture('texture/troll_big.png')
            scale=(512, 0, 256)#img size//2
            troll_img = OnscreenImage(image = img, scale=scale, pos = (x, 0, -y+64), parent=pixel2d)
            troll_img.set_transparency(TransparencyAttrib.M_alpha)

        s=Sequence()
        s.append(LerpPosHprInterval(troll_img, 2.0, (x, 0, -y), (0, 0, 20)))
        s.append(LerpPosHprInterval(troll_img, 3.0, (x+150, 0, -y-100), (0, 0, -60)))
        s.append(LerpPosHprInterval(troll_img, 4.0, (x-100, 0, -y+100), (0, 0, 60)))
        s.append(LerpPosHprInterval(troll_img, 1.0, (x, 0, -y+64), (0, 0, 0)))
        s.loop()

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
        self.menu_music.stop()
        self.game_music.play()
        self.current_chart=None
        self.level.reparent_to(deferred_render)
        self.sword.reparent_to(deferred_render)
        self.sword.loop('idle')
        self.zombie.reparent_to(deferred_render)
        self.key_lock=1
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
        self.key_lock-=1
        if self.key_lock < 0:
            self.key_lock=0

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
        self.key_lock+=1
        if self.current_chart is None:
            self.sounds['turn'].play()
            h=base.camera.get_h()
            s=Sequence()
            s.append(LerpHprInterval(base.camera, 0.8, (h+72,-10,-4)))
            s.append(LerpHprInterval(base.camera, 0.2, (h+90,-5,0)))
            s.append(Wait(0.2))
            s.append(Func(self.unlock_keys))
            s.start()
        else:
            if 'left' in self.current_chart[self.current_chart_node]:
                self.sounds['click'].play()
                cmd=self.current_chart[self.current_chart_node]['left'][2]
                self.current_chart_node=self.current_chart[self.current_chart_node]['left'][1]
                if cmd:
                    cmd()
            else:
                self.key_lock-=1
                return
            s=Sequence()
            s.append(Wait(1.1))
            s.append(Func(self.unlock_keys))
            s.start()
        self.chart.move_left()

    def rotate_right(self):
        if self.key_lock:
            return
        self.key_lock+=1
        if self.current_chart is None:
            self.sounds['turn'].play()
            h=base.camera.get_h()
            s=Sequence()
            s.append(LerpHprInterval(base.camera, 0.8, (h-72,-10,4)))
            s.append(LerpHprInterval(base.camera, 0.2, (h-90,-5,0)))
            s.append(Wait(0.2))
            s.append(Func(self.unlock_keys))
            s.start()
        else:
            if 'right' in self.current_chart[self.current_chart_node]:
                self.sounds['click'].play()
                cmd=self.current_chart[self.current_chart_node]['right'][2]
                self.current_chart_node=self.current_chart[self.current_chart_node]['right'][1]
                if cmd:
                    cmd()
            else:
                self.key_lock-=1
                return
            s=Sequence()
            s.append(Wait(1.1))
            s.append(Func(self.unlock_keys))
            s.start()

        self.chart.move_right()


    def move(self):
        if self.key_lock:
            return
        self.key_lock+=1
        if self.current_chart is None:
            if self.can_move():
                self.sounds['footsteps'].play()
                pos=base.camera.get_pos(render)
                heading=base.camera.get_h()
                h=(round(heading)%360)//90
                x,y=((0,2), (-2,0), (0,-2), (2,0))[h]
                map_pos=(int(round(pos.x*0.1)), int(round(pos.y*0.1)))
                forward_pos=(
                        (map_pos[0],map_pos[1]+1),
                        (map_pos[0]-1,map_pos[1]),
                        (map_pos[0],map_pos[1]-1),
                        (map_pos[0]+1,map_pos[1])
                        )[h]
                s=Sequence()
                if forward_pos in self.zombie_map:
                    self.current_chart=self.combat_chart
                    self.current_chart_node='start'
                    quat=Quat()
                    quat.set_hpr((-heading,0, 0))
                    head_sequence=Sequence(LerpHprInterval(base.camera, 0.5, (heading,0, 0)),
                                       LerpHprInterval(base.camera, 0.5, (heading,-5,0)))
                    move_sequence=Sequence()
                    for i in range(5):
                        if i==4:
                            z=0
                        elif i%2:
                            z=0.1
                        else:
                            z=-0.1
                        move_sequence.append(LerpPosInterval(base.camera, 0.2, pos+Point3(x*0.6*(i+1), y*0.6*(i+1), z)))
                    s.append(Parallel(head_sequence, move_sequence, LerpQuatInterval(self.zombie, 0.5, quat)))
                else:
                    head_sequence=Sequence(LerpHprInterval(base.camera, 0.5, (heading,0, 0)),
                                           LerpHprInterval(base.camera, 0.5, (heading,-5,0)))
                    move_sequence=Sequence()
                    for i in range(5):
                        if i==4:
                            z=0
                        elif i%2:
                            z=0.1
                        else:
                            z=-0.1
                        move_sequence.append(LerpPosInterval(base.camera, 0.2, pos+Point3(x*(i+1), y*(i+1), z)))
                    s.append(Parallel(head_sequence, move_sequence))
                s.append(Wait(0.1))
                s.append(Func(self.unlock_keys))
                s.start()
            else:
                self.key_lock-=1
                return
        else:
            if 'up' in self.current_chart[self.current_chart_node]:
                self.sounds['click'].play()
                cmd=self.current_chart[self.current_chart_node]['up'][2]
                self.current_chart_node=self.current_chart[self.current_chart_node]['up'][1]
                if cmd:
                    cmd()
            else:
                self.key_lock-=1
                return
            s=Sequence()
            s.append(Wait(1.1))
            s.append(Func(self.unlock_keys))
            s.start()
        self.chart.move_up()

game = Game()
game.run()

