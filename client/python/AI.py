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
        self.ACTION = [t for t in self.types if t.getName() == 'action'][0]
        self.BUILDER = [t for t in self.types if t.getName() == 'builder'][0]
        self.CANNON = [t for t in self.types if t.getName() == 'cannon'][0]
        self.DAMAGE = [t for t in self.types if t.getName() == 'damage'][0]
        self.ENGINE = [t for t in self.types if t.getName() == 'engine'][0]
        self.FORCE = [t for t in self.types if t.getName() == 'force'][0]
        
        random.seed(datetime.today())
        self.factory_workers_ids = []
        self.scrubbing_bubbles_ids = []
        if self.playerID() == 1:
            self.away = 1
        else:
            self.away = -1
        self.towards = -self.away
        steam_roller_selector = [self.FORCE]*5+[self.BUILDER]*3
        paladin_selector = [self.DAMAGE]*4+[self.BUILDER]*2+[self.CANNON]+[self.FORCE]*2
        scrubber_selector = [self.DAMAGE]*9+[self.BUILDER]*1
        super_selector = steam_roller_selector+scrubber_selector
        selectors = [steam_roller_selector] + [paladin_selector] + [scrubber_selector] + [super_selector]
        
        self.selector = random.choice(selectors)
        
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


    def end(self):
        pass

    def print_game_state(self):
        print "TURN: ", self.iteration
        print "#Bots: ", len(self.my_bots)
        print "Time(0): %s | Time(1): %s" % (self.player0Time(),self.player1Time())
        print "Selector is: ", self.selector
        #print ("big_bots_ids:%s" % ( self.big_bots_ids))
        #print ("constructors_ids %s" % ( self.constructors))


    def turn_begin(self):
        

        self.my_bots = [b for b in self.bots if b.getOwner() == self.playerID() and b.getPartOf() == 0]
        self.constructors = [b for b in self.my_bots if
                               (b.getType() > 0 and self.types[b.getType() - 1] == self.BUILDER) and
                               ((b.getX() < 4 and self.playerID() == 0) or (b.getX() >= 36 and self.playerID() == 1)) ]

        self.big_bots_ids = [b.getPartOf() for b in self.bots if b.getOwner() == self.playerID() if b.getPartOf() != 0 ]
        self.big_bots = [b for b in self.my_bots if (b.getId() in self.big_bots_ids)]
        self.big_constructors = [b for b in self.big_bots if ((b.getX() < 4 and self.playerID() == 0) or (b.getX() >= 36 and self.playerID() == 1)) and b.getBuildRate > 0]
        self.constructors.extend(self.big_constructors)

        self.destructors = list(set(self.my_bots)-set(self.constructors))
        #[b for b in self.bots if b.getOwner() == self.playerID() and ((b.getType() > 0 and self.types[b.getType() - 1] != s-elf.BUILDER) or ]
        self.enemy_bots = [b for b in self.bots if b.getOwner() != self.playerID() and b.getPartOf() == 0]

        for bot in self.my_bots:
            bot.talk("My ID: %s size:%s"  %(str(bot.getId()), bot.getSize()))
            
        for bot in self.constructors:
            bot.talk("I'm a constructor")
        
        for bot in self.big_bots:
            bot.talk("I'm a BIG boy bot")
            
        for bot in self.destructors:
            bot.talk("I'm a destructors")

        #for frame in self.frames:
            #if frame.getOwner() == self.playerID():
                #frame.talk("My ID: " + str(frame.getId()))

        self.print_game_state()
        self.init_map()
       

    def turn_end(self):        
        print "====================================\n"
        pass

    def print_map(self):
        for y in range(self.boardY()):
            for x in range(5):
                if self.map[x][y] == None:
                    print ' |',
                elif self.map[x][y].getOwner() == self.playerID():
                    print 'b|',
                elif self.map[x][y].getOwner() == -1:
                    print 'w|',
                else:
                    print 'e|',
            print
        pass

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
                    #print "map(%i,%i) = %i" % (object.getX()+x, object.getY()+y, object.getId())
                    self.map[object.getX()+x][object.getY()+y] = object

        for object in self.frames:
            for x in range(object.getSize()):
                for y in range(object.getSize()):
                    self.map[object.getX()+x][object.getY()+y] = object

        for object in self.walls:
            self.map[object.getX()][object.getY()] = object

        #self.print_map()


    def nearest_object(self, bot, object_list):
        if len(object_list) == 0:
            return None
        return min(object_list,
                   key=lambda t: util.distance(bot.getX(), bot.getY(), bot.getSize(),
                                               t.getX(), t.getY(), t.getSize()) )

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
                                               
    def move_horizontal(self, bot, target):
        if( bot.getX() > target.getX() ):
            if self.objects_in_direction(bot,'l') == []:
                self.my_move(bot, 'l')
                return True
            return False
        else:
            if self.objects_in_direction(bot,'r') == []:
                self.my_move(bot, 'r')
                return True
            return False

    def move_vertical(self, bot, target):
        if( bot.getY() > target.getY() ):
            if self.objects_in_direction(bot,'u') == []:
                self.my_move(bot, 'u')
                return True
            return False
        else:
            if self.objects_in_direction(bot,'d') == []:
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


    def check_clear(self, x, y, size):
        if x < 0:
            return False
        if y < 0:
            return False
        if x+size > self.boardX():
            return False
        if y+size > self.boardY():
            return False
        for i in xrange(x,x+size):
            for j in xrange(y,y+size):
                if( self.map[i][j] != None ):
                    return False
        return True


    def my_build(self, bot, type, x, y, size):
        if( self.check_clear(x, y, size) ):
            if bot.getBuildRate() <= 0:
                return False
            bot.build(type, x, y, size)
            for i in xrange(x,x+size):
                for j in xrange(y,y+size):
                    self.map[i][j] = type
            return True
        return False


    def my_move(self, bot, direction):
        direction = self.relative_direction(direction)

        self.map[bot.getX()][bot.getY()] = None
        bot.move(direction)
        self.map[bot.getX()][bot.getY()] = bot

    def check_for_combine(self):
        #next power of 2
        if self.playerID() == 0:
            if self.player0Time() < 6:
                return
        elif self.playerID() == 1:
            if self.player1Time() < 6:
                return
        for bot in self.my_bots:
            x = bot.getX()
            y = bot.getY()
            s = bot.getSize()
            mod_size = bot.getSize() * 2
            if (bot.getX() % mod_size == 0 and bot.getY() % mod_size == 0) or (bot.getX() > 3 and self.playerID() == 0) or (bot.getX < 36 and self.playerID() == 1):
                bot1 = self.map[x+s][y]
                bot2 = self.map[x][y+s]
                bot3 = self.map[x+s][y+s]
                #print "x:%s y:%s s:%s" % (x, y, s)
                if bot1 in self.my_bots and bot2 in self.my_bots and bot3 in self.my_bots:
                    #print "bot(%i,%i) bot2(%i,%i) bot3(%i,%i) bot4(%i,%i)" % (bot.getX(), bot.getY(), bot1.getX(), bot1.getY(),bot2.getX(), bot2.getY(),bot3.getX(), bot3.getY())
                    if bot1.getX() != x+s or bot1.getY() != y   or bot1.getSize() != bot.getSize():
                        continue
                    if bot2.getX() != x   or bot2.getY() != y+s or bot2.getSize() != bot.getSize():
                        continue
                    if bot3.getX() != x+s or bot3.getY() != y+s or bot3.getSize() != bot.getSize():
                        continue
                    #print "Combining bots (%i, %i, %i, %i)" % (bot.getId(), bot1.getId(), bot2.getId(), bot3.getId())
                    bot.combine(bot1, bot2, bot3)
                    #bot.talk("Combining bots (%i, %i, %i, %i)" % (bot.getId(), bot1.getId(), bot2.getId(), bot3.getId()))
                    remove_list = [bot, bot1, bot2, bot3]
                    for bot in remove_list:
                        if bot in self.my_bots:
                            self.my_bots.remove(bot)
                        if bot in self.constructors:
                            self.constructors.remove(bot)
                        if bot in self.destructors:
                            self.destructors.remove(bot)
                else:
                    pass#print "Bots not in constructors (none?)"
            else:
                pass#print "bot not at mod:%s" % (bot.getId())

    def open_cooridantes_horizontal(self, bot, x, y):
        if( bot.getX() > x ):
            if( self.map[bot.getX()-1][bot.getY()] == None ):
                return bot.getX()-1, bot.getY()
                #self.my_move(bot, 'l')
                #return True
            return -1, -1
        else:
            if( self.map[bot.getX()+1][bot.getY()] == None ):
                return bot.getX() + 1, bot.getY()
                #self.my_move(bot, 'r')
                #return True
            return -1, -1

    def open_cooridantes_vertical(self, bot, x, y):
        if( bot.getY() > y ):
            if( self.map[bot.getX()][bot.getY()-1] == None ):
                return bot.getX(), bot.getY()-1
            return -1, -1
        else:
            if( self.map[bot.getX()][bot.getY()+1] == None ):
                return bot.getX(), bot.getY()+1
            return -1, -1

    def open_cooridantes_toward(self, bot, x, y):
        deltaX = math.fabs( bot.getX() - x )
        deltaY = math.fabs( bot.getY() - y )
        if( deltaX <= deltaY):
            x,y = self.open_cooridantes_vertical(bot, x, y)
            if x == -1:
                x,y = self.open_cooridantes_horizontal(bot, x, y)
        elif( deltaY < deltaX ):
            x,y = self.open_cooridantes_horizontal(bot, x, y)
            if x == -1:
                x,y = self.open_cooridantes_vertical(bot, x, y)
        return x,y

    def check_for_wall(self, bot):
        x = bot.getX()
        y = bot.getY()
        #wall = self.get_closest_wall(bot)
        wall = self.nearest_object(bot, self.walls )
        near_scrubber = self.nearest_object(wall, self.my_bots)
        #build scrubber towards that is close and not already being scrubbed
        if wall and util.distance(bot.getX(), bot.getY(), bot.getSize(), wall.getX(), wall.getY(), wall.getSize()) <= 2 :#and \
                    #util.distance(near_scrubber.getX(), near_scrubber.getY(), near_scrubber.getSize(), wall.getX(), wall.getY(), wall.getSize())  != 1:
            #bot.talk("wall 2 away, building scrubber")
            #get coordinates that are open and in the direction of the wall
            x, y = self.open_cooridantes_toward(bot, wall.getX(), wall.getY())
            #bot.talk("open @ (%i, %i)" % (x,y))
            #if we actually build there, return true
            if self.my_build(bot, self.DAMAGE, x, y, bot.getSize()):
                #bot.talk('built scrubber @ (%i, %i) towards wall ' % (x, y) )
                return True

                '''#check down
                if y+bot.getSize() < self.boardY() and self.my_build(bot, self.DAMAGE, x, y+bot.getSize(),  bot.getSize()):
                    bot.talk('built scrubber down @ (%i, %i)' % (x, y+bot.getSize()) )
                    return True
                #check up
                elif y-bot.getSize() >= 0 and self.my_build(bot, self.DAMAGE, x, y-bot.getSize(),  bot.getSize()):
                    bot.talk('built scrubber up @ (%i, %i)' % (x, y-bot.getSize()) )
                    return True'''
        return False
        
    def nearest_injured_ally(self,bot):
        injured_allies = [b for b in self.my_bots if b.getHealth() < b.getMaxHealth()]
        return self.nearest_object(bot,injured_allies)

    def destructor_action(self, bot):
        target = self.nearest_object(bot, self.walls + self.enemy_bots )

        if target:
            target_distance = util.distance( bot.getX(), bot.getY(), bot.getSize(),
                                         target.getX(), target.getY(), target.getSize() )
            if target_distance == 1 :
                objects = [b for b in self.objects_in_direction(bot,'t') if b in self.bots and b.getOwner() != self.playerID()]
                if len(objects) >= 2:
                   self.my_move(bot,'t')
            if bot.getHealth() < (bot.getMaxHealth()) and bot.getBuildRate() > 0:
                bot.heal(bot)
            #bot.talk( "target id: %s (%s, %s) distance: %i" % (target.getId(), target.getX(), target.getY(), target_distance) )
            elif( target_distance <= bot.getRange() + 1 ):
                bot.talk( "ATK: target id: %s (%s, %s) distance: %i" % (target.getId(), target.getX(), target.getY(), target_distance) )
                bot.attack(target)
            else:
                heal_target = self.nearest_injured_ally(bot)
                if heal_target:
                    heal_target_distance = util.distance( bot.getX(), bot.getY(), bot.getSize(),
                                             heal_target.getX(), heal_target.getY(), heal_target.getSize() )
                    if( target_distance <= bot.getRange() + 1 and bot.getBuildRate() > 0 ):
                        bot.talk( "HEAL: target id: %s (%s, %s) distance: %i" % (heal_target.getId(), heal_target.getX(), healt_target.getY(), heal_target_distance) )
                        bot.heal(heal_target)
            if( target_distance > 1 ):
                if not self.move_towards(bot, target):
                    pass#self.move_random(bot)
            
    def constructor_action(self, bot):
        #build up or down if empty
        x = bot.getX()
        y = bot.getY()
        size = bot.getSize()
        #if wall nearby, build scrubber towards wall
        if self.walls and self.check_for_wall(bot):
            #bot.talk("Building scrubber for wall")
            return
        
        while size > 0:
            #check away
            if x+(size*self.away) >= 0 and x+(size*self.away) < self.boardX() and self.my_build(bot, self.BUILDER, x+(size*self.away), y, size):
                #bot.talk('built away @ (%i, %i)' % (x+(bot.getSize()*self.away), y) )
                break
            #check down
            elif y+size < self.boardY() and self.my_build(bot, self.BUILDER, x, y+size, size):
                 #bot.talk('built down @ (%i, %i)' % (x, y+bot.getSize()) )
                 break
            #check up
            elif y-size >= 0 and self.my_build(bot, self.BUILDER, x, y-size,  size):
                 #bot.talk('built up @ (%i, %i)' % (x, y-size) )
                 break
            else:
                size -= 1
                

    def constructor_second_pass(self, bot):
        xb = bot.getX() + self.towards*bot.getSize()
        yb = bot.getY()
        size = bot.getSize()/2
        if size <= 0:
            size = 1
        #build destructor
        
        if self.towards == -1 and (bot.getX() - size) >= 0: # Player one
            xb = bot.getX() - size;
        
        if bot.getActions > 0:
            for y in xrange(yb,min(self.boardY(),yb+bot.getSize())):
                if not self.check_clear(xb,y,size):
                    continue;            
                #bot.talk('building destructor forward')
                
                if self.my_build(bot, random.choice(self.selector), xb, y, size):
                    return

    def run(self):
        self.turn_begin()
        self.check_for_combine()
        for constructor in self.constructors:
            self.constructor_action(constructor)

        for constructor in self.constructors:
            self.constructor_second_pass(constructor)

        for destructor in self.destructors:
            self.destructor_action(destructor)

        self.turn_end()

        return 1

    def __init__(self, conn):
        BaseAI.__init__(self, conn)
