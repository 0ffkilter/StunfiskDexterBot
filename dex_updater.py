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
import HTMLParser
import pprint
from login import *
from var_keys import *
from aliases import *
from read_pokedex_json import POKEDEX
from pprint import pprint
from exception_handler import ExpHandler
from approved_submitters import APPROVED_SUBMITTERS


# Checks for an approving post
def approving_post(comment):
   text = comment.body.encode('ascii', 'ignore')
   text = unicode(text)
   approving_pattern = re.compile(r"\s*approved set\s*\|\s*pokemon:\s*(\w[\w.' -]+)\s*\|\s*set name:\s*([\w.!;\(\)/' +-]+).*", re.I)
   match = re.match(approving_pattern, text)
   if not match:
      return None
   raw_species = match.group(1)
   set_name = match.group(2)
   set_name = re.sub(r"\s+$", "", set_name) # remove trailing whitespace
   info = {}
   raw_species = raw_species.lower() # to lower case
   raw_species = re.sub(r"\s+$", "", raw_species) # remove trailing whitespace
   if raw_species in ALIAS_POKEMON:
      raw_species = ALIAS_POKEMON[raw_species]
   if not raw_species in NAME_TO_NUMBER:
      return None
   info["set_name"] = set_name
   info["stunfisk_dex_index"] = re.sub(r"[ .']","", raw_species)
   pokedex_index = re.sub("-", "", info["stunfisk_dex_index"])
   info["species"] = POKEDEX[pokedex_index]["species"]
   return info

# Check if we already replied to a comment
def already_replied(parent_comment, bot_name):
   for c in parent_comment.replies:
      for cx in c.replies:
         if cx.author.name == bot_name:
            return True
   return False

def add_set_to_page(pokemon_page, info, set_text, author):
   set_text = re.sub(r"^###","", set_text)
   set_text = re.sub(r"^##","", set_text)
   set_text = re.sub(r"^#","", set_text)
   page_split = pokemon_page["content"].split("##Nature", 1)
   if len(page_split) == 1:
      return
   new_poke_content = """{old_pre_content}

###[{set_name}]({permalink})

{set_text}

Submitted by /u/{author}

##Nature{old_post_content}"""
   new_poke_content = new_poke_content.format(
   old_pre_content=page_split[0],
   set_name=info["set_name"],
   permalink=info["permalink"],
   set_text=set_text,
   old_post_content=page_split[1],
   author=author)
   reason = "Adding a new set called {set_name}".format(set_name=info["set_name"])
   pokemon_page["page"].edit(content=new_poke_content, reason=reason)
   pokemon_page["content"] = new_poke_content

def update_pokedex_index(pokedex_index, species):
   bold_species = "**" + species + "**"
   if not bold_species in pokedex_index["content"]:
      pokedex_index["content"] = pokedex_index["content"].replace(species, bold_species, 1) # Limit to 1 to prevent updating different formes
      reason = "Updating {species} to bold font because a set has been added.".format(species=species)
      pokedex_index["page"].edit(content=pokedex_index["content"], reason=reason)

def approved_submitter(username):
   return username in APPROVED_SUBMITTERS

full_path = os.path.abspath(__file__)
source_dir = os.path.dirname(full_path) + os.sep
archive_dir = source_dir + "mail_sack" + os.sep
user_agent = "Updating Stunfisk Pokedex pages with user input by /u/veeveearnh"
r = praw.Reddit(user_agent = user_agent)
r.login(username = username, password = password)
stunfisk = r.get_subreddit('stunfisk')
#stunfisktest = r.get_subreddit('stunfiskpokedextest')
stunfisktest2 = r.get_subreddit('stunfiskCSS')
subreddit = stunfisktest2
me = praw.objects.Redditor(r, user_name=username)
keep_on = True

commented_count = 0
post_time_mark = 0
# fetch our last comment, which will dictate how far back we go on the
# first pass
my_comments = None
try:
   my_comments = me.get_comments(sort='new',time='all',limit=25)
except:
   # handle some exceptions here!
   raise
for c in my_comments:
   if c.submission.created_utc > post_time_mark:
      print ("new mark, " + str(time.time() - c.submission.created_utc) + " seconds in the past, for " + str(c.submission))
      post_time_mark = c.submission.created_utc

