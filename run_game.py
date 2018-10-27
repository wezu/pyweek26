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
from vfx import Vfx
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
                                    'up':('Start game', 'intro', self.logo.hide)},
                            'intro':{'txt':'The darkness envelops you. You lose track of time, space and self.',
                                    'up':('Next', 'intro1',None)},
                            'intro1':{'txt':"All you can remember is someone's voice, maybe even your own...",
                                    'up':('Next', 'intro2', None)},
                            'intro2':{'txt':'"You can move on only when you defat all the undead"',
                                    'up':('Go!', None, self.start_game)},
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
                                    'up':('OK.','zombie_turn',self.zombie_turn )},
                            'die':{'txt':'You died.',
                                   'up':('OK.','die',None)},
                            'win':{'txt':'The zombie is dead... even more dead.',
                                   'up':('OK.','win',self.end_combat)},
                           }
        self.end_game_chart={ 'start':{'txt':'As the last zombie dies a bright light appears in front of you.',
                               'up':('Next', 'txt1', None)},
                              'txt1':{'txt':'You realize it is a portal identical to the one that brought you into this dungeon.',
                               'up':('Next', 'txt2', None)},
                              'txt2':{'txt':'You take a hesitant step forward, dreading what horrors might await on the other side...',
                               'up':('Next', 'txt3', None)},
                              'txt3':{'txt':'...but then again, could there be anything worst then this place?',
                                    'right':('Go in', 'txt4', None),
                                    'left':('Step back', 'txt5', None)},
                              'txt4':{'txt':'You step into the portal... but that is a story for another PyWeek\nGAME OVER',
                                     'up':('End', 'txt4', self.game_over)},
                              'txt5':{'txt':'The portal vanishes. You are alone. You sword is your only exit...\nGAME OVER ',
                                      'up':('End', 'txt5', self.bad_end)}
                            }

        self.current_chart=self.tutorial_chart
        self.current_chart_node='start'


        self.key_forward=ConfigVariableString('up-key', 'w').get_value()
        self.key_left=ConfigVariableString('left-key', 'a').get_value()
        self.key_right=ConfigVariableString('right-key', 'a').get_value()

        base.accept(self.key_forward, self.move)
        base.accept(self.key_left, self.rotate_left)
        base.accept(self.key_right, self.rotate_right)

        self.bias=0.0035
        base.accept('=', self.set_bias,[0.0001])
        base.accept('-', self.set_bias,[-0.0001])


        self.key_lock=0
        self.block=False

        self.tiles_description={
                                'wall':('You see a wall',
                                        'You see a wall',
                                        'You see a wall',
                                        'You see a wall',
                                        'There is a big wall of stones in front of you.',
                                        'There is just a stone wall in front.',
                                        'There is no passage in front because of the wall.',
                                        'Stones, stones everywhere I look in front.',
                                        'You see a thick wall of cold bricks.',
                                        'You see a thick wall of mouldy bricks.',
                                        'You see a thick wall of rotten bricks.',
                                        'You see a thick wall of decaying bricks.',
                                        'You can notice a strong wall just ahead.',
                                        'The passage is leading to a dead end.',
                                        'The passage is blocked by a dry-stone wall.',
                                        'The passageway is blocked by a stone wall.',
                                        'The stonework do not allow you to move forward.',
                                        "There is a wall. You stare at it but it doesn't stare back. Surprise!",
                                        "There is a wall. You stare at it but it doesn't stare back. Surprise?",
                                        "There is a wall. You stare at it but it doesn't stare back....or does it???",
                                        'You see nothing out of the ordinary.',
                                        'You see nothing out of the unusual.',
                                        'You see nothing exceptional about this wall.',
                                        'You should be accustomed to seeing bricks.',
                                        'The sanctity of this place has been defiled'
                                        ),
                                (False,False,False):('You see a dead end',
                                                     'You see a dead end',
                                                     'You see a dead end',
                                                     'You see a dead end',
                                                     'You can see a brick wall',
                                                     'There are just three stone walls in front of you.',
                                                     'The passage terminates in a dead end.',
                                                     "It's a blind alley - there is no hope of progress",
                                                     "It's a blind alley - there is no hope of moving on..",
                                                     "The walls obstructs my progress.",
                                                     "These walls impedes my progress.",
                                                     'This way leads nowhere.'
                                                    ),
                                (False,True,False):('You see a tunnel leading straight ahead',
                                                    'You see a tunnel leading straight ahead',
                                                    'You see a tunnel leading straight ahead',
                                                    'There is a tunnel before.',
                                                    'There is a tunnel before.',
                                                    'There is a tunnel before.',
                                                    'This passage looks familiar.',
                                                    'Have you been in this place?',
                                                    'There is a slight breeze here..',
                                                    'There is no light coming from this tunnel',
                                                    'The smell of death surrounds me',
                                                    'The sanctity of this place has been defiled',
                                                    'The is something before me',
                                                    'You hear footsteps in the distance',
                                                    'The corridor is shrouded in a gloomy light',
                                                    'This way leads straight'
                                                    ),
                                (True,False,False):('You see a tunnel leading left',
                                                    'You see a tunnel leading left',
                                                    'You see a tunnel leading left',
                                                    'You see a tunnel leading left',
                                                    'You see a passage to the left',
                                                    'You see a passage to the left',
                                                    'The corridor leads left',
                                                    'How long have I been here?',
                                                    'There is no hope, just a passage to the left',
                                                    'I can go left from here',
                                                    '"Left"- you say aloud, just to remember how a human vice sounds like',
                                                    'You think you are lost',
                                                    '...and then a Dragon eats you! - not really, just checking if you read this.',
                                                    'I wonder if God was ever here? Did he turn away in fear?'
                                                    ),
                                (False,False,True):('You see a tunnel leading right',
                                                    'You see a tunnel leading right',
                                                    'You see a tunnel leading right',
                                                    'You see a passage to the right',
                                                    'You see a passage to the right',
                                                    'You see a passage to the right',
                                                    'The corridor leads right',
                                                    'The corridor leads right',
                                                    'The corridor leads right',
                                                    'The corridor leads right',
                                                    'All these corridors look alike',
                                                    'There is no hope, just a passage to the right',
                                                    "I can't go left from here",
                                                    '"Right"- you say aloud, just to remember how a human vice sounds like',
                                                    ),
                                (True,True,False):('You see a tunnel with a side passage going left',
                                                    'You can go forward or you can go left',
                                                    ),
                                (False,True,True):('You see a tunnel with a side passage going right',
                                                    'You see a tunnel with a side passage going right',
                                                    'You see a tunnel with a side passage going right',
                                                    'You can go forward or you can go right',
                                                    'You can go forward or you can go right',
                                                    'You can go forward or you can go right',
                                                    'The echo of you footsteps taunt you, but you know you are not alone',
                                                    ),
                                (True, False, True):('The tunnel before you goes left and right',
                                                    'The tunnel before you goes left and right',
                                                    'The tunnel before you goes left and right',
                                                    'The tunnel before you goes left and right',
                                                    'The tunnel before you goes left and right',
                                                    "There's a slight breeze coming from the right",
                                                    "There's a slight breeze coming from the left",
                                                    "Something moved in the darkness",
                                                    "Left or Right? You could toss a coin if you only had a coin..."
                                                    ),
                                (True, True, True):('You came to a junction',
                                                    'You came to a junction',
                                                    'You came to a junction',
                                                    'You came to a junction',
                                                    'You came to a complex corridor, simple is better than complex.',
                                                    'You came to a complex corridor, complex is better than complicated.',
                                                    'There should be one (and preferably only one) obvious way to go... there is not.',
                                                    'You can go left, right or straight ahead.',
                                                    'You came to a 4 way intersection.',
                                                    'Tunnels connect here.',
                                                    'Tunnels connect here.',
                                                    'Tunnels connect here.',
                                                    'You think you are lost, even more then before',
                                                    'You can choose where to go from here',
                                                    'You can choose where to go from here, if only you knew where to go',
                                                    'You see three tunnels before you - Choose your destiny.',
                                                    )
                                }

        #print('loading tiles...')
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
        #print('building level...')
        self.set_loading_txt('Building level...')
        self.level, self.map, zombie_tiles = level_gen.generate_level(self.tileset, num_tiles=250)
        #self.level.reparent_to(render)
        #self.level.analyze()
        #print('ready!')
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
                     'die':loader.load_sfx('sound/die.ogg'),
                    }

        self.hp=1.0
        self.zombie_hp=1.0

        self.set_loading_txt('Spawning zombies...')
        self.zombie_map={}

        #find a place to put the zombie in
        #this should be close to the start, but not on top of the player
        first_zombie_pos=None
        for x,y in ((0,1), (0,-1), (1,0), (-1,0)):
            if first_zombie_pos is None:
                if (x,y) in self.map:
                    for (z,w) in ((x,y+1), (x,y-1), (x+1,y), (x-1,y)):
                        if (z,w) in self.map and (z,w)!=(x,y) and (z,w)!=(0,0):
                            if first_zombie_pos is None:
                                self.zombie.set_pos(z*10, w*10, 0)
                                self.zombie_map[(z,w)]=self.zombie
                                first_zombie_pos=(z,w)

        #put 10 more zombies in the map
        valid_pos=[]
        #print(len(zombie_tiles))
        num_samples=min(50, len(zombie_tiles))

        for pos in random.sample(zombie_tiles, num_samples):
            if len(valid_pos) ==10:
                break
            if pos != first_zombie_pos:
                v_pos=Vec2(pos)
                good=True
                for test_pos in valid_pos:
                    d=(Vec2(test_pos)-v_pos).length()
                    if d <5.0:
                        good=False
                if good:
                    valid_pos.append(pos)

        for zombie_pos in valid_pos:
            self.make_zombie(zombie_pos)
        self.set_loading_txt('')

        self.chart=FlowChart(self)
        self.chart.update()
        base.musicManager.set_volume(ConfigVariableDouble('music-volume', 0.75).get_value())
        base.sfxManagerList[0].set_volume(ConfigVariableDouble('sound-volume', 1.0).get_value())
        self.menu_music.play()

        self.accept('tab', base.bufferViewer.toggleEnable)
        self.accept('9',aspect2d.hide)
        self.accept('0',aspect2d.show)


    def game_over(self):
        self.key_lock=1
        aspect2d.hide()
        self.zombie.hide()
        self.level.hide()
        self.sword.hide()
        vfx_pos=render.get_relative_point(base.camera, (0, 9, 1.0))
        LerpPosInterval(base.camera, 0.5, vfx_pos).start()

    def bad_end(self):
        self.vfx.remove()
        if not self.potato_mode:
            del self.vfx_light
        self.current_chart=None

    def test_vfx(self):
        self.vfx=Vfx('texture/vfx_portal.png', True, 30, 256)
        self.vfx.set_pos((0, 0, 1.2))
        self.vfx.set_scale(8)


    def make_zombie(self, map_pos):
        zombie= Actor('actor/m_zombie',
                          {'idle':'actor/a_zombie_idle',
                          'interrupt':'actor/a_zombie_interrupt',
                          'ready':'actor/a_zombie_ready',
                          'stabbed':'actor/a_zombie_stabbed',
                          'strike':'actor/a_zombie_strike',
                          'block':'actor/a_zombie_block',
                          'die':'actor/a_zombie_die',
                          'attack':'actor/a_zombie_attack'})
        #zombie.set_hpr(90, 0, 0)
        zombie.set_scale(0.03)
        zombie.loop('idle')
        if not self.potato_mode:
            zombie.set_blend(frameBlend = True)
            attr = ShaderAttrib.make(Shader.load(Shader.SLGLSL, 'shader/actor_v.glsl', 'shader/geometry_f.glsl'))
            attr = attr.setFlag(ShaderAttrib.F_hardware_skinning, True)
            zombie.set_attrib(attr)
            loader._setTextureInputs(zombie)
        zombie.set_transparency(TransparencyAttrib.MNone, 1)
        zombie.set_pos(map_pos[0]*10, map_pos[1]*10, 0)
        zombie.reparent_to(deferred_render)
        self.zombie_map[map_pos]=zombie


    def end_combat(self):
        #print('end combat')
        self.hp+=0.5
        self.set_hp()

        pos=base.camera.get_pos(render)
        heading=base.camera.get_h()
        h=(round(heading)%360)//90
        map_pos=(int(round(pos.x*0.1)), int(round(pos.y*0.1)))

        self.current_chart=None

        del self.zombie_map[map_pos]

        if len(self.zombie_map)<1:
            self.game_music.stop()
            self.menu_music.play()
            self.vfx=Vfx('texture/vfx_portal.png', True, 30, 256)
            vfx_pos=render.get_relative_point(base.camera, (0, 10, 0.8))
            self.vfx.set_pos(vfx_pos)
            self.vfx.set_scale(7.5)
            self.current_chart=self.end_game_chart
            self.current_chart_node='start'
            if not self.potato_mode:
                light_pos=render.get_relative_point(base.camera, (0, 10, 0.5))
                self.vfx_light = SphereLight(color=(0.33,0.24,0.95), pos=(light_pos), radius=20.0, shadow_size=0, shadow_bias=0.0035)
        else:
            LerpPosInterval(base.camera, 0.5, (map_pos[0]*10, map_pos[1]*10, pos.z)).start()

    def set_hp(self, value=0.0):
        self.hp+=value
        #print(self.hp)
        if self.hp >1.0:
            self.hp =1.0
        if self.hp <=0.01:
           self.hp =0.0
           self.sounds['die'].play()
           #print('You died')
           self.current_chart_node='die'
           pos=base.camera.get_pos(render)
           pos.z=0.2
           hpr=base.camera.get_hpr(render)
           hpr.z=-90
           LerpPosHprInterval(base.camera, 2.0, pos, hpr).start()
           self.sword.hide()
        deferred_renderer.set_filter_input('pre_aa','health', self.hp)

    def zombie_turn(self):
        if self.zombie_hp <= 0.01:
            self.zombi_anim('die', hold=True)
            self.current_chart_node='win'
            self.combat_chart['zombie_turn']['txt']='The zombie falls on its back.'
            return

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
                Sequence(Wait(0.4), Func(self.set_hp, -0.1)).start()
            else:
                self.combat_chart['zombie_turn']['txt']='The zombie delivers a powerful attacks. It hurts!'
                Sequence(Wait(0.4), Func(self.set_hp, -0.3)).start()
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
                Sequence(Wait(0.65), Func(self.set_hp, -0.2)).start()
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
            Sequence(Wait(0.4), Func(self.set_hp, -0.2)).start()
            self.zombie_hp-=0.1
        else:
            self.sounds['stab_hit'].play()
            self.zombi_anim('stabbed', 0.2)
            self.combat_chart['result']['txt']='You stabbed the zombie! It is not happy.'
            self.zombie_hp-=0.2

    def slash(self):
        self.block=False
        self.key_lock+=1
        self.sword_anim('slash')
        if self.zombi_state == 'ready':
            self.zombi_anim('interrupt', 0.8)
            self.sounds['slash'].play()
            self.combat_chart['result']['txt']="You strike the zombie knocking it off balance!"
            self.zombie_hp-=0.2
            self.zombi_state = 'recover'
        elif self.zombi_state == 'idle':
            self.sounds['block'].play()
            self.zombi_anim('block', 0.2)
            self.combat_chart['result']['txt']='You try to strike the zombie, but it blocks easily.'
        else:
            self.zombi_anim('interrupt')
            self.sounds['slash'].play()
            self.combat_chart['result']['txt']='You strike the zombie'
            self.zombie_hp-=0.1

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
                    self.zombie=self.zombie_map[forward_pos]
                    self.zombie_hp=1.0
                    self.zombi_state = 'idle'
                    self.current_chart=self.combat_chart
                    self.current_chart_node='start'
                    temp=render.attach_new_node('temp')
                    temp.set_pos(self.zombie.get_pos())
                    temp.look_at(base.camera)
                    temp.set_h(temp.get_h()-180)
                    quat=temp.get_quat()
                    temp.remove_node()
                    head_sequence=Sequence(LerpHprInterval(base.camera, 0.5, (heading,-3, 0)),
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
                    head_sequence=Sequence(LerpHprInterval(base.camera, 0.5, (heading,-3, 0)),
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

