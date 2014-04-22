This is a bot for importing comments directly into
the Stunfisk Pokedex (http://www.reddit.com/r/Stunfisk/wiki/Pokedex).

Requirements: Python 2.7.x, PRAW, Reddit account (with approval to write in
the Stunfisk wiki).

To run the bot, rename "login_template.py" to "login.py" and replace
USERNAME and PASSWORD with your reddit username and password. To generate the
Pokedex index, run generate_dex_index.py. To run the bot, run dex_updater.py.

The list of approved submitters is in approved_submitters.py.
Approved posts must be in the format: APPROVED SET | POKEMON: [name] | SET NAME: [set name]
