#!/usr/bin/python
import json
import re
from pprint import pprint

json_data = open('pokedex.js')
POKEDEX = json.load(json_data)
#pprint(data)
#lines = json_data.readlines()
#json_data.close()
#pattern = re.compile(r"^(\w[\w.' -]+):(.*)")
#for line in lines:
#   match = re.match(pattern, line)
#   if match:
#      print '"' + match.group(1) + '":' + match.group(2)
#
