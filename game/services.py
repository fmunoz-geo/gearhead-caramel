import pygame
import gears
from gears import tags
from gears import champions
import random
import pbge
import copy
from . import shopui, fieldhq

MECHA_STORE = (tags.ST_MECHA,)
MEXTRA_STORE = (tags.ST_MECHA,tags.ST_MECHA_WEAPON)
ARMOR_STORE = (tags.ST_CLOTHING,)
WEAPON_STORE = (tags.ST_WEAPON,)
GENERAL_STORE = (tags.ST_WEAPON,tags.ST_CLOTHING,tags.ST_ESSENTIAL)
MECHA_PARTS_STORE = (tags.ST_MECHA_EQUIPMENT,)
MECHA_WEAPON_STORE = (tags.ST_MECHA_WEAPON,)
TIRE_STORE = (tags.ST_MECHA_MOBILITY,)
CYBERWARE_STORE = (tags.ST_CYBERWARE,)
GENERAL_STORE_PLUS_MECHA = (tags.ST_WEAPON,tags.ST_CLOTHING,tags.ST_ESSENTIAL,tags.ST_MECHA,tags.ST_MECHA_EQUIPMENT)
BARE_ESSENTIALS_STORE = (tags.ST_ESSENTIAL,)
PHARMACY = (tags.ST_MEDICINE,)
BLACK_MARKET = (tags.ST_WEAPON, tags.ST_CLOTHING, tags.ST_ESSENTIAL, tags.ST_CONTRABAND)

