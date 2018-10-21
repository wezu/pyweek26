from panda3d.core import *
load_prc_file_data("", "sync-video 0")
load_prc_file_data("", "show-frame-rate-meter  1")
#load_prc_file_data("", "win-size 1280 720")
from direct.showbase.ShowBase import ShowBase

from flow_chart import FlowChart

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        #base.set_background_color(0.0, 0.0, 0.0)

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
        base.accept('w', self.chart.move_up)
        base.accept('a', self.chart.move_left)
        base.accept('d', self.chart.move_right)

        '''font=loader.load_font('font/mono_font.egg')
        self.txt=SdfText(font)
        self.txt.wrap=20
        self.txt.set_text_color((0.8, 0, 0, 1))
        self.txt.set_outline_color((0.6, 0, 0, 1))
        self.txt.set_outline_strength(0.5)
        self.txt.set_text(test_txt)
        #txt.set_text('short text')
        self.txt.reparent_to(aspect2d)
        self.txt.set_pos(0,0,0)
        self.txt.set_scale(0.05)
        #txt.geom.setRenderModeFilledWireframe((1.0, 0, 0, 1))



        base.accept('w', self.chart.move_up)'''

        '''txt_node=TextNode('text_node')
        txt_node.set_font(loader.load_font('font/txt.ttf'))
        txt_node.set_text(frame_txt)
        txt_np=aspect2d.attachNewNode(txt_node)
        #txt_node.set_pos(0,0,0)
        txt_np.set_scale(0.06)'''

        '''cm = CardMaker("frame")
        cm.set_frame_fullscreen_quad()
        self.quad = NodePath(cm.generate())
        self.quad.set_texture(loader.load_texture('texture/frame_4.png'))
        self.quad.set_scale(scale)
        self.quad.reparent_to(aspect2d)
        #self.quad.set_pos(bounds[0][0], 0 , bounds[1][2])
        self.quad.set_transparency(TransparencyAttrib.MAlpha, 1)
        self.quad.set_shader(txt.shader)
        self.quad.set_color((0.8, 0, 0, 1), 1)
        self.quad.set_shader_input('outline_color',(0.6, 0, 0, 0))
        self.quad.set_shader_input('outline_power', 1.0/0.5)
        self.quad.set_shader_input('outline_offset', Vec2(0.0))
        self.quad.set_shader_input('outline_power', 1.0)'''

    def change_txt(self):
        self.txt.set_text('short text')


game = Game()
game.run()
