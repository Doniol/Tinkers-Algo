    def parents_selector(self, population):
        parents = []
        for pop_index in range(0, len(population), 2):
            if pop_index + 1 == len(population):
                parents.append(population[pop_index][1])
                break
            if population[pop_index][0] > population[pop_index + 1][0]:
                parents.append(population[pop_index][1])
            else:
                parents.append(population[pop_index + 1][1])
        return parents