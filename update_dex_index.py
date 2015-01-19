#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import praw
import time # for sleep
import signal # for setting up signal handler and signal constant
import os # for working with file paths
import re
import sys
import socket
import string
import urllib2
import HTMLParser
import traceback
from login import username as u
from login import password as p
from var_keys import *
from aliases import *
from read_pokedex_json import POKEDEX
from pprint import pprint
from exception_handler import ExpHandler

h = HTMLParser.HTMLParser()

set_key = "##Sets\n\n##Nature"

def has_set(content):
    return set_key in content

def update_index(subreddit, subreddit_name):
   content ="""\
**THIS PAGE IS A WORK IN PROGRESS**
**Only approved submitters and wiki submitters may edit this page.** - DW

**How to use the PokeDex**:

1. Press \"Ctrl + F\" or \"F3\" on Windows or \"Cmd + F\" on Mac to search for a Pokemon, type, ability, or BST.

2. Pokemon in **bold** have move sets.

3. Hidden abilities are *italicized*.

___

Pokémon|Type|Abilities|HP|Atk|Def|SpA|SpD|Spe|BST
:--|:--|:--|:--|:--|:--|:--|:--|:--|:--
"""
   for poke_name in sorted(NAME_TO_NUMBER.iterkeys()):
      stunfisk_dex_index = re.sub(r"[ .']","", poke_name)
      pokedex_index = re.sub("-", "", stunfisk_dex_index)
      types = " / ".join(POKEDEX[pokedex_index]["types"])
      abilities = " / ".join(POKEDEX[pokedex_index]["abilities"].values())
      bst = sum(POKEDEX[pokedex_index]["baseStats"].values())
      base_stats = POKEDEX[pokedex_index]["baseStats"]
      bold = ""
      try:
         pokemon_page = subreddit.get_wiki_page(page=stunfisk_dex_index)
         poke_content = pokemon_page.content_md
         poke_content = h.unescape(poke_content)
         if has_set (poke_content):
             bold = "**"
      except KeyboardInterrupt:
        sys.exit(0)
      except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
        print ("Page not indexed %s" %stunfisk_dex_index)
      print("Currently up to: " + POKEDEX[pokedex_index]["species"])
      content = "{content}[{bold}{species}{bold}](/r/{subreddit_name}/w/{stunfisk_dex_index})|{types}|{abilities}|{hp}|{atk}|{defence}|{spa}|{spd}|{spe}|{bst}\n".format(
      content=content,
      bold=bold,
      species=POKEDEX[pokedex_index]["species"],
      subreddit_name=subreddit_name,
      stunfisk_dex_index=stunfisk_dex_index,
      types=types,
      abilities=abilities,
      hp=base_stats["hp"],
      atk=base_stats["atk"],
      defence=base_stats["def"],
      spa=base_stats["spa"],
      spd=base_stats["spd"],
      spe=base_stats["spe"],
      bst=bst)


   subreddit.edit_wiki_page(page="pokedex", content=content, reason="updating pokedex page with new megas")
#   index_page = subreddit.get_wiki_page(page="pokedex")
#   pprint(vars(index_page))
#   index_page.edit(content=content, reason="Renewing the index page.")

full_path = os.path.abspath(__file__)
source_dir = os.path.dirname(full_path) + os.sep
archive_dir = source_dir + "mail_sack" + os.sep
user_agent = ("Generates the /r/stunfisk wiki page.  Created by /u/veeveearnh")
r = praw.Reddit(user_agent = user_agent)
r.login(username=u, password=p)
stunfisk = r.get_subreddit('stunfisk')
me = praw.objects.Redditor(r, user_name=u)
update_index(stunfisk, "stunfisk")
