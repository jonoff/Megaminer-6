# -*- coding: iso-8859-1 -*-
#-*-python-*-
from BaseAI import BaseAI
from GameObject import *
import util
from jon import *
from library import library
from datetime import datetime
import random, math

direction = 'lrud'

class AI(BaseAI):
    """The class implementing gameplay logic."""
    @staticmethod
    def username():
        return "mst00132"

    @staticmethod
    def password():
        return "S690n6r64"

    def init(self):
        random.seed(datetime.today())
        self.factory_workers_ids = []
        self.scrubbing_bubbles_ids = []
        if self.playerID() == 1:
            self.away = 1
        else:
            self.away = -1
        self.towards = -self.away


    def relative_direction(self, direction):
        if direction == 't':
            if self.playerID() == 0:
                return 'r'
            else:
                return 'l'
        elif direction == 'a':
            if self.playerID() == 0:
                return 'l'
            else:
                return 'r'
        return direction

    def my_move(self, bot, direction):
        direction = self.relative_direction(direction)

        self.map[bot.getX()][bot.getY()] = None
        bot.move(direction)
        self.map[bot.getX()][bot.getY()] = bot

    def end(self):
        pass

    def print_game_state(self):
        print "TURN: ", self.iteration
        print "#Bots: ", len(self.my_bots)
        print "bubble ids", self.scrubbing_bubbles_ids
        print "====================================\n"


    def turn_begin(self):
        self.ACTION = [t for t in self.types if t.getName() == 'action'][0]
        self.BUILDER = [t for t in self.types if t.getName() == 'builder'][0]
        self.CANNON = [t for t in self.types if t.getName() == 'cannon'][0]
        self.DAMAGE = [t for t in self.types if t.getName() == 'damage'][0]
        self.ENGINE = [t for t in self.types if t.getName() == 'engine'][0]
        self.FORCE = [t for t in self.types if t.getName() == 'force'][0]


        self.my_bots = [b for b in self.bots if b.getOwner() == self.playerID() and b.getPartOf() == 0]
        self.enemy_bots = [b for b in self.bots if b.getOwner() != self.playerID() and b.getPartOf() == 0]
        self.factory_workers = [b for b in self.my_bots if b.getId() in self.factory_workers_ids]
        self.scrubbing_bubbles = [b for b in self.my_bots if b.getId() in self.scrubbing_bubbles_ids]
        self.single_bots = [b for b in self.my_bots if b.getSize() == 1]
        self.double_bots = [b for b in self.my_bots if b.getSize() == 2]
        self.quad_bots = [b for b in self.my_bots if b.getSize() == 4]
        self.octo_bots = [b for b in self.my_bots if b.getSize() == 8]

        for bot in self.my_bots:
            bot.talk("My ID: " + str(bot.getId()))

        for frame in self.frames:
            if frame.getOwner() == self.playerID():
                frame.talk("My ID: " + str(frame.getId()))

        self.init_map()
        self.print_game_state()

    def turn_end(self):
        self.factory_workers_ids = [b.getId() for b in self.factory_workers]
        if self.scrubbing_bubbles_ids == [] and len(self.scrubbing_bubbles) != 4:
            self.scrubbing_bubbles = []
        else:
            self.scrubbing_bubbles_ids = [b.getId() for b in self.scrubbing_bubbles]
        #Combine non-factory workers
        to_combine = list(set(self.single_bots) - set(self.factory_workers) - set(self.scrubbing_bubbles))
        if self.can_combine(to_combine):
            to_combine[0].combine(to_combine[1], to_combine[2], to_combine[3])

    def init_map(self):
        self.map = {}
        #import pdb; pdb.set_trace()
        for x in range(-1, self.boardX()+1):
            self.map[x] = {}
            for y in range(-1, self.boardY()+1):
                if x == -1 or x == self.boardX() or y == -1 or y == self.boardY():
                    self.map[x][y] = -1
                else:
                    self.map[x][y] = None

        for object in self.bots:
            for x in range(object.getSize()):
                for y in range(object.getSize()):
                    self.map[object.getX()+x][object.getY()+y] = object
        for object in self.frames:
            for x in range(object.getSize()):
                for y in range(object.getSize()):
                    self.map[object.getX()+x][object.getY()+y] = object
        for object in self.walls:
            self.map[object.getX()][object.getY()] = object

    def can_combine(self, bot_list):
        if len(bot_list) != 4:
            return False

        x_values = []
        y_values = []

        for bot in bot_list:
            if bot.getX() not in x_values:
                x_values.append(bot.getX())
            if bot.getY() not in y_values:
                y_values.append(bot.getY())

        if len(x_values) != 2 or len(y_values) != 2:
            return False
        if math.fabs(x_values[0] - x_values[1]) != 1 or math.fabs(y_values[0] - y_values[1]) != 1:
            return False

        return True

    def objects_in_direction(self, bot, direction):
        direction = self.relative_direction(direction)
        objects = []
        #check all blocks to the right
        if direction == 'r':
            x = bot.getX() + bot.getSize()
            for y in range(bot.getY(), bot.getY() + bot.getSize()):
                if self.map[x][y] != None:
                    objects.append(self.map[x][y])

        elif direction == 'l':
            x = bot.getX() - 1
            for y in range(bot.getY(), bot.getY() + bot.getSize()):
                if self.map[x][y] != None:
                    objects.append(self.map[x][y])

        elif direction == 'u':
            y = bot.getY() - 1
            for x in range(bot.getX(), bot.getX() + bot.getSize()):
                if self.map[x][y] != None:
                    objects.append(self.map[x][y])

        elif direction == 'd':
            y = bot.getY() + bot.getSize()
            for x in range(bot.getX(), bot.getX() + bot.getSize()):
                if self.map[x][y] != None:
                    objects.append(self.map[x][y])

        return objects



    def factory_worker_directions(self,bots,types):
        for bot in bots:
            if bot.getY() < self.boardY() - 1 and self.map[bot.getX()][bot.getY()+1] in self.factory_workers:
                #Build towards
                if bot.getX() < self.boardX() - 1 and self.map[bot.getX()+self.towards][bot.getY()] == None:
                    bot.build(types[0], bot.getX()+self.towards, bot.getY(), 1)
            #B has A above
            elif bot.getY() > 0 and self.map[bot.getX()][bot.getY()-1] in self.factory_workers:
                #build towards
                if bot.getX() < self.boardX() - 1 and self.map[bot.getX()+self.towards][bot.getY()] == None:
                    bot.build(types[1], bot.getX()+self.towards, bot.getY(), 1)

            #C has D 3 below
            elif bot.getY() < self.boardY() - 3 and self.map[bot.getX()][bot.getY()+3] in self.factory_workers:
                #Build below
                if bot.getY() < self.boardY() - 1 and self.map[bot.getX()][bot.getY()+1] == None:
                    bot.build(types[2], bot.getX(), bot.getY()+1, 1)

            #D has C 3 above
            elif bot.getY() > 3 and self.map[bot.getX()][bot.getY()-3] in self.factory_workers:
                #Build above
                if bot.getY() > 0 and self.map[bot.getX()][bot.getY()-1] == None:
                    bot.build(types[3], bot.getX(), bot.getY()-1, 1)

    def nearest_object(self, bot, object_list):
        if len(object_list) == 0:
            return None
        return min(object_list,
                   key=lambda t: util.distance(bot.getX(), bot.getY(), bot.getSize(),
                                               t.getX(), t.getY(), t.getSize()) )


    def move_horizontal(self, bot, target):
        if( bot.getX() > target.getX() ):
            if( self.map[bot.getX()-1][bot.getY()] == None ):
                self.my_move(bot, 'l')
                return True
            return False
        else:
            if( self.map[bot.getX()+1][bot.getY()] == None ):
                self.my_move(bot, 'r')
                return True
            return False

    def move_vertical(self, bot, target):
        if( bot.getY() > target.getY() ):
            if( self.map[bot.getX()][bot.getY()-1] == None ):
                self.my_move(bot, 'u')
                return True
            return False
        else:
            if( self.map[bot.getX()][bot.getY()+1] == None ):
                self.my_move(bot, 'd')
                return True
            return False

    def move_towards(self, bot, target):
        # we're going up, down, left, right
        # depending on what's clear
        deltaX = math.fabs( bot.getX() - target.getX() )
        deltaY = math.fabs( bot.getY() - target.getY() )
        if( deltaX <= deltaY):
            if not self.move_vertical(bot, target):
                return self.move_horizontal(bot, target)
            return True
        elif( deltaY < deltaX ):
            if not self.move_horizontal(bot, target):
                return self.move_vertical(bot, target)
            return True

    def move_random(self, bot):
        # we're going up, down, left, right
        # depending on what's clear
        directions = []
        if( self.map[bot.getX()][bot.getY()-1] == None ):
            directions.append('u')
        if( self.map[bot.getX()][bot.getY()+1] == None ):
            directions.append('d')
        if( self.map[bot.getX()-1][bot.getY()] == None ):
            directions.append('l')
        if( self.map[bot.getX()+1][bot.getY()] == None ):
            directions.append('r')
        if( len(directions) > 0 ):
            self.my_move(bot, random.choice(directions))


   def double_bot(self, bot):
        #depends on composition
        mini_bots_types = [self.types[b.getType() - 1] for b in self.my_bots if b.getPartOf() == bot.getId()]
        if mini_bots_types == [self.BUILDER] * 4:
            
        #self.my_bots = [b for b in self.bots if b.getOwner() == self.playerID() and b.getPartOf() == 0]


        #move if empty space next to us
        objects = self.objects_in_direction(bot, 't')
        if objects == []:
            self.my_move(bot,'t')

        #otherwise, attack objects in front if not friendly
        else:
            for object in objects:
                if object.getOwner() != self.playerID():
                    bot.attack(object)

        #always heal
        bot.heal(bot)


    def jons_build(self):
        #Move factory into place
        if len(self.my_bots) == 4 and self.can_combine(self.my_bots):
            print "MOVING FACTORY workers"
            for bot in self.my_bots:
                self.factory_workers.append(bot)
                #Guy to right
                if bot.getX() < self.boardX() - 1 and self.map[bot.getX()+self.towards][bot.getY()] in self.my_bots:
                    self.my_move(bot,'a')
                #Guy to left
                else:
                    #Guy below
                    if bot.getY() < self.boardY() - 1 and self.map[bot.getX()][bot.getY()+1] in self.my_bots:
                        #move up
                        self.my_move(bot,'u')
                    #Guy above
                    else:
                        self.my_move(bot,'d')
        else:
            if len(self.scrubbing_bubbles)  == 0:
                self.factory_worker_directions(self.factory_workers,[self.DAMAGE, self.DAMAGE, self.DAMAGE, self.DAMAGE])

            else: #len(self.double_bots) < 3:
                self.factory_worker_directions(self.factory_workers,[self.BUILDER, self.BUILDER, self.BUILDER, self.BUILDER])

            for bot in self.my_bots:
                if bot.getSize() == 2:
                    self.double_bot(bot)
                    continue

                #Less than 4, create factory
                if( len(self.my_bots) < 4 ):
                    if bot.getX() < self.boardX() - 1 and self.map[bot.getX()+self.towards][bot.getY()] == None:
                            bot.build(self.BUILDER, bot.getX()+self.towards, bot.getY(), 1)


                #Factory in place:
                #  C   <--  A,B,C,D individual builders
                #AXX   <-- X is to be built
                #BXX
                #  D
                elif bot in self.factory_workers:
                    continue

                elif bot.getSize() == 1:
                    bot.talk("I am little and of type: %s!" % str(bot.getType()))
                    if self.types[bot.getType()-1] == self.DAMAGE:
                        if self.scrubbing_bubbles_ids == []:
                            self.scrubbing_bubbles.append(bot)

                        if bot in self.scrubbing_bubbles:
                            bot.talk("I am a bubble!");
                            target = self.nearest_object(bot, self.walls + self.enemy_bots )
                            if target:
                                target_distance = util.distance( bot.getX(), bot.getY(), bot.getSize(),
                                                             target.getX(), target.getY(), target.getSize() )
                                bot.talk( "target id: %s  distance: %i" % (target.getId(), target_distance) )
                                if( target_distance <= bot.getRange() + 1 ):
                                    bot.attack(target)
                                if( target_distance > 1 ):
                                    if not self.move_towards(bot, target):
                                        self.move_random(bot)



    def run(self):
        self.turn_begin()
        self.jons_build()
        self.turn_end()

        return 1

    def __init__(self, conn):
        BaseAI.__init__(self, conn)
