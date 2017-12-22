from pbge.plots import Plot, Chapter, PlotState
import waypoints
import ghterrain
import gears
import pbge
from .. import teams,ghdialogue
from ..ghdialogue import context
from pbge.scenes.movement import Walking, Flying, Vision
from gears.geffects import Skimming, Rolling
import random
import copy
import os
from pbge.dialogue import Cue,ContextTag,Offer,Reply



# ********************************
# ***   TERRAIN  DEFINITIONS   ***
# ********************************

class WinterMochaSnowdrift( pbge.scenes.terrain.HillTerrain ):
    altitude = 20
    image_middle = 'terrain_wintermocha_snowdrift.png'
    bordername = ''
    blocks = (Walking,Skimming,Rolling)

class WinterMochaHangarTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_top = 'terrain_wintermocha_hangar.png'
    blocks = (Walking,Skimming,Rolling,Flying)

class WinterMochaHangar(pbge.randmaps.terrset.TerrSet):
    TERRAIN_TYPE = WinterMochaHangarTerrain
    TERRAIN_MAP = (
        (0,1),
        (2,3,4),
        (5,6,7,8),
        (9,10,11,12,13,14),
        (15,16,17,18,19,20),
        (21,22,23,24,25,26),
        (None,27,28,29,30,31),
        (None,None,32,33,34,35),
        (None,None,36,37,38,39),
        (None,None,WinterMochaSnowdrift,WinterMochaSnowdrift,WinterMochaSnowdrift)
    )
    WAYPOINT_POS = {
        "DOOR": (3,8), "DRIFT": (3,9)
    }

class WinterMochaFenceTerrain(pbge.scenes.terrain.TerrSetTerrain):
    image_top = 'terrain_wintermocha_fence.png'
    blocks = (Walking,Skimming,Rolling,Flying)

class WinterMochaFence(pbge.randmaps.terrset.TerrSet):
    TERRAIN_TYPE = WinterMochaFenceTerrain
    TERRAIN_MAP = (
        (0,),
        (1,),
        (2,),
    )
    WAYPOINT_POS = {
        "DOOR": (0,1)
    }

class WinterMochaBurningBarrelTerrain( pbge.scenes.terrain.AnimTerrain ):
    frames = (6,7)
    anim_delay = 2
    image_top = 'terrain_wintermocha.png'
    blocks = (Walking,Skimming,Rolling)

class WinterMochaBurningBarrel( waypoints.Waypoint ):
    TILE = pbge.scenes.Tile( None, None, WinterMochaBurningBarrelTerrain )
    desc = "There's a fire in this barrel. It's nice and warm."

class WinterMochaGeneratorTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 4
    blocks = (Walking,Skimming,Rolling)

class WinterMochaGenerator( waypoints.Waypoint ):
    TILE = pbge.scenes.Tile( None, None, WinterMochaGeneratorTerrain )
    desc = "You stand before a geothermal generator."

class WinterMochaToolbox( waypoints.Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.WinterMochaToolboxTerrain )
    desc = "You stand before an abandoned toolbox."

class WinterMochaHeatLampTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 5
    blocks = (Walking,Skimming,Rolling)

class WinterMochaHeatLamp( waypoints.Waypoint ):
    TILE = pbge.scenes.Tile( None, None, WinterMochaHeatLampTerrain )
    desc = "You stand before an industrial heat lamp. It's probably being used in the construction of the new arena."

class WinterMochaBarrel( waypoints.Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.WinterMochaBarrelTerrain )
    desc = "You stand before a big container of fuel."

class WinterMochaShovel( waypoints.Waypoint ):
    TILE = pbge.scenes.Tile( None, None, ghterrain.WinterMochaBrokenShovel )
    desc = "You stand before a broken shovel."

class WinterMochaDomeTerrain(pbge.scenes.terrain.Terrain):
    image_top = 'terrain_wintermocha.png'
    frame = 3
    blocks = (Walking,Skimming,Rolling)

class WinterMochaDome( waypoints.Waypoint ):
    TILE = pbge.scenes.Tile( None, None, WinterMochaDomeTerrain )
    desc = "You stand before a half buried dome. No idea what its function is."

