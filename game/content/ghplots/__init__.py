import inspect

from . import actionscenes
from . import campfeatures
from . import challengeplots
from . import consequences
from . import dd_combatmission
from . import dd_conclusion
from . import dd_customobjectives
from . import dd_distanttown
from . import dd_homebase
from . import dd_intro
from . import dd_lancedev
from . import dd_main
from . import dd_misc
from . import dd_roadedge
from . import dd_roadedge_etc
from . import dd_roadedge_propp
from . import dd_roadedge_unique
from . import dd_roadstops
from . import dungeons
from . import encounters
from . import lancedev
from . import lancemates
from . import missionbuilder
from . import mission_conversations
from . import mission_stubs
from . import mission_teamups
from . import mocha
from . import peopleplots
from . import randomplots
from . import recovery
from . import romance
from . import rwme_default
from . import rwme_objectives
from . import seekenemybase
from . import setpiece
from . import shops_plus
from . import tarot_cards
from . import tarot_reveal
from . import tarot_sockets
from . import thingplacers
from . import treasures
from . import utility
from game.content import mechtarot, PLOT_LIST, UNSORTED_PLOT_LIST, CARDS_BY_NAME
from pbge.plots import Plot


def harvest( mod ):
    for name in dir( mod ):
        o = getattr( mod, name )
        if inspect.isclass( o ) and issubclass( o , Plot ) and o is not Plot and o is not mechtarot.TarotCard:
            PLOT_LIST[ o.LABEL ].append( o )
            UNSORTED_PLOT_LIST.append( o )
            # print o.__name__
            if issubclass(o,mechtarot.TarotCard):
                CARDS_BY_NAME[o.__name__] = o


harvest(actionscenes)
harvest(campfeatures)
harvest(challengeplots)
harvest(consequences)
harvest(dd_combatmission)
harvest(dd_conclusion)
harvest(dd_customobjectives)
harvest(dd_distanttown)
harvest(dd_homebase)
harvest(dd_intro)
harvest(dd_lancedev)
harvest(dd_main)
harvest(dd_misc)
harvest(dd_roadedge)
harvest(dd_roadedge_etc)
harvest(dd_roadedge_propp)
harvest(dd_roadedge_unique)
harvest(dd_roadstops)
harvest(dungeons)
harvest(encounters)
harvest(lancedev)
harvest(lancemates)
harvest(missionbuilder)
harvest(mission_conversations)
harvest(mission_stubs)
harvest(mission_teamups)
harvest(mocha)
harvest(peopleplots)
harvest(randomplots)
harvest(recovery)
harvest(romance)
harvest(rwme_default)
harvest(rwme_objectives)
harvest(seekenemybase)
harvest(setpiece)
harvest(shops_plus)
harvest(tarot_cards)
harvest(tarot_reveal)
harvest(tarot_sockets)
harvest(thingplacers)
harvest(treasures)
harvest(utility)

# Load the DLC.
import importlib.util
import sys
import glob
import pbge
import os.path


def init_plots():
    dlcs = glob.glob(pbge.util.user_dir('content','*.py'))
    modict = globals()

    for dlcpath in dlcs:
        dlcname = os.path.basename(dlcpath).rpartition('.')[0]
        if dlcname not in modict:
            try:
                spec = importlib.util.spec_from_file_location(dlcname, dlcpath)
                module = importlib.util.module_from_spec(spec)
                sys.modules[dlcname] = module
                spec.loader.exec_module(module)
                modict[dlcname] = module
                harvest(module)
            except (IndentationError, SyntaxError, ImportError) as err:
                print("ERROR: {} could not be loaded due to error: {}".format(dlcpath, err))
        else:
            print("Warning: User content {} not loaded because of duplicate name".format(dlcname))


def reload_plot_module(mod_name):
    # Reload a compiled adventure from disk.
    modict = globals()

    # Step one: get rid of existing module.
    if mod_name in modict:
        mod = modict[mod_name]
        for name in dir(mod):
            o = getattr(mod, name)
            if inspect.isclass(o) and issubclass(o, Plot) and o is not Plot and o is not mechtarot.TarotCard:
                PLOT_LIST[o.LABEL].remove(o)
                UNSORTED_PLOT_LIST.remove(o)
                # print o.__name__
                if issubclass(o, mechtarot.TarotCard):
                    del CARDS_BY_NAME[o.__name__]
        del sys.modules[mod_name]
        del modict[mod_name]

    # Step two: reload the module.
    try:
        spec = importlib.util.spec_from_file_location(mod_name, pbge.util.user_dir('content','{}.py'.format(mod_name)))
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        modict[mod_name] = module
        harvest(module)
    except (IndentationError, SyntaxError, ImportError) as err:
        print(
            "ERROR: {} could not be loaded due to error: {}".format(pbge.util.user_dir('content','{}.py'.format(
                mod_name)), err)
        )


