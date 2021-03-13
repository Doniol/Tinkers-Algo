import csv
import re
import random
import datetime


def read_from_file(file):
    with open(file, 'r') as file:
        reader = csv.reader(file)
        stuff = []
        for row in reader:
            row_stuff = []
            for column in row:
                try:
                    new = float(column)
                    row_stuff += [new]
                except:
                    row_stuff += [column]
            stuff += [row_stuff]
        return stuff


class Algorithm():
    def __init__(self, heads, extras, handles, traits, pop_size, iters, 
                 mut_chance, desired_stats, undesired_stats, free_mods):
        self.heads = heads
        self.handles = handles
        self.extras = extras
        self.traits = traits
        self.pop_size = pop_size
        self.iters = iters
        self.mut_chance = mut_chance
        self.desired_stats = desired_stats
        self.undesired_stats = undesired_stats
        self.free_mods = free_mods
        self.modifiers = ["Haste", "Sharp", "Diamond", "Emerald"]

    def parents_selector(self, population):
        parents = []
        for score_index in range(0, len(population), 2):
            if score_index + 1 == len(population):
                parents.append(population[score_index][1])
                break
            if population[score_index][0] > population[score_index + 1][0]:
                parents.append(population[score_index][1])
            else:
                parents.append(population[score_index + 1][1])
        return parents

    def children_creator(self, parents, weapon_class):
        children = []
        for i in range(self.pop_size):
            parent_1 = random.choice(parents)
            parent_2 = random.choice(parents)
            children.append(weapon_class.get_random_crossover(parent_1, parent_2, self.mut_chance, 
                                                              self.heads, self.extras, self.handles, 
                                                              self.traits, self.free_mods))
        return children

    def get_best_weapon(self, weapon_class):
        random.seed(datetime.datetime.now())
        population = [weapon_class.get_random(self.heads, self.extras, self.handles, self.traits,
                                              self.free_mods) for i in range(self.pop_size)]
        scores = []

        for iteration in range(self.iters):
            scores = []
            # Calc all scores
            for pop in population:
                scores.append([pop.get_score(self.desired_stats, self.undesired_stats), pop])
            
            parents = self.parents_selector(scores)
            population = self.children_creator(parents, weapon_class)
        results = map(lambda x: [x.get_score(self.desired_stats, self.undesired_stats)] + [x], population)
        return sorted(results, key=lambda x: x[0], reverse=True)


class TinkersTool():
    def __init__(self):
        pass

    @classmethod
    def get_random(cls, heads, extras, handles, traits, free_mods):
        return cls()

    @classmethod
    def get_random_crossover(cls, parent_1, parent_2, mut_chance, heads, extras, handles, traits, free_mods):
        return cls()

    def get_material_data(self, material, data):
        for entry in data:
            if entry[0] == material:
                return entry

    def set_modifiers(self, modifiers):
        pass

    def get_traits(self, all_traits):
        pass    

    def get_modifier_count(self):
        mod_count = 3
        thaumic = 0
        botanical_II = False
        botanical = 0

        for trait_data in self.traits:
            trait = trait_data[0]
            if trait == "Writeable":
                mod_count += 1
            elif trait == "Magically Modifiable":
                mod_count += 3
            elif trait == "Thaumic":
                thaumic += 1
            elif trait == "Botanical_II":
                botanical_II = True
                botanical += 1
            elif trait == "Botanical":
                botanical += 1
        
        if thaumic > 0:
            if thaumic == 3:
                mod_count += 2
            else:
                mod_count += 1
        if botanical > 0:
            if botanical_II and botanical > 1:
                mod_count += 3
            elif botanical_II and botanical == 1:
                mod_count += 2
            else:
                mod_count += 1
        return mod_count

    def get_score(self, desired_stats, undesired_stats):
        pass


