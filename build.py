from collections import Counter
from datetime import datetime
from importlib import import_module
import os
import pickle

import yaml

from utils import PeriodicList

DATA_DIR = os.getenv('DATA_DIR', 'test_data')

methods = import_module('.'.join([DATA_DIR, 'methods']))
ability_methods = methods.ability_methods
passive_abilities = methods.passive_abilities

aspects = {}
for aspect in ['nouns', 'adjectives', 'verbs', 'abilities']:
    with open(os.path.join(DATA_DIR, f'{aspect}.yaml')) as f:
        aspects[aspect] = yaml.load(f)


class Attribute:
    def __init__(self, value):
        self.current = value
        self.max = value

    def reduce(self, value):
        new_value = self.current - value
        if new_value >= 0:
            self.current = new_value
        else:
            self.current = 0
            return abs(new_value)

    def increase(self, value):
        new_value = self.current + value
        self.current = min(new_value, self.max)

    def upgrade(self, value):
        self.max += value
        self.increase(value)

    @property
    def stats(self):
        return f'{self.current}/{self.max}'


class Stats:
    STATS = PeriodicList(['might', 'speed', 'intellect'])

    def __init__(self, noun, adjective, verb):
        self.might = Attribute(aspects['nouns'][noun]['might']['pool'])
        self.speed = Attribute(aspects['nouns'][noun]['speed']['pool'])
        self.intellect = Attribute(aspects['nouns'][noun]['intellect']['pool'])

        modifiers = aspects['adjectives'][adjective]['modifiers']
        getattr(self, modifiers['pool']).upgrade(modifiers['points'])

        try:
            modifiers = aspects['verbs'][verb]['modifiers']
            getattr(self, modifiers['pool']).upgrade(modifiers['points'])
        except KeyError:
            pass

        self.might.edge = Attribute(aspects['nouns'][noun]['might']['pool'])
        self.speed.edge = Attribute(aspects['nouns'][noun]['speed']['pool'])
        self.intellect.edge = Attribute(
            aspects['nouns'][noun]['intellect']['pool']
            )

    def __str__(self):
        return ', '.join(
            f'{f} = {getattr(self, f).stats}'
            for f in self.STATS
        )

    @property
    def total(self):
        return self.might.current + self.speed.current + self.intellect.current

    def add_pool(self, stat, value):
        getattr(self, stat).upgrade(value)

    def damage(self, stat, value):
        extra_damage = getattr(self, stat).reduce(value)
        if self.total <= 0:
            print('You died!')
            return
        if extra_damage:
            index = self.STATS.index(stat)
            self.damage(self.STATS[index + 1], extra_damage)

    def heal(self, stat, value):
        getattr(self, stat).increase(value)


class PC:
    def __init__(self, name, noun, adjective, verb):
        self.name = name
        self.descriptor = f'I am a(n) {adjective} {noun} who {verb}'
        self.noun = noun
        self.adjective = adjective
        self.verb = verb
        self.stats = Stats(noun, adjective, verb)
        self.effort = Attribute(self.noun_info['effort'])
        self.shins = self.noun_info['shins'] + self.adjective_info['shins']
        self.extra_points = self.noun_info['extra_points']
        self.applied_abilites = Counter()
        self.armour = 0

        self.equipment = Counter()
        verbal_equipment = self.verb_info.get('equipment', {})
        for name, quantity in verbal_equipment.items():
            self.add_equipment(name, quantity)

        self.skills = {}
        skills = self.verb_info.get('skills', {})
        for name, level in skills.items():
            self.skills[name] = level

        self.abilities = []
        abilities = self.verb_info.get('abilities', {})
        for name in abilities:
            self.abilities.append(name)

    def __repr__(self):
        return f'{self.__class__} {self.name}: {self.descriptor}'

    @classmethod
    def load(cls, name):
        last_save = sorted(
            os.listdir(os.path.join('characters', name)),
            reverse=True,
        )[0]
        with open(os.path.join('characters', name, last_save), 'rb') as f:
            return pickle.load(f)

    @property
    def noun_info(self):
        return aspects['nouns'][self.noun]

    @property
    def adjective_info(self):
        return aspects['adjectives'][self.adjective]

    @property
    def verb_info(self):
        return aspects['verbs'][self.verb]

    def add_pool(self, stat, value):
        if self.extra_points == 0:
            return("No more points to spend")
        elif (self.extra_points - value) < 0:
            return("Trying to spend too many points!")
        else:
            self.stats.add_pool(stat, value)
            self.extra_points = self.extra_points - value

    def add_armour(self, value):
        self.armour += value

    def add_ability(self, name):
        if name not in self.abilities:
            self.abilities.append(name)
        else:
            print('You already have this ability!')
        if name in passive_abilities:
            self.ability(name)

    def check_stats(self):
        s = ''

        if self.extra_points > 0:
            s = 'You still have stats points to spend!\n\n'

        s += str(self.stats)

        print(s)

    def print_description(self):
        s = '\n'.join(
            (
                self.adjective_info['description'],
                self.verb_info['description'],
            )
        )

        print(s)

    def earn(self, value):
        self.shins += value

    def pay(self, value):
        self.earn(-value)

    def add_equipment(self, item, number=1):
        self.equipment[item] += number

    def remove_equipment(self, item, number=1):
        self.add_equipment(item, -number)
        if self.equipment[item] <= 0:
            del self.equipment[item]

    def add_skill(self, skill, level='trained'):
        self.skills[skill] = level

    def train_skill(self, skill):
        if skill in self.skills:
            if self.skills[skill] == 'specialised':
                print('You are already specialised!')
            else:
                self.skills[skill] = 'specialised'
        else:
            print("You don't have this skill to train!")

    def print_abilities(self):
        s = []
        for ability in self.abilities:
            s.append(
                '\n'.join(
                    (
                        ability,
                        aspects['abilities'][ability]['description'],
                        )
                    )
                )
        print(*s, sep='\n')

    def print_skills(self):
        s = []
        for skill in self.skills:
            s.append(
                ': '.join(
                    (
                        skill,
                        self.skills[skill]
                    )
                )
            )
        print(*s, sep='\n')

    def save(self):
        filename = f'{self.name}_{datetime.now()}.pickle'
        current_dir = os.getcwd()
        final_dir = os.path.join(current_dir, 'characters', self.name)
        if not os.path.exists(final_dir):
            os.makedirs(final_dir)
        with open(os.path.join(final_dir, filename), 'wb') as f:
            pickle.dump(self, f)

    def ability(self, name):
        if name in self.abilities:
            ability_methods[name](self)
            self.applied_abilites[name] += 1
