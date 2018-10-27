from panda3d.core import *
from operator import itemgetter
import random
import itertools

__all__ = ['Grid3D', 'Tileset', 'generate_level']

def frange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

def num_range(start, step, num):
    count=0
    while count<num:
        yield start+count*step
        count+=1

class Grid3D():
    def __init__(self, size=(10.0, 10.0, 5.0)):
        self.size=size
        self.grid=set()

    def pos_to_hash(self, pos):
        x=int(round(pos[0]/self.size[0]))
        y=int(round(pos[1]/self.size[1]))
        z=int(round(pos[2]/self.size[2]))
        return (x,y,z)

    def add(self, pos):
        h=self.pos_to_hash(pos)
        self.grid.add(h)
        return h

    def is_free(self, pos):
        p=self.pos_to_hash(pos)
        if p in self.grid:
            return False
        else:
            look_in=[(0,1,1),
                   (0,-1,1),
                   (1,0,1),
                   (-1,0,1),
                   (0,1,-1),
                   (0,-1,-1),
                   (1,0,-1),
                   (-1,0,-1)]
        for i in look_in:
            if tuple([sum(x) for x in zip(i,p)]) in self.grid:
                return False
        return True

class Tileset():
    def __init__(self, tile_path='', max_exits=3):
        self.tiles=[]
        self.weights=[]
        self.walls=[]
        self.all_exit_tiles=[]
        self.tile_path=tile_path
        self.max_exits=max_exits

    def add_tile(self, model, weight):
        tile=loader.load_model(self.tile_path+model)
        tile.clear_model_nodes()
        self.tiles.append(tile)
        self.weights.append(weight)
        if tile.find_all_matches('**/connect').get_num_paths() == self.max_exits:
            self.all_exit_tiles.append(tile)

    def add_wall(self, model):
        wall=loader.load_model(self.tile_path+model)
        wall.clear_model_nodes()
        self.walls.append(wall)

    def get_wall(self):
        return random.choice(self.walls)

    def get_tile(self):
        return random.choices(population=self.tiles, weights=self.weights)[0]

    def get_all_exit_tile(self):
        return random.choice(self.all_exit_tiles)

    @property
    def tile(self):
        return self.get_tile()

    @property
    def wall(self):
        return self.get_wall()

    @property
    def all_exit_tile(self):
        return self.get_all_exit_tile()

def make_quadtree(models):
    #find the size of the model
    min_point=Point3()
    max_point=Point3()
    models.calc_tight_bounds(min_point,max_point)
    x_min=min_point.x
    x_max=max_point.x
    y_min=min_point.y
    y_max=max_point.y
    x_size=x_max-x_min
    y_size=y_max-y_min
    #make a quad tree structure
    root=NodePath('quadree_root')
    low_nodes=[]
    for x in range(2):
        for y in range(2):
            top_node=root.attach_new_node('top_node'+str(x)+str(y))
            top_node.set_pos(render,x_min+((x*2+1)/4.0)*x_size,y_min+((y*2+1)/4.0)*y_size,0)
            for x1 in range(2):
                for y1 in range(2):
                    mid_node=top_node.attach_new_node('mid_node'+str(x1)+str(y1))
                    mid_node.set_pos(render,x_min+(x/2.0)*x_size+((x1*2+1)/8.0)*x_size,
                                     y_min+(y/2.0)*y_size+((y1*2+1)/8.0)*y_size,
                                     0)
                    for x2 in range(4):
                        for y2 in range(4):
                            low_node=mid_node.attach_new_node('low_node'+str(x2)+str(y2))
                            low_node.set_pos(render, x_min+(x/2.0)*x_size+(x1/4.0)*x_size+((x2*2+1)/32.0)*x_size,
                                                    y_min+(y/2.0)*y_size+(y1/4.0)*y_size+((y2*2+1)/32.0)*y_size,
                                                    0)
                            low_nodes.append(low_node)

    for model in models.get_children():
        best_distance=x_size*y_size
        for node in root.get_children():
            distance =model.get_distance(node)
            if distance < best_distance:
                top_node=node
                best_distance=distance

        best_distance=x_size*y_size
        for node in top_node.get_children():
            distance =model.get_distance(node)
            if distance < best_distance:
                mid_node=node
                best_distance=distance
        best_distance=x_size*y_size
        for node in mid_node.get_children():
            distance =model.get_distance(node)
            if distance < best_distance:
                low_node=node
                best_distance=distance
        model.wrt_reparent_to(low_node)
    #print('collapsing nodes...')
    for node in low_nodes:
        if node.get_num_children()>0:
            node.flatten_strong()
        else:
            node.remove_node()
    return root

