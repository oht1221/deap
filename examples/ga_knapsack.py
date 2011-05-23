#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import sys
import random
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

from deap import algorithms
from deap import base
from deap import creator
from deap import operators
from deap import toolbox

IND_SIZE = 30
MAX_ITEM = 50
MAX_WEIGHT = 50
NBR_ITEMS = 100

creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0))
creator.create("Individual", set, fitness=creator.Fitness)
creator.create("Population", list)

# Create the item dictionary, items' name is an integer, and value is a (weight, value) 2-uple.
# The items will be created during the runtime to enable reproducibility.
items = {}

tools = toolbox.Toolbox()

# Attribute generator
tools.register("attr_item", random.randrange, NBR_ITEMS)

# Structure initializers
tools.register("individual", creator.Individual, toolbox.Repeat(tools.attr_item, IND_SIZE))
tools.register("population", creator.Population, toolbox.Repeat(tools.individual, NBR_ITEMS))

def evalKnapsack(individual):
    weight = 0.0
    value = 0.0
    for item in individual:
        weight += items[item][0]
        value += items[item][1]
    if len(individual) > MAX_ITEM or weight > MAX_WEIGHT:
        return 10000, 0             # Ensure overweighted bags are dominated
    return weight, value

def cxSet(ind1, ind2):
    """Apply a crossover operation on input sets. The first child is the
    intersection of the two sets, the second child is the difference of the
    two sets.
    """
    temp = set(ind1)                # Used in order to keep type
    ind1 &= ind2                    # Intersection (inplace)
    ind2 ^= temp                    # Symmetric Difference (inplace)
    
def mutSet(individual):
    """Mutation that pops or add an element."""
    if random.random() < 0.5:
        if len(individual) > 0:     # We cannot pop from an empty set
            individual.pop()
    else:
        individual.add(random.randrange(NBR_ITEMS))

tools.register("evaluate", evalKnapsack)
tools.register("mate", cxSet)
tools.register("mutate", mutSet)
tools.register("select", operators.selSPEA2)

stats_t = operators.Stats(lambda ind: ind.fitness.values)
stats_t.register("Avg", operators.mean)
stats_t.register("Std", operators.std_dev)
stats_t.register("Min", min)
stats_t.register("Max", max)

def main():
    random.seed(64)
    # Create random items and store them in the items' dictionary.
    for i in xrange(NBR_ITEMS):
        items[i] = (random.randint(1, 10), random.uniform(0, 100))

    pop = tools.population()
    hof = operators.ParetoFront()
    stats = tools.clone(stats_t)
    
    algorithms.eaMuPlusLambda(tools, pop, 50, 100, 0.7, 0.2, 50, stats, halloffame=hof)
    
    logging.info("Best individual for measure 1 is %s, %s", 
                 hof[0], hof[0].fitness.values)
    logging.info("Best individual for measure 2 is %s, %s", 
                 hof[-1], hof[-1].fitness.values)
    
    return pop, stats, hof
                 
if __name__ == "__main__":
    main()                 