# *****************
# ***   PLOTS   ***
# *****************

class MochaStub( Plot ):
    LABEL = "SCENARIO_MOCHA"
    # Creates a Winter Mocha adventure.
    # - Play starts in Mauna, near Vikki and Hyolee.
    #   - The good mecha are snowed into the hangar.
    #   - The bad mecha are in the parking lot.
    # - Head out to battle some raiders.
    # - Win or lose, the end.

    def custom_init( self, nart ):
        """Create the world + starting scene."""
        w = nart.camp
        self.register_element( "WORLD", w )
        self.chapter = Chapter( world=w )
        self.add_first_locale_sub_plot( nart, locale_type="MOCHA_MAUNA" )


        return True

class FrozenHotSpringCity( Plot ):
    # Mauna in winter. There was a heavy snowfall last night, and the mecha
    # hangar is blocked.
    LABEL = "MOCHA_MAUNA"
    active = True
    scope = True
    def custom_init( self, nart ):
        """Create map, fill with city + services."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(60,60,"Mauna",player_team=team1,scale=gears.scale.HumanScale)

        myfilter = pbge.randmaps.converter.BasicConverter(WinterMochaSnowdrift)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.SmallSnow,myfilter,mutate=mymutate)
        myscenegen = pbge.randmaps.SceneGenerator(myscene,myarchi)


        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        myroom = pbge.randmaps.rooms.FuzzyRoom(10,10)

        myent = self.register_element( "ENTRANCE", WinterMochaBurningBarrel(anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append( myent )

        vikki = gears.base.Character(name="Vikki",statline={gears.stats.Reflexes:15,
         gears.stats.Body:10,gears.stats.Speed:13,gears.stats.Perception:13,
         gears.stats.Knowledge:10,gears.stats.Craft:10,gears.stats.Ego:10,
         gears.stats.Charm:12,gears.stats.MechaPiloting:7,gears.stats.MechaGunnery:7,
         gears.stats.MechaFighting:7})
        vikki.imagename = 'cha_wm_vikki.png'
        vikki.portrait = 'por_f_wintervikki.png'
        vikki.colors = (gears.color.ShiningWhite,gears.color.LightSkin,gears.color.NobleGold,gears.color.HunterOrange,gears.color.Olive)
        vikki.mmode = pbge.scenes.movement.Walking
        myroom.contents.append(vikki)
        self.register_element( "VIKKI", vikki )

        myscenegen.contents.append(myroom)

        hangar_gate = self.register_element("HANGAR_GATE",waypoints.Waypoint(plot_locked=True,desc="This is the door of the mecha hangar."))
        snow_drift = self.register_element("SNOW_DRIFT",waypoints.Waypoint(desc="The snow has blocked the entrance to the mecha hangar. You're going to have to take one of the backup mecha from the storage yard."))
        myroom2 = pbge.randmaps.rooms.FuzzyRoom(15,15)
        myroom3 = WinterMochaHangar(parent=myroom2,waypoints={"DOOR":hangar_gate,"DRIFT":snow_drift})
        myscenegen.contents.append(myroom2)

        fence_gate = self.register_element("FENCE_GATE",waypoints.Waypoint(plot_locked=True,desc="This is the gate of the mecha storage yard."))

        myroom4 = pbge.randmaps.rooms.FuzzyRoom(6,5,anchor=pbge.randmaps.anchors.northwest,parent=myscenegen)
        myroom5 = WinterMochaFence(parent=myroom4,anchor=pbge.randmaps.anchors.west,waypoints={'DOOR':fence_gate})

        # I don't know why I added a broken shovel. Just thought it was funny.
        myroom6 = pbge.randmaps.rooms.FuzzyRoom(3,3,parent=myscenegen)
        if random.randint(1,3) != 1:
            myroom6.contents.append(WinterMochaShovel(anchor=pbge.randmaps.anchors.middle))
        else:
            myroom6.contents.append(WinterMochaDome(anchor=pbge.randmaps.anchors.middle))

        # Add the puzzle to get through the snowdrift.
        #
        # Bibliography for procedural puzzle generation:
        # Isaac Dart, Mark J. Nelson (2012). Smart terrain causality chains for adventure-game puzzle generation. In Proceedings of the IEEE Conference on Computational Intelligence and Games, pp. 328-334.
        # Clara Fernandez-Vara and Alec Thomson. 2012. Procedural Generation of Narrative Puzzles in Adventure Games: The Puzzle-Dice System. In Proceedings of the The third workshop on Procedural Content Generation in Games (PCG '12).
        self.add_sub_plot( nart, "MELT", PlotState( elements={"TARGET":snow_drift} ).based_on( self ) )

        self.add_sub_plot( nart, "MOCHA_MISSION", PlotState( elements={"CITY":myscene} ).based_on( self ), ident="COMBAT" )

        self.did_opening_sequence = False
        self.got_vikki_history = False
        self.got_vikki_mission = False

        return True

    def SNOW_DRIFT_MELT( self, camp ):
        scene = self.elements["LOCALE"]
        drift = self.elements["SNOW_DRIFT"]
        scene._map[drift.pos[0]][drift.pos[1]].wall = None
        scene._map[drift.pos[0]-1][drift.pos[1]].wall = None
        scene._map[drift.pos[0]+1][drift.pos[1]].wall = None

    def FENCE_GATE_menu(self,thingmenu):
        thingmenu.add_item('Board a mecha and start mission',self._give_bad_mecha)
        thingmenu.add_item("Don't start mission yet",None)

    def HANGAR_GATE_menu(self,thingmenu):
        thingmenu.add_item('Board a mecha and start mission',self._give_good_mecha)
        thingmenu.add_item("Don't start mission yet",None)

    def _give_bad_mecha(self,camp):
        # Give the PC some cheapass mecha.
        mygearlist = gears.Loader.load_design_file('BuruBuru.txt')+gears.Loader.load_design_file('Claymore.txt')
        random.shuffle(mygearlist)
        mek1 = mygearlist[0]
        mek2 = mygearlist[1]
        mek1.colors = gears.random_mecha_colors()
        mek2.colors = (gears.color.ShiningWhite,gears.color.Olive,gears.color.ElectricYellow,gears.color.GullGrey,gears.color.Terracotta)
        mek1.pilot = camp.pc
        mek2.pilot = self.elements["VIKKI"]
        camp.party += [mek1,mek2]

        self._go_to_mission(camp)

    def _give_good_mecha(self,camp):
        mek1 = gears.Loader.load_design_file('Zerosaiko.txt')[0]
        mek2 = gears.Loader.load_design_file('Thorshammer.txt')[0]
        mek1.colors = gears.random_mecha_colors()
        mek2.colors = (gears.color.ShiningWhite,gears.color.Olive,gears.color.ElectricYellow,gears.color.GullGrey,gears.color.Terracotta)
        mek1.pilot = camp.pc
        mek2.pilot = self.elements["VIKKI"]
        camp.party += [mek1,mek2]

        self._go_to_mission(camp)


    def _go_to_mission(self,camp):
        self.subplots["COMBAT"].enter_combat(camp)

    def VIKKI_offers(self,camp):
        # Return list of dialogue offers.
        mylist = list()

        mylist.append(Offer("[LONGTIMENOSEE] It's me, Vikki Shingo, from Hogye. Did they pull you out of bed for this mission too?",
            context=ContextTag([self]),
            replies=[Reply("What mission? What's going on?",destination=Cue(ContextTag([context.INFO,context.MISSION]))),
                Reply("Vikki! How's life been treating you?",destination=Cue(ContextTag([context.INFO,context.PERSONAL])))
            ]))

        if not self.got_vikki_mission:
            mylist.append(Offer("Some bandits are attacking a convoy down on the Gyori Highway. Because of the blizzard last night, the Guardians are tied up with disaster relief. Even worse, the hangar where my and probably your mecha are stored is snowed under.",
                context=ContextTag([context.INFO,context.MISSION]), data={"subject":"mission",},
                replies = [
                    Reply("[DOTHEYHAVEITEM]",
                     destination=Offer("Yeah, they do have snow clearing equipment... it's in the same hangar as our mecha. Not to worry, though- the junker meks we used in the charity game are in the storage yard, so we can use them.", context=ContextTag([context.MISSION,context.PROBLEM]),data={"item":"snow clearing equipment",})
                    ),
                    Reply("[IWILLDOMISSION]",
                     destination=Offer("[GOODLUCK] I'm going back to bed.", context=ContextTag([context.GOODBYE,context.MISSION]),data={"mission":"fight the bandits"})
                    ),
                ], effect = self._get_vikki_mission
                 ))
        else:
            mylist.append(Offer("You should have had a cup of coffee. There are bandits on the Gyori Highway, you can get a mecha to use from the storage yard up north.",
                context=ContextTag([context.INFO,context.MISSION]), data={'subject':'bandits'} ))


        if not self.got_vikki_history:
            mylist.append(Offer("I've been doing alright. I'm working for the Defense Force nearly full time now... Haven't gotten over the heartbreak of losing my Ovaknight to Typhon, but I did some work on the old Thorshammer.",
                context=ContextTag([context.INFO,context.PERSONAL]), data={'subject':'past six months'}, effect=self._ask_vikki_history ))

        if self.elements["VIKKI"] not in camp.party:
            mylist.append(Offer("Alright, I'll go with you. Between the two of us this should be no problem.",
                context=ContextTag([context.JOIN]), effect=self._vikki_join ))

        return mylist

    def _get_vikki_mission(self,camp):
        self.got_vikki_mission = True

    def _ask_vikki_history(self,camp):
        self.got_vikki_history = True

    def _vikki_join(self,camp):
        camp.party.append(self.elements["VIKKI"])

    def t_START(self,camp):
        if not self.did_opening_sequence:
            pbge.alert("December 23, NT157. It's been an awful year for the Federated Territories of Earth.")
            pbge.alert("An ancient bioweapon named Typhon was awakened from stasis and rampaged through several cities. Fortunately, a team of cavaliers was able to destroy it before it reached Snake Lake. You were there.")
            pbge.alert("Now, six months later, you are meeting with several of your former lancemates for a charity mecha tournament in the recently constructed Mauna Arena.")
            pbge.alert("At 5AM, alarms go off through the hotel. You rush outside to see what's going on.")

            npc = self.elements["VIKKI"]
            cviz = ghdialogue.ghdview.ConvoVisualizer(npc)
            cviz.rollout()
            convo = pbge.dialogue.Conversation(camp,npc,camp.pc,Cue(ContextTag([self])),visualizer=cviz)
            convo.converse()

            self.did_opening_sequence = True

class WinterBattle( Plot ):
    # Go fight mecha near Mauna.
    LABEL = "MOCHA_MISSION"
    active = True
    scope = "LOCALE"
    def custom_init( self, nart ):
        """Create map, fill with city + services."""
        team1 = teams.Team(name="Player Team")
        myscene = gears.GearHeadScene(60,60,"Near Mauna",player_team=team1,scale=gears.scale.MechaScale)

        myfilter = pbge.randmaps.converter.BasicConverter(ghterrain.Forest)
        mymutate = pbge.randmaps.mutator.CellMutator()
        myarchi = pbge.randmaps.architect.Architecture(ghterrain.Snow,myfilter,mutate=mymutate,prepare=pbge.randmaps.prep.HeightfieldPrep(ghterrain.Water,ghterrain.SmallSnow,ghterrain.Snow))
        myscenegen = pbge.randmaps.SceneGenerator(myscene,myarchi)

        self.register_scene( nart, myscene, myscenegen, ident="LOCALE" )

        myroom = pbge.randmaps.rooms.FuzzyRoom(10,10,parent=myscene,anchor=pbge.randmaps.anchors.south)
        myent = self.register_element( "ENTRANCE", waypoints.Waypoint(anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append( myent )

        boringroom = pbge.randmaps.rooms.FuzzyRoom(5,5,parent=myscene)

        mygoal = pbge.randmaps.rooms.FuzzyRoom(10,10,parent=myscene,anchor=pbge.randmaps.anchors.north)
        team2 = teams.Team(enemies=(team1,))
        boss_mecha = self.register_element("BOSS",gears.Loader.load_design_file('Blitzen.txt')[0])
        boss_mecha.load_pilot(gears.random_pilot())
        mygoal.contents.append(boss_mecha)
        myscene.local_teams[boss_mecha] = team2

        return True

    def t_FIGHTOVER(self,camp):
        myboss = self.elements["BOSS"]
        if not myboss.is_operational():
            pbge.alert("Victory! Thank you for trying GearHead Caramel. Keep watching for more updates.")
        elif not camp.first_active_pc():
            pbge.alert("Game over. Better luck next time.")
    def t_START(self,camp):
        pass

    def enter_combat( self, camp ):
        camp.destination = self.elements["LOCALE"]
        camp.entrance = self.elements["ENTRANCE"]


#  ************************
#  ***   PUZZLE  BITS   ***
#  ************************
#
# A PuzzleBit subplot takes a "TARGET" element and does some kind of thing
# to it. When the action is successfully done, it sends a trigger back to
# the plot that generated it.

class MeltWithHeat( Plot ):
    # Heat should be able to melt a snowdrift. This MELT plot request just
    # branches the request to either a HEAT or a WIND plot, which is kind of a
    # kludgey way to handle things but I wanted to make this division explicit
    # so you can see clearly how the puzzle generator works from this
    # not-much-content example.
    LABEL = "MELT"
    active = True
    scope = True
    def custom_init( self, nart ):
        self.add_sub_plot( nart, "HEAT" )
        return True
    def TARGET_HEAT(self,camp):
        camp.check_trigger( "MELT", self.elements[ "TARGET" ])
        self.active = False

class MeltWithWind( Plot ):
    # See above.
    LABEL = "MELT"
    active = True
    scope = True
    def custom_init( self, nart ):
        self.add_sub_plot( nart, "WIND" )
        return True
    def TARGET_WIND(self,camp):
        camp.check_trigger( "MELT", self.elements[ "TARGET" ])
        self.active = False

class BurnTheBarrels( Plot ):
    # Burn down the malls! Burn down the malls!
    LABEL = "HEAT"
    active = True
    scope = True
    def custom_init( self, nart ):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",WinterMochaBarrel(plot_locked=True,anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        self.add_sub_plot( nart, "IGNITE", PlotState( elements={"TARGET":puzzle_item} ).based_on( self ) )
        return True
    def PUZZITEM_IGNITE(self,camp):
        pbge.alert("The barrel of fuel fires up, melting some of the nearby snow.")
        scene = self.elements["LOCALE"]
        barrel = self.elements["PUZZITEM"]
        scene._map[barrel.pos[0]][barrel.pos[1]].decor = WinterMochaBurningBarrelTerrain
        camp.check_trigger( "HEAT", self.elements[ "TARGET" ])
        self.active = False

class IndustrialStrengthHeater( Plot ):
    # Activate an industrial heat lamp to get rid of some snow
    LABEL = "HEAT"
    active = True
    scope = True
    def custom_init( self, nart ):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",WinterMochaHeatLamp(plot_locked=True,anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        self.add_sub_plot( nart, "ENERGIZE", PlotState( elements={"TARGET":puzzle_item} ).based_on( self ) )
        return True
    def PUZZITEM_ENERGIZE(self,camp):
        pbge.alert("The industrial heat lamp fires up, melting some of the nearby snow.")
        camp.check_trigger( "HEAT", self.elements[ "TARGET" ])
        self.active = False

class IndustrialStrengthBlower( Plot ):
    # Activate an industrial blower for an artificial chinook.
    LABEL = "WIND"
    active = True
    scope = True
    def custom_init( self, nart ):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",WinterMochaHeatLamp(plot_locked=True,anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        self.add_sub_plot( nart, "ENERGIZE", PlotState( elements={"TARGET":puzzle_item} ).based_on( self ) )

        return True
    def PUZZITEM_ENERGIZE(self,camp):
        pbge.alert("The industrial blower roars into action, melting some of the nearby snow.")
        camp.check_trigger( "WIND", self.elements[ "TARGET" ])
        self.active = False


class OpenGeothermalVent( Plot ):
    # Open the geothermal generator, let the steam out.
    LABEL = "WIND"
    active = True
    scope = True
    def custom_init( self, nart ):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",WinterMochaGenerator(plot_locked=True,anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        self.add_sub_plot( nart, "OPEN", PlotState( elements={"TARGET":puzzle_item} ).based_on( self ) )

        return True
    def PUZZITEM_OPEN(self,camp):
        pbge.alert("A sudden blast of steam escapes from the geothermal vent, melting some of the nearby snow.")
        camp.check_trigger( "WIND", self.elements[ "TARGET" ])
        self.active = False

class LazyassOpener( Plot ):
    # You want to open this thing? Just open it.
    # Not much of a puzzle, but if I'm gonna get this demo released this week...
    LABEL = "OPEN"
    active = True
    scope = True
    def TARGET_menu(self,thingmenu):
        thingmenu.add_item('Try to open it',self._try_open)
    def _try_open(self,camp):
        pbge.alert("You open it easily. Who leaves stuff like this unlocked?!")
        camp.check_trigger( "OPEN", self.elements[ "TARGET" ])
        self.active = False


class UniversalLockpick( Plot ):
    # You know what opens stuff? A crowbar.
    # Since this is just a demo, we're just simulating the key items.
    LABEL = "OPEN"
    active = True
    scope = True
    def custom_init( self, nart ):
        puzzle_item = self.register_element("PUZZITEM","Crowbar")
        self.add_sub_plot( nart, "FIND", PlotState( elements={"TARGET":puzzle_item} ).based_on( self ), ident="FINDER" )
        self.found_item = False
        return True
    def TARGET_menu(self,thingmenu):
        if self.found_item:
            thingmenu.add_item('Open it with the crowbar',self._open_thing)
        else:
            thingmenu.add_item('Try to open it',self._try_open)

    def _open_thing(self,camp):
        pbge.alert("The crowbar makes short work of the lock.")
        camp.check_trigger( "OPEN", self.elements[ "TARGET" ])
        self.active = False
    def _try_open(self,camp):
        pbge.alert("It's locked.")
        self.subplots["FINDER"].active = True
    def PUZZITEM_FIND(self,camp):
        self.found_item = True

class FindAbandonedToolbox( Plot ):
    # The item you seek is in an abandoned toolbox.
    LABEL = "FIND"
    active = True
    scope = True
    def custom_init( self, nart ):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",WinterMochaToolbox(plot_locked=True,anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        return True
    def get_crowbar(self,camp):
        pbge.alert("You take the {}. It might be useful for something.".format(self.elements["TARGET"]))
        camp.check_trigger( "FIND", self.elements[ "TARGET" ])
        self.active = False
    def PUZZITEM_menu(self,thingmenu):
        thingmenu.desc = '{} There is a {} inside.'.format(thingmenu.desc,self.elements["TARGET"])
        thingmenu.add_item('Borrow the {}'.format(self.elements["TARGET"]),self.get_crowbar)

class BorrowAnItem( Plot ):
    # The item you seek is in an abandoned toolbox.
    LABEL = "FIND"
    active = False
    scope = True
    def custom_init( self, nart ):
        mynpc = self.seek_element(nart,"NPC",self._seek_npc)
        return True
    def _seek_npc( self, candidate ):
        return isinstance( candidate, gears.base.Character )
    def _get_item( self, camp ):
        camp.check_trigger( "FIND", self.elements[ "TARGET" ])
        self.active = False
    def NPC_offers(self, camp ):
        mylist = list()
        mylist.append( pbge.dialogue.Offer('Sure, here you go.',context=pbge.dialogue.ContextTag((ghdialogue.context.ASK_FOR_ITEM,)),data={'item':self.elements["TARGET"]},effect=self._get_item))
        return mylist

class ExtensionCord( Plot ):
    # Have you tried plugging it in?
    LABEL = "ENERGIZE"
    active = True
    scope = True
    def custom_init( self, nart ):
        puzzle_item = self.register_element("PUZZITEM","Extension Cord")
        self.add_sub_plot( nart, "FIND", PlotState( elements={"TARGET":puzzle_item} ).based_on( self ), ident="FINDER" )
        self.found_item = False
        return True
    def TARGET_menu(self,thingmenu):
        if self.found_item:
            thingmenu.add_item('Plug it in and turn it on',self._open_thing)
        else:
            thingmenu.add_item('Try to turn it on',self._try_activate)
    def _open_thing(self,camp):
        pbge.alert("You connect it to the electrical outlet and press the power button...")
        camp.check_trigger( "ENERGIZE", self.elements[ "TARGET" ])
        self.active = False
    def _try_activate(self,camp):
        pbge.alert("Nothing happens. It doesn't have any power. You notice that it isn't plugged in.")
        self.subplots["FINDER"].active = True
    def PUZZITEM_FIND(self,camp):
        self.found_item = True

class CircuitBroken( Plot ):
    # The generator's offline; try wiggling the switch.
    LABEL = "ENERGIZE"
    active = True
    scope = True
    def custom_init( self, nart ):
        scene = self.elements["LOCALE"]
        myroom = self.register_element("_ROOM",pbge.randmaps.rooms.FuzzyRoom(5,5),dident="LOCALE")
        puzzle_item = self.register_element("PUZZITEM",WinterMochaGenerator(plot_locked=True,anchor=pbge.randmaps.anchors.middle))
        myroom.contents.append(puzzle_item)
        return True
    def TARGET_menu(self,thingmenu):
        thingmenu.add_item('Try to turn it on',self._try_activate)
    def _try_activate(self,camp):
        pbge.alert("Nothing happens. Everything seems to be connected properly, but it isn't getting any power.")
    def PUZZITEM_menu(self,thingmenu):
        thingmenu.desc = '{} The generator is currently off; the circuit breaker must have blown during the storm.'.format(thingmenu.desc)
        thingmenu.add_item("Turn it back on again",self._fix_generator)
        thingmenu.add_item("Leave it alone",None)
    def _fix_generator(self,camp):
        pbge.alert("You reset the controls, and the generator flickers back to life.")
        camp.check_trigger( "ENERGIZE", self.elements[ "TARGET" ])
        self.active = False

class OpenContainer( Plot ):
    # Let oxygen do all the heavy lifting.
    LABEL = "IGNITE"
    active = True
    scope = True
    def custom_init( self, nart ):
        self.add_sub_plot( nart, "OPEN", ident="OPENER" )
        return True
    def TARGET_menu(self,thingmenu):
        thingmenu.desc = '{} There is a large red warning label pasted to the front.'.format(thingmenu.desc)
        thingmenu.add_item('Read the warning label',self._try_activate)
        thingmenu.add_item('Leave it alone',None)
    def _try_activate(self,camp):
        pbge.alert("Warning: Contents will react violently when exposed to oxygen. Extreme caution should be used when handling.")
        self.subplots["OPENER"].active = True
    def TARGET_OPEN(self,camp):
        pbge.alert("You open it up and retreat to a safe distance as the fireworks begin.")
        camp.check_trigger( "IGNITE", self.elements[ "TARGET" ])
        self.active = False


class UseFlares( Plot ):
    # Easiest way to set something on fire is to set it on fire
    LABEL = "IGNITE"
    active = True
    scope = True
    def custom_init( self, nart ):
        puzzle_item = self.register_element("PUZZITEM","Flare")
        self.add_sub_plot( nart, "FIND", PlotState( elements={"TARGET":puzzle_item} ).based_on( self ), ident="FINDER" )
        self.found_item = False
        return True
    def TARGET_menu(self,thingmenu):
        thingmenu.desc = '{} There is a large yellow warning label pasted to the front.'.format(thingmenu.desc)
        if self.found_item:
            thingmenu.add_item('Place a lit flare in the barrel',self._open_thing)
            thingmenu.add_item('Leave it alone',None)
        else:
            thingmenu.add_item('Read the warning label',self._try_activate)
    def _open_thing(self,camp):
        pbge.alert("You stick the lit flare in the barrel's spigot and retreat to a safe distance...")
        camp.check_trigger( "IGNITE", self.elements[ "TARGET" ])
        self.active = False
    def _try_activate(self,camp):
        pbge.alert("Warning: Highly flammable. Keep away from sparks and open flame.")
        self.subplots["FINDER"].active = True
    def PUZZITEM_FIND(self,camp):
        self.found_item = True