def prev_tile(hpr, tile_id):
    h=(round(hpr.x)%360)//90
    return( (tile_id[0],tile_id[1]-1),
            (tile_id[0]+1,tile_id[1]),
            (tile_id[0],tile_id[1]+1),
            (tile_id[0]-1,tile_id[1]) )[h]


def generate_level(tileset, num_tiles, seed=None, grid=None):
    if seed:
        random.seed(seed)
    if grid is None:
        grid=Grid3D()
    grid.add((0,0,0))
    root = NodePath("random_level")

    #temp hack for staring tile... probably to stay
    tileset.all_exit_tile.copy_to(root)
    wall0=tileset.wall.copy_to(root)
    wall0.set_y(-10)
    wall0.set_h(180)

    #to late to find/fix bug, let's go around
    zombie_tiles=[]

    tiles={(0,0):[]}
    #print ('Adding tiles')
    while len(tiles) < num_tiles:
        connection=root.find('**/connect')
        if connection:
            pos=connection.get_pos(render)
            hpr=connection.get_hpr(render)
            connection.remove_node()
            if grid.is_free(pos):
                model=tileset.tile.copy_to(root)
                model.set_pos_hpr(pos, hpr)
                tile_id=(round(pos[0]*0.1),round(pos[1]*0.1))
                if model.get_name() == 'dungeon_n_0.egg':
                    zombie_tiles.append(tile_id)
                prev_tile_id=prev_tile(hpr, tile_id)
                #if prev_tile_id not in tiles:
                #    tiles[prev_tile_id]=[]
                if tile_id not in tiles:
                    tiles[tile_id]=[]
                tiles[tile_id].append(prev_tile_id)
                grid.add(pos)
            else:
                model=tileset.wall.copy_to(root)
                model.set_pos_hpr(pos, hpr)
        else:
            #print('corner case')
            #no connection found, remove corner and put a all exit tile there
            pos=list(tiles.keys())
            corners=[max(pos,key=itemgetter(0)), min(pos,key=itemgetter(0)),
                    max(pos,key=itemgetter(1)), min(pos,key=itemgetter(1))]
            model= tiles[random.choice(corners)]
            pos=model.get_pos(render)
            hpr=model.get_hpr(render)
            model.remove_node()
            model=tileset.all_exit_tile.copy_to(root)
            model.set_pos_hpr(pos, hpr)
            tile_id=(round(pos[0]*0.1),round(pos[1]*0.1))
            prev_tile_id=prev_tile(hpr, tile_id)
            if prev_tile_id not in tiles:
                tiles[prev_tile_id]=[]
            if tile_id not in tiles:
                tiles[tile_id]=[]
            tiles[tile_id].append(prev_tile_id)
            tiles[prev_tile_id].append(tile_id)
            debug[tile_id]=(model.get_name(),' removed corner')

            #tiles[prev_tile_id].append(tile_id)
            #tiles[prev_tile(hpr, tile_id)].append(tile_id)
    #close all connections that have no tiles
    # print ('Adding walls')
    for connection in root.find_all_matches('**/connect'):
        pos=connection.get_pos(render)
        hpr=connection.get_hpr(render)
        model=tileset.get_wall().copy_to(root)
        model.set_pos_hpr(pos, hpr)
        connection.remove_node()
        tile_id=(round(pos[0]*0.1),round(pos[1]*0.1))
        if tile_id in zombie_tiles:
            zombie_tiles.pop(zombie_tiles.index(tile_id))
    #find all places where there are two walls back to back and remve them
    #print ('Removing walls')
    walls={}
    for node in root.find_all_matches('**/wall'):
        pos=render.get_relative_point(node, (0,-5, 0))
        pos=(round(pos[0]),round(pos[1]))
        hpr=node.get_hpr(render)
        if pos in walls:
            map_pos=(round(node.get_x(render)*0.1),round(node.get_y(render)*0.1))
            prev_id=prev_tile(hpr, map_pos)
            if prev_id in tiles:
                tiles[prev_id].append(map_pos)
            #else:
            #    print('error')
            node.get_parent().remove_node()
            walls[pos].get_parent().remove_node()
        else:
            walls[pos]=node

    #root.ls()
    #print('optimizing...')
    return make_quadtree(root), tiles, zombie_tiles
    #root.flatten_strong()
    #return root
