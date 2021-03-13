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
        return stuff[1:]


def get_material_data(material, data):
    for thing in data:
        if thing[0] == material:
            return thing


class Sword():
    def __init__(self, heads, handles, extras, traits):
        self.heads = heads
        self.handles = handles
        self.extras = extras
        self.traits = traits

    def get_score(self, head, handle, guard, modifiers, specifics):
        # Calc trait score
        # print("\n", head, handle, guard)
        # print(modifiers)
        traits = [get_material_data(head, self.heads)[-1]] + [get_material_data(handle, self.handles)[-1]] + [get_material_data(guard, self.extras)[-1]]
        traits = [re.sub(r'\[|\]', '', trait) for trait in traits]
        traits = [re.split(r'\,', trait) for trait in traits]
        final_traits = []
        for trait in traits:
            final_traits = list(set(list(final_traits + trait)))
        # print("Final traits:", final_traits)
        trait_score = sum(get_material_data(trait, self.traits)[-1] 
        if specifics not in get_material_data(trait, self.traits)[1] 
        else get_material_data(trait, self.traits)[-1] * 1.5 for trait
        in final_traits)
        # print("Trait score:", trait_score)

        # Damage per Second, damage per hit * attack speed
        base_dmg = get_material_data(head, self.heads)[3] + 2
        end_dmg = base_dmg
        # print("Base dmg:", base_dmg)
        base_spd = 1.6
        end_spd = base_spd
        # print("Base spd:", base_spd)

        # Durability
        base_dur = ((get_material_data(head, self.heads)[1] + get_material_data(guard, self.extras)[1]) * get_material_data(handle, self.handles)[1] + 
                   get_material_data(handle, self.handles)[2]) * 1.1
        end_dur = base_dur
        # print("Base durability:", base_dur)

        # Apply optional modifiers
        for modifier in modifiers:
            if modifier == "Haste":
                end_spd += base_spd * 0.2
            elif modifier == "Sharp":
                end_dmg = ((end_dmg * 0.847) + 3.6411)
            elif modifier == "Diamond":
                end_dur += 500
            elif modifier == "Emerald":
                end_dur += base_dur * 1.5
        
        # print("End durability:", end_dur)
        # print("End dmg:", end_dmg)
        # print("End spd:", end_spd)
        dur_score = 1 if end_dur < 0 else -5 if end_dur < 200 else 1000 if end_dur >= 1000 else end_dur
        # print("Durability Score:", dur_score)
        end_dps = end_dmg * end_spd
        # print("End dps:", end_dps)
        
        if "Offense" in specifics or "Damage" in specifics:
            return (trait_score/2) + (end_dps*2.0) + (dur_score/100)
        elif "Durability" in specifics:
            return (trait_score/2) + (end_dps*1.5) + (dur_score/50)
        else:
            return (trait_score/2) + (end_dps*1.5) + (dur_score/100)


def get_modifiers(parts):
    # Only for 3-part weapons atm
    mod_count = 3
    writeables = 0
    thaumic = 0
    botanical = 0
    for part in parts:
        if "Writeable" in part[-1]:
            writeables += 1
        if "Magically Modifiable" in part[-1]:
            mod_count += 3
        if "Thaumic" in part[-1]:
            thaumic += 1
        if "Botanical_II" in part[-1]:
            botanical_II = True
            botanical += 1
        elif "Botanical" in part[-1]:
            botanical += 1

    if writeables > 0:
        mod_count += 1
    if thaumic > 0:
        if thaumic == len(parts):
            mod_count += 2
        else:
            mod_count += 1
    if botanical > 0:
        if botanical_II and botanical == len(parts):
            mod_count += 3
        elif botanical_II and botanical == 1:
            mod_count += 2
        else:
            mod_count += 1
        
    
    return mod_count


def random_pop(heads, handles, extras, free_mod_count):
    parts = [random.choice(heads)[0], random.choice(handles)[0], random.choice(extras)[0]]
    mod_count = get_modifiers(parts)
    return parts + [[random.choice(["Haste", "Sharp", "Diamond", "Emerald"]) for i in range(mod_count - free_mod_count)]]


def create_child(parent_1, parent_2, heads, handles, extras, mutation_chance):
    parts = random.choice([parent_1[0], parent_2[0]]), random.choice([parent_1[1], parent_2[1]]), random.choice([parent_1[2], parent_2[2]])
    modifiers = [random.choice(parent_1[-1] + parent_2[-1]) for i in range(get_modifiers(parts))]
    child = list(parts) + [modifiers]
    
    if random.randint(0, mutation_chance) == mutation_chance:
        mutation = random.randint(0, 2)
        child.pop(mutation)
        child.insert(mutation, random.choice([heads, handles, extras][mutation])[0])
    return child


def get_best_sword(population_size, iterations, heads, handles, extras, traits, specifics="None", free_mod_count=0):
    selector = Sword(heads, handles, extras, traits)
    # Create random population pool
    random.seed(datetime.datetime.now())
    population = [random_pop(heads, handles, extras, free_mod_count) for i in range(population_size)]
    scores = []

    for iteration in range(iterations):
        # print(iteration)
        scores = []
        # Calc all scores
        for pop in population:
            # print(pop)
            # print(*pop)
            score = selector.get_score(*pop, specifics)
            # print("Score:", score)
            scores.append([int(score), pop])

        # Select parents for mating
        parents = []
        for score_index in range(0, len(scores), 2):
            # In case the population is an uneven number
            if score_index + 1 == len(scores):
                parents.append(scores[score_index][1])
                break
            # Save the better parent of the 2
            if scores[score_index][0] > scores[score_index + 1][0]:
                parents.append(scores[score_index][1])
            else:
                parents.append(scores[score_index + 1][1])

        # Fill the new generation
        population = []
        for i in range(population_size):
            child = create_child(random.choice(parents), random.choice(parents), heads, handles, extras, 25)
            # print(child)
            population.append(child)
    
    return sorted(scores, key=lambda x: x[0], reverse=True)


# Heads: Sword Blade, Large Sword Blade, Pickaxe Head, Shovel Head, Axe Head, Broad Axe Head,
#  Hammer Head,  Excavator Head, Kama Head, Scythe Head, Pan and Sign Plate
#  Also Knife Blade, Large Plate, Bowlimb and Arrow Head when on place of Head in construction
heads = read_from_file("heads.csv")
# print(heads)

# Handles: Bindings, Tough Bindings (+Extras)
handles = read_from_file("handles.csv")
extras = [[handle[0], handle[3], handle[4]] for handle in handles]
# print(handles)
# print(extras)

# Traits:
traits = read_from_file("traits.csv")
# print(traits)

print(get_best_sword(1, 1, heads, handles, extras, traits, "Offense")[:5])