while (keep_on):
   # do stuff
   comments = None
   comments = subreddit.get_comments(limit=100)
   pprint(comments)
   retrieved_count = 0
   new_time_mark = post_time_mark
   print ("Starting loop at " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()) + " with post_time_mark of " + str(time.time() - post_time_mark) + " seconds in the past")

   try:
      for c in sorted(comments, key=lambda comment: comment.created_utc):
         h = HTMLParser.HTMLParser()
         pokedex_index = {}
         pokedex_index["page"] = subreddit.get_wiki_page(page="pokedex")
         pokedex_index["content"] = h.unescape(pokedex_index["page"].content_md)
         edited_pages = {}
         try:
            retrieved_count += 1
            # skip posts older than our previous "newest post" timestamp
            if c.created_utc <= post_time_mark:
               continue
            if c.is_root:
               continue
            if not approved_submitter(c.author.name):
               continue
            info = approving_post(c)
            if not info:
               continue
            parent_comment = r.get_info(thing_id=c.parent_id)
            parent_comment = r.get_submission(parent_comment.permalink).comments[0]
            info["permalink"] = parent_comment.permalink
            if already_replied(parent_comment, username):
               continue
            print ("We are currently considering a comment that is " + str(time.time() - parent_comment.created_utc) + " seconds old, from " + str(parent_comment.subreddit))
            text = parent_comment.body.encode('ascii', 'ignore')
            text = unicode(text)
            h = HTMLParser.HTMLParser()
            text = h.unescape(text)
            print text
            print ("We are now editing the Wiki page for " + info["species"])
            try:
               if not info["stunfisk_dex_index"] in edited_pages:
                  edited_pages[info["stunfisk_dex_index"]] = {}
                  edited_pages[info["stunfisk_dex_index"]]["page"] = subreddit.get_wiki_page(page=info["stunfisk_dex_index"])
                  edited_pages[info["stunfisk_dex_index"]]["content"] = h.unescape(
                        edited_pages[info["stunfisk_dex_index"]]["page"].content_md)
               add_set_to_page(edited_pages[info["stunfisk_dex_index"]], 
                     info, text, parent_comment.author.name)
               update_pokedex_index(pokedex_index, info["species"])
               reply_text = """\
The /r/Stunfisk [Pokedex](http://www.reddit.com/r/{subreddit}/wiki/pokedex) has been updated on the [{species}](http://www.reddit.com/r/{subreddit}/wiki/{stunfisk_dex_index}) page with the new set called {set_name}.

*I am a bot that searches for comments with approved sets to put into the /r/Stunfisk [Pokedex](http://www.reddit.com/r/{subreddit}/wiki/pokedex).*
"""
               reply_text = reply_text.format(
               subreddit=parent_comment.subreddit,
               species=info['species'],
               stunfisk_dex_index=info['stunfisk_dex_index'],
               set_name=info['set_name'])
               print ("We will now comment on this post...")
               numTries = 0
               while (numTries < 4):
                  try:
                     c.reply(reply_text)
                     commented_count += 1
                     break
                  except praw.errors.RateLimitExceeded as e:
                     print ("You are doing too much. Please try again soon.")
                     print ("We have so far tried " + str(numTries) + " times.")
                     print ("Sleeping for 5 minutes and then trying again.")
                     time.sleep(300)
                     numTries += 1
               new_time_mark = c.created_utc
            except socket.timeout as e:
               print "We have failed to open or read the wiki page, so we're ignoring this comment."
               continue
            print ("Sleeping for 5 seconds...")
            time.sleep(5)
         except UnicodeError as e:
            print("Unicode error, continuing to next post")
            continue
#   except (NameError, TypeError) as e:
#      pprint.pprint(dir(e))
#      pprint.pprint(vars(e))
#      break
   except socket.timeout as e:
      pprint.pprint(dir(e))
      pprint.pprint(vars(e))
      print ("Timeout")
#   except Exception as e:
#      pprint.pprint(dir(e))
#      pprint.pprint(vars(e))
#      print "Main loop failed with an exception, delaying 5 minutes before retrying"
#      time.sleep(300)

   print (str(retrieved_count) + " submissions considered at " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
   print (str(commented_count) + " submissions replied to so far this run")

   post_time_mark = new_time_mark
   print ("The new post_time_mark is " + str(post_time_mark))

   # sleep for 30 min between refreshes of the same page request, per the API rules
   print ("sleeping")
   time.sleep(1800)