class ThreePartWeapon(TinkersTool):
    def __init__(self, head, extra, handle, traits, modifiers=None):
        self.head = head
        self.extra = extra
        self.handle = handle
        self.modifiers = modifiers
        self.traits = self.get_traits(traits)
        TinkersTool.__init__(self)

    @classmethod
    def get_random(cls, heads, extras, handles, traits, free_mods):
        head = random.choice(heads)
        extra = random.choice(extras)
        handle = random.choice(handles)

        tool = cls(head, extra, handle, traits)
        modifiers = [random.choice(["Haste", "Sharp", "Diamond", "Emerald"]) for i in range(tool.get_modifier_count() - free_mods)]
        tool.set_modifiers(modifiers)
        return tool

    @classmethod
    def get_random_crossover(cls, parent_1, parent_2, mut_chance, heads, extras, handles, traits, free_mods):
        head = random.choice([parent_1.head, parent_2.head])
        extra = random.choice([parent_1.extra, parent_2.extra])
        handle = random.choice([parent_1.handle, parent_2.handle])
        parts = [head, extra, handle]
        mutation = 0

        if random.randint(0, mut_chance) == mut_chance:
            mutation = random.randint(0, 3)
            if mutation < 3:
                parts.pop(mutation)
                parts.insert(mutation, random.choice([heads, extras, handles][mutation]))

        tool = cls(*parts, traits)
        modifiers = []            

        for i in range(tool.get_modifier_count() - free_mods):
            possibilities = []
            if i < len(parent_1.modifiers):
                possibilities.append(parent_1.modifiers[i])
            if i < len(parent_2.modifiers):
                possibilities.append(parent_2.modifiers[i])
            if possibilities:
                modifiers.append(random.choice(possibilities))
            else:
                modifiers.append(random.choice(["Haste", "Sharp", "Diamond", "Emerald"]))

        if mutation == 3:
            modifier_mutation = random.randint(0, len(modifiers) - 1)
            modifiers.pop(modifier_mutation)
            modifiers.append(["Haste", "Sharp", "Diamond", "Emerald"])

        tool.set_modifiers(modifiers)

        return tool

    def set_modifiers(self, modifiers):
        self.modifiers = modifiers

    def get_traits(self, all_traits):
        trait_names = [self.head[-1], self.extra[-1], self.handle[-1]]
        final_trait_names = []
        for trait in trait_names:
            final_trait_names += re.split(r'\,', trait)
        
        given_traits = [self.get_material_data(trait, all_traits) for trait in final_trait_names]
        actual_traits = []
        for trait in given_traits:
            if trait[2] == "Yes" and trait not in actual_traits:
                actual_traits.append(trait)
            elif trait[2] == "No":
                actual_traits.append(trait)
        return actual_traits
    
    def check_desire(self, trait, desired_stats, undesired_stats):
        for stat in desired_stats:
            if stat in trait[1]:
                return 1.5
        for stat in undesired_stats:
            if stat in trait[1]:
                return 0.5
        return 1

    def get_score(self, base_dmg_bonus, base_spd, dur_modifier, sharpness_modifiers, desired_stats, undesired_stats):
        base_dmg = self.head[3] * base_dmg_bonus[0] + base_dmg_bonus[1]
        base_dur = ((self.head[1] + self.extra[1]) * self.handle[1] + self.handle[2]) * dur_modifier
        trait_score = sum(trait[-1] * self.check_desire(trait, desired_stats, undesired_stats) for trait in self.traits)
        
        end_dmg = base_dmg
        end_spd = base_spd
        end_dur = base_dur

        for modifier in self.modifiers:
            if modifier == "Haste":
                end_spd += base_spd * 0.2
            elif modifier == "Sharp":
                end_dmg = ((end_dmg * sharpness_modifiers[0]) + sharpness_modifiers[1])
            elif modifier == "Diamond":
                end_dur += 500
            elif modifier == "Emerald":
                end_dur += base_dur * 1.5
        
        dur_score = 1 if end_dur < 0 else -5 if end_dur < 200 else 1000 if end_dur >= 1000 else end_dur
        end_dps = end_dmg * end_spd
        
        if "Offense" in desired_stats or "Damage" in desired_stats:
            return (trait_score) + (end_dps*1.5) + (dur_score/100)
        elif "Durability" in desired_stats:
            return (trait_score) + end_dps + (dur_score/50)
        else:
            return (trait_score) + end_dps + (dur_score/100)

    def __repr__(self, name):
        text = ("\nType: " + name + 
            ":\nHead: " + str(self.head) + 
            "\nExtra: " + str(self.extra) + 
            "\nHandle: " + str(self.handle) + 
            "\nModifiers: " + str(self.modifiers) + "\n")
        return text


class Broadsword(ThreePartWeapon):
    def __init__(self, head, extra, handle, traits, modifiers=None):
        ThreePartWeapon.__init__(self, head, extra, handle, traits, modifiers)

    def get_score(self, desired_stats, undesired_stats):
        return ThreePartWeapon.get_score(self, [1, 2], 1.6, 1.1, [0.847, 3.6411], desired_stats, undesired_stats)

    def __repr__(self):
        return ThreePartWeapon.__repr__(self, "Broadsword")


class Rapier(ThreePartWeapon):
    def __init__(self, head, extra, handle, traits, modifiers=None):
        ThreePartWeapon.__init__(self, head, extra, handle, traits, modifiers)

    def get_score(self, desired_stats, undesired_stats):
        return ThreePartWeapon.get_score(self, [0.55, 1], 3, 0.8, [0.8363636, 2.1136364], desired_stats, undesired_stats)

    def __repr__(self):
        return ThreePartWeapon.__repr__(self, "Rapier")


class Longsword(ThreePartWeapon):
    def __init__(self, head, extra, handle, traits, modifiers=None):
        ThreePartWeapon.__init__(self, head, extra, handle, traits, modifiers)

    def get_score(self, desired_stats, undesired_stats):
        return ThreePartWeapon.get_score(self, [1.1, 1.55], 1.4, 1.05, [0.8481, 4.0198], desired_stats, undesired_stats)

    def __repr__(self):
        return ThreePartWeapon.__repr__(self, "Broadsword")


def main():
    #TODO: Apply Traits to raw stats where possible
    #TODO: Select multiple different weapons
    #TODO: Tool for monitoring each generation
    heads = read_from_file("new_heads.csv")[1:]
    extras = read_from_file("new_extras.csv")[1:]
    handles = read_from_file("new_handles.csv")[1:]
    traits = read_from_file("new_traits.csv")[1:]

    tester = Algorithm(heads, extras, handles, traits, 1000, 10000, 100, 
                       ["Damage", "Offense"], ["Utility", "Defense"], 0)
    ans = tester.get_best_weapon(Broadsword)[:5]
    print(ans)

main()