class Shop(object):
    MENU_AREA = pbge.frects.Frect(50, -200, 300, 300)

    def __init__(self, ware_types=MECHA_STORE, allow_misc=True, caption="Shop", rank=25, shop_faction=None,
                 num_items=10, turnover=1, npc=None, mecha_colors=None, sell_champion_equipment=False):
        self.wares = list()
        self.ware_types = ware_types
        self.allow_misc = allow_misc
        self.caption = caption
        self.rank = rank
        self.num_items = num_items
        self.turnover = turnover
        self.last_updated = -1
        self.npc = npc
        self.shopper = None
        self.shop_faction = shop_faction
        self.mecha_colors = mecha_colors or gears.color.random_mecha_colors()
        self.customer = None
        self.sell_champion_equipment = sell_champion_equipment


    def item_matches_shop(self, item, camp):
        myfaction = self.shop_faction or camp.scene.get_metro_scene().faction
        if item.get_full_name() in [a.get_full_name() for a in self.wares]:
            return False
        elif myfaction and hasattr(item, "faction_list"):
            if (myfaction.get_faction_tag() in item.faction_list) or (None in item.faction_list):
                return True
        else:
            return True

    def _pick_an_item(self, itype, rank, camp):
        candidates = [item for item in gears.selector.DESIGN_LIST if
                      itype in item.shop_tags and self.item_matches_shop(item, camp)]
        if candidates:
            # Step one: Sort the candidates by cost.
            random.shuffle(candidates)
            candidates.sort(key=lambda i: i.cost)
            # Step two: Determine this store's ideal index position.
            ideal_index = len(candidates) * min(max(rank,0),100) / 100.0
            # Step three: Create a new list sorted by distance from ideal_index.
            sorted_candidates = candidates.copy()
            sorted_candidates.sort(key=lambda i: abs(candidates.index(i) - ideal_index))
            # Step four: Choose an item, the lower the better.
            max_i = min(len(candidates)-1,max(5,len(candidates)//3))
            i = min(random.randint(0,max_i),random.randint(0,max_i),random.randint(0,max_i))
            it = copy.deepcopy(sorted_candidates[i])
            if isinstance(it, gears.base.Mecha):
                it.colors = self.mecha_colors
            if self.sell_champion_equipment and random.randint(1,3) == 1:
                if isinstance(it, gears.base.Mecha):
                    champions.upgrade_to_champion(it)
                elif it.scale == gears.scale.MechaScale and isinstance(it, (gears.base.Component, gears.base.Shield, gears.base.Launcher)):
                    champions.upgrade_item_to_champion(it)

            return it


    def generate_item(self, itype, rank, camp):
        tries = 0
        while tries < 10:
            it = self._pick_an_item(itype, rank, camp)
            # Avoid duplicates.
            if it and it.get_full_name() not in [a.get_full_name() for a in self.wares]:
                return it
            tries = tries + 1
        return it


    def update_wares(self, camp):
        # Once a day the wares get updated. Delete some items, make sure that
        # there's at least one item of every ware_type, and then fill up the
        # store to full capacity.

        # A lot of stuff about the wares is going to depend on the shopkeeper's
        # friendliness.
        if self.npc:
            friendliness = self.npc.get_reaction_score(camp.pc, camp)
        else:
            friendliness = 0

        # Find prosperity of the town, if possible.
        metro = camp.scene.get_metro_scene()
        if metro:
            prosperity = metro.metrodat.get_quality_of_life().prosperity
        else:
            prosperity = 0

        # The number of items is highly dependent on friendliness, or more
        # specifically a lack thereof.
        if friendliness < 0:
            num_items = max(5, (self.num_items * (100 + 2 * friendliness)) // 100)
        else:
            num_items = self.num_items + friendliness // 10

        if prosperity < 0:
            num_items = max(num_items+prosperity, 1)

        # Get rid of some of the old stock, to make room for new stock.
        while len(self.wares) > num_items:
            it = random.choice(self.wares)
            self.wares.remove(it)
        days = camp.day - self.last_updated
        for n in range(max(3, (random.randint(1, 6) + days) * self.turnover)):
            if self.wares:
                it = random.choice(self.wares)
                self.wares.remove(it)
            else:
                break

        rank = self.rank + prosperity * 10

        tries = 0
        while len(self.wares) < num_items:
            tries += 1
            itype = random.choice(self.ware_types)
            it = self.generate_item(itype, rank, camp)
            if it:
                self.wares.append(it)
            elif tries > 100:
                break

    def improve_friendliness(self, camp, item, modifier=0):
        """Dealing with a shopkeeper will generally increase friendliness."""
        if self.npc:
            target = abs( self.npc.get_reaction_score( self.customer, camp ) ) + 50
            roll = random.randint( 1, 100 ) + camp.get_party_skill(gears.stats.Charm,gears.stats.Negotiation) + modifier
            if roll > target:
                self.npc.relationship.reaction_mod += random.randint(1,6)

    def calc_purchase_price(self, camp, item):
        """The sale price of an item depends on friendliness. Min price = 70%"""
        it = item.cost
        if self.npc:
            f = self.npc.get_reaction_score(camp.pc, camp)
            if f < 0:
                it = (it * (120 - 2 * f)) // 100
            else:
                it = (it * (240 - f)) // 200
        return it

    def can_be_sold(self,item):
        if isinstance(item,gears.base.Being):
            return False
        elif hasattr(item,"pilot") and item.pilot:
            return False
        elif hasattr(item,"owner") and item.owner:
            return False
        else:
            return True

    def calc_sale_price(self, camp, it):
        # Max price = 60%
        percent = 46
        if self.npc:
            f = self.npc.get_reaction_score(camp.pc, camp)
            percent += f//7
        return max((it.cost * percent)//100 , 1)

    def enter_shop(self, camp):
        self.customer = camp.pc
        ui = shopui.ShopUI(camp, self)
        ui.activate_and_run()

    def update_shop(self, camp):
        if camp.day > self.last_updated:
            self.update_wares(camp)
            self.last_updated = camp.day

    def __call__(self, camp):
        self.update_shop(camp)
        self.enter_shop(camp)

class SkillButtonWidget(pbge.widgets.LabelWidget):
    def __init__(self, skill, clickfun, scolumn):
        super().__init__(0, 0, 170, 24, skill.name, on_click=clickfun, data=skill, font=pbge.BIGFONT)
        self.scolumn = scolumn

    def render( self ):
        if self is self.scolumn.active_button:
            pbge.draw_text(self.font,self.text,self.get_rect(),pbge.rpgmenu.MENU_SELECT_COLOR,self.justify)
        else:
            pbge.draw_text(self.font,self.text,self.get_rect(),pbge.rpgmenu.MENU_ITEM_COLOR,self.justify)


class SkillColumn(pbge.widgets.ColumnWidget):
    def __init__(self, skill_list, set_skill_fun):
        self.skill_list = skill_list
        self.set_skill_fun = set_skill_fun
        self.up_button = pbge.widgets.ButtonWidget(0, 0, 128, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), off_frame=1)
        self.down_button = pbge.widgets.ButtonWidget(0, 0, 128, 16, sprite=pbge.image.Image("sys_updownbuttons.png", 128, 16), frame=2, on_frame=2, off_frame=3)
        super().__init__(0, 0, 170, 200, padding=2, center_interior=True)
        self.skill_list_w = pbge.widgets.ScrollColumnWidget(0,0,170,160, up_button = self.up_button, down_button=self.down_button,)
        self.add_interior(self.up_button)
        self.add_interior(self.skill_list_w)
        self.add_interior(self.down_button)

        for sk in self.skill_list:
            self.skill_list_w.add_interior(SkillButtonWidget(sk, self.set_skill_wrapper, self))
        self.active_button = self.skill_list_w.children[0]

    def set_skill_wrapper(self, wid, ev):
        self.active_button = wid
        self.set_skill_fun(wid.data)


class SkillBuyWidget(pbge.widgets.LabelWidget):
    def __init__(self, cost, clickfun, trainer):
        super().__init__(0, 0, 150, 24, "${:,}".format(cost), on_click=clickfun, data=cost, font=pbge.MEDIUMFONT,
                         border=True, justify=0)
        self.trainer = trainer

    def render( self ):
        if self.data <= self.trainer.camp.credits and self.trainer.skill in self.trainer.pc.statline:
            pbge.widgets.widget_border_on.render(self.get_rect())
            pbge.draw_text(self.font,self.text,self.get_rect(),pbge.WHITE,self.justify)
        else:
            pbge.widgets.widget_border_off.render(self.get_rect())
            pbge.draw_text(self.font,self.text,self.get_rect(),pbge.GREY,self.justify)


class PlayerCharacterSwitchPlusSkillTrainingInfo(pbge.widgets.RowWidget):
    def __init__(self, camp, pc, set_pc_fun, trainer, **kwargs):
        super().__init__(0,0,350,100,**kwargs)
        self.trainer = trainer

        self.my_switch = fieldhq.backpack.PlayerCharacterSwitch(camp, pc, set_pc_fun)
        self.add_left(self.my_switch)
        self.add_right(pbge.widgets.LabelWidget(0,0,200,100,text_fun=self.get_label_text, justify=0, color=pbge.INFO_GREEN, font=pbge.BIGFONT))

    def get_label_text(self,wid):
        return "{}\n \n ${:,}\n {}: {}".format(str(self.my_switch.pc), self.my_switch.camp.credits,
                                               self.trainer.skill.name, self.trainer.pc.get_stat(self.trainer.skill))


class SkillTrainer(object):
    CREDITS_PER_XP = 500
    COURSE_COSTS = (10000, 50000, 100000, 250000, 500000, 1000000, 2000000)
    def __init__(self, skill_list=(gears.stats.Vitality, gears.stats.Athletics, gears.stats.Concentration)):
        self.skill_list = skill_list
        self.pc = None

    def do_training(self, camp):
        # Setup the widgets.
        mywidget = pbge.widgets.ColumnWidget(-175,-200,350,400, draw_border=True, center_interior=True)
        myswitch = PlayerCharacterSwitchPlusSkillTrainingInfo(camp, camp.pc, self._set_pc, self)
        self.pc: gears.base.Character = camp.pc
        mywidget.add_interior(myswitch)

        myrow = pbge.widgets.RowWidget(0,0,350,200)
        myskillcol = SkillColumn(self.skill_list, self._set_skill)
        self.skill = self.skill_list[0]
        myrow.add_left(myskillcol)

        self.camp = camp
        mybuycol = pbge.widgets.ColumnWidget(0,0,155,200, padding=12)
        for t in self.COURSE_COSTS:
            mybuycol.add_interior(SkillBuyWidget(t, self._buy_training, self))

        myrow.add_right(mybuycol)
        mywidget.add_interior(myrow)

        mywidget.children.append(pbge.widgets.LabelWidget(95,210,80,16,text="Done",justify=0,on_click=self._done_button,draw_border=True))


        pbge.my_state.widgets.append(mywidget)
        self.running = True
        while self.running and not pbge.my_state.got_quit:
            ev = pbge.wait_event()
            if ev.type == pbge.TIMEREVENT:
                pbge.my_state.view()
                pbge.my_state.do_flip()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.running = False
        pbge.my_state.widgets.remove(mywidget)

    def _set_pc(self, pc):
        self.pc = pc

    def _set_skill(self, sk):
        self.skill = sk

    def _done_button(self, wid, ev):
        self.running = False

    def _buy_training(self, wid, ev):
        if self.pc and wid.data <= self.camp.credits and self.skill in self.pc.statline:
            xpcred = wid.data
            if self.pc.get_stat(gears.stats.Knowledge) > 10:
                xpcred = (xpcred * (self.pc.get_stat(gears.stats.Knowledge) + 40))//50
            self.camp.credits -= wid.data
            self.pc.dole_experience(xpcred//self.CREDITS_PER_XP, self.skill)

    def __call__(self, camp):
        self.do_training(camp)
