passive_abilities = [
    'extra_armour'
]


def extra_armour(self):
    if self.applied_abilites['extra_armour'] < 1:
        self.add_pool('might', 3)
        self.add_pool('speed', 3)
        self.add_armour(1)


ability_methods = {
    'extra_armour': lambda self: extra_armour(self),
    'rush': lambda self: self.stats.damage('might', 1),
    'flame spell': lambda self: self.stats.damage('intellect', 1),
}
