from panda3d.core import *
from direct.interval.IntervalGlobal import *
from sdf_text import SdfText

class FlowChart:
    def __init__(self, game):
        self.game=game

        clip = aspect2d.attach_new_node(PlaneNode("clip", Plane(Vec3(0, 0, -1), Point3(0, 0, -0.01))))
        aspect2d.set_clip_plane(clip)


        self.font=loader.load_font('font/mono_font.egg')

        center_txt='???'
        if self.game.current_chart:
            center_txt=self.game.current_chart[self.game.current_chart_node]['txt']

        self.center=SdfText(self.font)
        self.center.wrap=30
        self.center.set_text_color((0.8, 0, 0, 1))
        self.center.set_outline_color((0, 0, 0, 1))
        self.center.set_outline_strength(1.0)
        #self.center.set_text('center')
        self.center.set_text(center_txt)
        self.center.reparent_to(aspect2d)
        self.center.set_pos(0,0,-0.75)
        self.center.set_scale(0.05)

        self.left=SdfText(self.font)
        self.left.wrap=8
        self.left.frame_tilt=45
        self.left.set_text_color((0.8, 0, 0, 1))
        self.left.set_outline_color((0.6, 0, 0, 1))
        self.left.set_outline_strength(0.5)
        self.left.set_text('left')
        self.left.reparent_to(aspect2d)
        self.left.set_pos(-1.0,0,-0.75)
        self.left.set_scale(0.05)

        self.right=SdfText(self.font)
        self.right.wrap=8
        self.right.frame_tilt=45
        self.right.set_text_color((0.8, 0, 0, 1))
        self.right.set_outline_color((0.6, 0, 0, 1))
        self.right.set_outline_strength(0.5)
        self.right.set_text('right')
        self.right.reparent_to(aspect2d)
        self.right.set_pos(1.0,0,-0.75)
        self.right.set_scale(0.05)


        self.top=SdfText(self.font)
        self.top.wrap=8
        self.top.frame_tilt=45
        self.top.set_text_color((0.8, 0, 0, 1))
        self.top.set_outline_color((0.6, 0, 0, 1))
        self.top.set_outline_strength(0.5)
        self.top.set_text('up')
        self.top.reparent_to(aspect2d)
        self.top.set_pos(0,0,-0.2)
        self.top.set_scale(0.05)


        self.left_line=self.draw_horizontal_line(self.left, self.center)
        self.right_line=self.draw_horizontal_line(self.center, self.right)
        self.top_line=self.draw_vertical_line(self.top, self.center)
        self.move_line=None

    def draw_vertical_line(self, top, bottom):
        top_min_point=Point3()
        top_max_point=Point3()
        top.geom.calc_tight_bounds(top_min_point,top_max_point)

        bottom_min_point=Point3()
        bottom_max_point=Point3()
        bottom.geom.calc_tight_bounds(bottom_min_point, bottom_max_point)

        lines=aspect2d.attach_new_node('line')

        l=LineSegs()
        l.set_color(Vec4(0, 0, 0, 1))
        l.set_thickness(5.0)
        l.move_to(Point3(top.pos.x, 0, top_min_point.z))
        l.draw_to(Point3(top.pos.x, 0, bottom_max_point.z))
        lines.attach_new_node(l.create())

        l=LineSegs()
        l.set_color(Vec4(0.8, 0, 0, 1))
        l.set_thickness(1.0)
        l.move_to(Point3(top.pos.x, 0, top_min_point.z))
        l.draw_to(Point3(top.pos.x, 0, bottom_max_point.z))
        lines.attach_new_node(l.create())
        return lines

    def draw_horizontal_line(self, left, right):
        left_min_point=Point3()
        left_max_point=Point3()
        left.geom.calc_tight_bounds(left_min_point,left_max_point)

        right_min_point=Point3()
        right_max_point=Point3()
        right.geom.calc_tight_bounds(right_min_point, right_max_point)

        lines=aspect2d.attach_new_node('line')

        l=LineSegs()
        l.set_color(Vec4(0, 0, 0, 1))
        l.set_thickness(5.0)
        l.move_to(Point3(left_max_point.x-0.01,0,left.pos.z))
        l.draw_to(Point3(right_min_point.x+0.01,0,left.pos.z))
        lines.attach_new_node(l.create())

        l=LineSegs()
        l.set_color(Vec4(0.8, 0, 0, 1))
        l.set_thickness(1.0)
        l.move_to(Point3(left_max_point.x,0,left.pos.z))
        l.draw_to(Point3(right_min_point.x,0,left.pos.z))
        lines.attach_new_node(l.create())
        return lines

    def update(self):
        try:
            self.left_line.remove_node()
            self.right_line.remove_node()
            self.top_line.remove_node()
        except:
            print("fu?")
        can_move=self.game.can_move()
        left_txt=self.game.get_left_text()
        if left_txt is not None:
            self.left.set_text(left_txt)
            self.left.set_pos(-1.0,0,-0.75)
            self.left_line=self.draw_horizontal_line(self.left, self.center)
        else:
            self.left.geom.hide()

        right_txt=self.game.get_right_text()
        if right_txt is not None:
            self.right.set_text(right_txt)
            self.right.set_pos(1.0,0,-0.75)
            self.right_line=self.draw_horizontal_line(self.center, self.right)
        else:
            self.right.geom.hide()

        up_text=self.game.get_up_text()
        if up_text is not None:
            if can_move:
                self.top.set_text(up_text)
                self.top.set_pos(0,0,-0.2)
                self.top_line=self.draw_vertical_line(self.top, self.center)
        else:
            self.top.geom.hide()

        if self.move_line:
            self.move_line.remove_node()


    def move_right(self):
        self.center.set_text(self.game.get_forward_text(-1))
        self.center.geom.set_pos(0, 0, 1)
        self.top.geom.hide()
        self.left.geom.hide()
        self.left_line.remove_node()
        self.right_line.remove_node()
        self.top_line.remove_node()
        self.move_line=self.draw_vertical_line(self.center, self.right)
        self.move_line.wrt_reparent_to(self.right.geom)
        self.move_line.set_pos(self.move_line, (1.0,0,0))

        s=Sequence()
        s.append(LerpPosInterval(self.right.geom, 0.25, (0,0,-0.75)))
        s.append(Parallel(
                    LerpPosInterval(self.right.geom, 0.7, (0,0,-2.5)),
                    LerpPosInterval(self.center.geom, 0.7, (0,0,-0.75))
                    )
                )
        s.append(Wait(0.1))
        s.append(Func(self.update))
        s.start()


    def move_left(self):
        self.center.set_text(self.game.get_forward_text(1))
        self.center.geom.set_pos(0, 0, 1)
        self.top.geom.hide()
        self.right.geom.hide()
        self.left_line.remove_node()
        self.right_line.remove_node()
        self.top_line.remove_node()

        self.move_line=self.draw_vertical_line(self.center, self.left)
        self.move_line.wrt_reparent_to(self.left.geom)
        self.move_line.set_pos(self.move_line, (-1.0,0,0))

        s=Sequence()
        s.append(LerpPosInterval(self.left.geom, 0.25, (0,0,-0.75)))
        s.append(Parallel(
                    LerpPosInterval(self.left.geom, 0.7, (0,0,-2.5)),
                    LerpPosInterval(self.center.geom, 0.7, (0,0,-0.75))
                    )
                )
        s.append(Wait(0.1))
        s.append(Func(self.update))
        s.start()

    def move_up(self):
        self.center.set_text(self.game.get_forward_text(0,2))
        self.center.geom.set_pos(0, 0, 1)
        self.left.geom.hide()
        self.right.geom.hide()
        self.left_line.remove_node()
        self.right_line.remove_node()
        self.top_line.remove_node()

        self.move_line=self.draw_vertical_line(self.center, self.top)
        self.move_line.wrt_reparent_to(self.top.geom)

        s=Sequence()
        s.append(Parallel(
                    LerpPosInterval(self.top.geom, 0.25, (0,0,-0.75)),
                    LerpPosInterval(self.center.geom, 0.25, (0,0, 0.55))
                    )
                )

        s.append(Parallel(
                    LerpPosInterval(self.top.geom, 0.7, (0,0,-1.95)),
                    LerpPosInterval(self.center.geom, 0.7, (0,0,-0.75))
                    )
                )
        s.append(Wait(0.1))
        s.append(Func(self.update))
        s.start()


