# Dungeon Master
This python project allows you to build a role playing character, choose a class ('noun'),
type ('adjective'), and job ('verb') and automatically generate the correct aspects for you
based on pre-specified aspects in the test_data file.

For example, if I wanted to create a character called Dan with a 'warrior' class, a 'kind' type and
a job of 'attacks' I would type the following into the console:

> from build import *

> a = PC('Dan', 'warrior', 'kind', 'attacks')

I could then check his stats by typing:

> a.check_stats()

I notice by typing

> a.print_abilities()

that Dan has the ability 'rush' that costs 1 might point to activate.
If I wanted to use this ability I would type

> a.ability('rush')

and this would remove one point from my might pool.

This project is designed with a particular RPG in mind but should be very flexible.
Use the files in test_data as examples and add to these files to create a huge
variety of characters with deadly abilities that will help you keep track of your
character without the need to keep rubbing out stats from your character sheet!
