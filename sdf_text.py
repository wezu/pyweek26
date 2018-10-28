from panda3d.core import *
from textwrap import wrap


__all__ = ['SdfText']


class SdfText:
    def __init__(self, font):
        self.potato_mode=ConfigVariableBool('potato-mode', False).get_value()
        self.txt_node=TextNode('sdf_text_node')
        self.txt_node.set_font(font)
        self.geom=NodePath(self.txt_node.get_internal_geom())
        self.__txt_color=Vec4(1.0, 1.0, 1.0, 1.0)
        self.__outline_color= Vec4(0.0, 0.0, 0.0, 0.0)
        self.__outline_offset= Vec2(0.0)
        self.__outline_power=1.0
        self.parent=None
        self.wrap=None
        self.frame=True
        self.frame_tilt=0
        self.__center=True
        self.__pos=Vec3(0.0)
        self.__hpr=Vec3(0.0)
        self.__scale=Vec3(1.0)
        self.shader=Shader.load(Shader.SL_GLSL, 'shader/sdf_v.glsl', 'shader/sdf_f.glsl')
        self.geom=None
        self.quad=None
        self._make_geom()

    def _make_geom(self):
        '''Refresh or create the actual geom with the text '''
        if self.geom:
            self.geom.remove_node()
        self.geom=NodePath(self.txt_node.get_internal_geom())
        if self.potato_mode:
            self.geom.set_transparency(TransparencyAttrib.M_binary, 1)
        else:
            self.geom.set_shader(self.shader, 1)
            self.geom.set_shader_input('outline_color', self.__outline_color)
            self.geom.set_shader_input('outline_offset', self.__outline_offset)
            self.geom.set_shader_input('outline_power', self.__outline_power)
            self.geom.set_transparency(TransparencyAttrib.M_alpha, 1)
        if self.__center:
            center_point=self.geom.get_bounds().get_center()
            self.geom.set_pos(-center_point)
            self.geom.flatten_light()
        if self.parent:
            self.geom.reparent_to(self.parent)
        if self.frame:
            min_point=Point3()
            max_point=Point3()
            self.geom.calc_tight_bounds(min_point,max_point)
            if not min_point.almost_equal(Point3(0)) and not max_point.almost_equal(Point3(0)):
                cm = CardMaker("card")
                if self.frame_tilt:
                    frame_size=(
                            min(min(min_point[0], min_point[2])-0.4, -1.6),
                            max(max(max_point[0], max_point[2])+0.4, 1.6),
                            min(min(min_point[0], min_point[2])-0.4,-1.6),
                            max(max(max_point[0], max_point[2])+0.4, 1.6)
                            )
                else:
                    frame_size=(
                            min(min_point[0]-0.4, -1.5),
                            max(max_point[0]+0.4, 1.5),
                            min(min_point[2]-0.4,-1.5),
                            max(max_point[2]+0.4, 1.5)
                            )
                cm.set_frame(*frame_size)
                center_node=self.geom.attach_new_node('frame')
                frame= NodePath(cm.generate())
                frame.reparent_to(self.geom)
                frame.wrt_reparent_to(center_node)
                frame.set_color(0,0,0, 0.7)
                frame.set_transparency(TransparencyAttrib.M_alpha, 1)
                #draw lines
                l=LineSegs()
                l.set_color(Vec4(0.8, 0, 0, 1))
                l.set_thickness(1.0)
                #l.move_to(Point3(frame_size[0], 0, frame_size[2]))
                #l.move_to(Point3(frame_size[0], 0, frame_size[1]))
                ''' left, right, bottom, top
                    0,3----1,3
                    |      |
                    |      |
                    0,2---1,2
                '''
                l.move_to(Point3(frame_size[0], 0, frame_size[3]))
                l.draw_to(Point3(frame_size[1], 0, frame_size[3]))
                l.draw_to(Point3(frame_size[1], 0, frame_size[2]))
                l.draw_to(Point3(frame_size[0], 0, frame_size[2]))
                l.draw_to(Point3(frame_size[0], 0, frame_size[3]))
                center_node.attach_new_node(l.create())
                center_node.set_hpr(0,0,self.frame_tilt)
                center_node.flatten_light()

        self.geom.set_pos_hpr_scale(self.__pos, self.__hpr, self.__scale)



    def set_center(self, center=True):
        self.__center=center
        if center:
            self.txt_node.set_align(TextNode.A_center)
        else:
            self.txt_node.set_align(TextNode.A_left)
        self._make_geom()

    def set_text(self, text):
        '''Sets text'''
        if self.wrap:
            '''wrapped_text=''
            pattern='{:^'+str(self.wrap)+'}\n'
            for line in wrap(text, self.wrap):
                wrapped_text+=pattern.format(line)
            text=wrapped_text
            #print(text)'''
            text="\n".join(wrap(text, self.wrap))
        self.txt_node.set_text(text)
        if self.__center:
            self.txt_node.set_align(TextNode.A_center)
        else:
            self.txt_node.set_align(TextNode.A_left)

        #if self.frame:
        #    self.txt_node.set_frame_color(self.__txt_color)
        #    self.txt_node.set_frame_as_margin(0.5, 0.7, 0.5, 0.5)
        self._make_geom()

    def reparent_to(self, node):
        '''Reparent the text geom to node (as if for NodePath)'''
        self.geom.reparent_to(node)
        self.parent=node
        self._make_geom()

    def set_hpr(self,*args):
        '''Set rotation (as if for NodePath)'''
        self.geom.set_hpr(*args)
        self.__hpr=self.geom.get_hpr()

    def set_pos(self, *args):
        '''Set position (as if for NodePath)'''
        self.geom.set_pos(*args)
        self.__pos=self.geom.get_pos()

    def set_scale(self, *args):
        '''Set scale (as if for NodePath)'''
        self.geom.set_scale(*args)
        self.__scale=self.geom.get_scale()

    def set_text_color(self, *color):
        '''Sets text color (rgba) '''
        self.__txt_color=Vec4(*color)
        self.txt_node.set_text_color(self.__txt_color)
        self._make_geom()

    def set_outline_color(self, *color):
        '''Sets text outline color (rgba) '''
        self.__outline_color=Vec4(*color)
        self.geom.set_shader_input('outline_color', self.__outline_color)

    def set_outline_strength(self, strength):
        '''Sets outline strength.
        Values smaller than 1.0 will make the outline less prominent
        Values greater than 1.0 will make the outline stronger'''
        self.__outline_power=1.0/strength
        self.geom.set_shader_input('outline_power', self.__outline_power)

    def set_outline_offset(self, x_offset=0, y_offset=0):
        '''Outline offset in pixels.
        Will cause artefacts when larger than the glyph padding in the texture!'''
        tex=self.geom.find_all_textures()[0]
        x=tex.get_x_size()
        y=tex.get_y_size()
        self.__outline_offset=Vec2(x_offset/x, y_offset/y)
        self.geom.set_shader_input('outline_offset', self.__outline_offset)

    #properties:
    @property
    def outline_offset(self):
        return self.__outline_offset

    @outline_offset.setter
    def outline_offset(self, value):
        self.set_outline_offset(value)

    @property
    def outline_strength(self):
        return self.__outline_strength

    @outline_strength.setter
    def outline_strength(self, value):
        self.set_outline_strength(value)

    @property
    def outline_color(self):
        return self.__outline_color

    @outline_color.setter
    def outline_color(self, value):
        self.set_outline_color(value)

    @property
    def text_color(self):
        return self.__text_color

    @text_color.setter
    def text_color(self, value):
        self.set_text_color(value)

    @property
    def scale(self):
        return self.__scale

    @scale.setter
    def scale(self, value):
        self.set_scale(value)

    @property
    def pos(self):
        return self.__pos

    @pos.setter
    def pos(self, value):
        self.set_pos(value)

    @property
    def hpr(self):
        return self.__hpr

    @hpr.setter
    def hpr(self, value):
        self.set_hpr(value)

    @property
    def text(self):
        return self.txt_node.get_text()

    @text.setter
    def text(self, value):
        self.set_text(value)

    @property
    def center(self):
        return self.__center

    @center.setter
    def center(self, value):
        self.set_center(value)
