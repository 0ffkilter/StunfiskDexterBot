#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import praw
import os # for working with file paths
import re
import HTMLParser
from login import username as u
from login import password as p
from var_keys import *
from aliases import *
from read_pokedex_json import POKEDEX
from pprint import pprint
from exception_handler import ExpHandler


def perform_merge(page, subreddit):
    content = parser.unescape(page.content_md)
    lst = content.split("#ARCHIVE")
    if len(lst) == 2:
       one = lst[0].split("##")
       lst[1] = re.sub('>', '', lst[1]) #Naively removes all '>' from the post - kind of messes up the format though
       two = lst[1].split("##")
    elif len(lst) == 1:
        print("page %s not archived" %page.page)
        return
    else:
        print("page under different format: %s" %page.page)
        return
    for i in range(1, len(one)):
        if one[i] != two[i]:
            one[i] = two[i]
    subreddit.edit_wiki_page(page=page.page, content = "##".join(one), reason='performing archive merge')
    print("performed page merge on %s" %page.page)
#   index_page = subreddit.get_wiki_page(page="pokedex")
#   pprint(vars(index_page))
#   index_page.edit(content=content, reason="Renewing the index page.")

parser = HTMLParser.HTMLParser()
full_path = os.path.abspath(__file__)
source_dir = os.path.dirname(full_path) + os.sep
archive_dir = source_dir + "mail_sack" + os.sep
user_agent = ("wiki page merges by /u/0ffkilter")
r = praw.Reddit(user_agent = user_agent)
r.login(username=u, password=p)
stunfisk = r.get_subreddit('stunfisk')
print("starting wiki merge")
for pokemon in sorted(NAME_TO_NUMBER.iterkeys()):
    try:
        perform_merge(stunfisk.get_wiki_page(page=pokemon), stunfisk)
    except:
        pass

