import random 
from deap import base, creator, tools, algorithms

import eval_function_file 
import auto_eval 

"""
A duct is a tuple (L = length, D = dimension)
A pipe is a list of ducts i.e. tuples
"""
toolbox = base.Toolbox()

#
# ABEC setup
#
project_file_path = r"C:\Users\julio\Documents\RDTeam\ABEC3\ABEC3 Examples\LEM\Enclosure Vented\Project.abec"
output_file_path = r"C:\Users\julio\Documents\RDTeam\ABEC3\ABEC3 Examples\LEM\Enclosure Vented\Results\Spectrum.txt"
auto_output_file_path = r"C:\Users\julio\Documents\RDTeam\ABEC3\ABEC3 Examples\LEM\Enclosure Vented\Results\VacsSpectrum.vips"

abec = auto_eval.ABEC(project_file_path, output_file_path, auto_output_file_path)

#
# Genetic Algorithm parameters
#
population_size = 5 
generations = 2

computeFitness_passband = (30,90)
computeFitness_tolerance = 30
crossover_continuation_prob = 0.5
mutation_length_change_sigma = 100  # 68% in [-100,100], 95% in [-200,200]
mutation_dim_change_sigma    = 50   # 68% in [ -50, 50], 95% in [-100,100]
selection_tournsize = 3

CXPB = 0.5      # CXPB  is the probability with which two individuals are crossed
MUPB = 0.2      # MUTPB is the probability for mutating an individual

#
# constraints 
# dimensions in mm
# 
pipe_max_ducts = 10 
duct_min_len = 1
duct_max_len = 1000
duct_min_dim = 1
duct_max_dim = 300



#
# functions -> later put in seperate file maybe..
#

# generate single duct
def rand_duct() :
    L = random.randint(duct_min_len, duct_max_len)
    D = random.randint(duct_min_dim, duct_max_dim)
    return (L,D)

# generate a pipe of random length ducts
def rand_pipe():
    l = list()
    number = random.randint(1, 10) 
    for i in range(number) :
        l.append(rand_duct())

# evaluation function to be used
def evalFunction(pipe) :
    # This function takes the list individual i.e. its ducts,
    # transform it into an LE-Script, put this script into the file.
    # Then call the auto_eval function and read in the data_frame 
    # Evaluate the data_frame and return the following tuple:
    # (n_spl, n_std,n_dev,n_range,stable_phase ,n_gstd , n_maxgd)

    abec.load(pipe)                 # translate the pipe into LEScript and put it in file
    abec.calc_spectra_and_safe()    # do calculation in ABEC
    abec.return_data()              # load the data from file
    
    return eval_function_file.compute_fitness(abec.df, computeFitness_passband, computeFitness_tolerance)


    
# TODO:
# crossover function
def crossFunction(p1, p2) :
    # this function needs to do cross-over changes on p1 and p2 in-place -> no return 
    p = list()
    max_len = max(len(p1), len(p2))

    for i in range(max_len) :
        duct1 = p1[i] if i < len(p1) else None 
        duct2 = p2[i] if i < len(p2) else None 

        if duct1 is not None and duct2 is not None :
            p.append(random.choice([duct1, duct2]))
        elif random.random() > crossover_continuation_prob :   # stop the loop (adding elements) 
            break
        elif duct1 is not None :
            p.append(duct1)
        elif duct2 is not None :
            p.append(duct2)
    return p    

# mutation function   -> Do we want to do mutation like this? or like in the 
def mutateFunction(p) :
    # how exactly do we do mutation? 
    # suggestion 50/50 either (delete,add) or (length,dim) and then 50/50 again
    # for length and dim i suggest increasing/decreasing after a normal distribution
    # i.e. the more change the less likely => See parameters in top of program

    r = random.random()
    pos = random.randint(0, len(p) - 1)
    (L,D) = p[pos]

    if r < 0.25 : # add 
        if len(p) < 10 :
            pos = random.randint(0, len(p))
            p.insert(pos, rand_duct)
        else :
            mutateFunction(p) 
    elif r < 0.5 : # delete
        if len(p) > 1 :
            del p[pos]
        else :
            mutateFunction(p) 
    elif r < 0.75 : # length
        
        change = random.gauss(0, mutation_length_change_sigma)
        if change > 0 : 
            p[pos] = (min(L + change, duct_max_len),D)
        else :
            p[pos] = (max(L + change, duct_min_len),D)


    else : # dimensionality 
        change = random.gauss(0, mutation_dim_change_sigma)
        if change > 0 : 
            p[pos] = (L, min(D + change, duct_max_len))
        else :
            p[pos] = (L, max(D + change, duct_min_len))



#
# Structure Inits
#

# UNFINISHED: weights has to be adjusted according to the number of objectives and how they should be accounted for 
creator.create("FitnessMax", base.Fitness, weights = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0) )       
creator.create("Pipe", list, fitness=creator.FitnessMax)

# Function toolbox.attr_duct() -> random duct
toolbox.register("attr_duct", rand_duct)

# Function toolbox.individual() -> pipe of length in [1,10] and random duct dimensions
toolbox.register("individual", tools.initRepeat, creator.Pipe, toolbox.attr_duct, random.randint(1,10))

# toolbox.population(pop_size) -> list of pop_size individuals 
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


#
# Operations 
#

# goal/fitness function 
toolbox.register("evaluate", evalFunction)

# provisorically used tools.cxTwoPoint instead of crossFunction
# crossover operation
toolbox.register("mate", tools.cxTwoPoint)

# mutation function 
toolbox.register("mutate", mutateFunction)

# selection 
toolbox.register("select", tools.selTournament, tournsize = selection_tournsize)


def main() :


    random.seed(1)

    pop = toolbox.population(n=population_size)

    #
    # Start evolution
    #

    print("Start evolution")

    # Evaluate entire pop
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses) :
        ind.fitness.values = fit 

    print("  Evaluated %i individuals" % len(pop))

    # Extracting all the fitnesses of individuals into a list
    fits = [ind.fitness.values for ind in pop]

    g = 0

    while g < generations :
        g = g + 1
        print("-- Generation %i --" % g)

       # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # cross two individuals with probability CXPB
            if random.random() < CXPB:
                toolbox.mate(child1, child2)

                # fitness values of the children
                # must be recalculated later
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:

            # mutate an individual with probability MUTPB
            if random.random() < MUPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        print("  Evaluated %i individuals" % len(invalid_ind))

        # The population is entirely replaced by the offspring
        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)

        
    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))

    abec.end()

if __name__ == "__main__":
    main()


