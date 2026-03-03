import random 
from deap import base, creator, tools, algorithms

"""
A duct is a tuple (L = length, D = dimension)
A pipe is a list of ducts i.e. tuples
"""
#
# Genetic Algorithm parameters
#
crossover_continuation_prob = 0.5



#
# constraints 
#
pipe_max_ducts = 10 
duct_min_len = 1
duct_max_len = 100
duct_min_dim = 1
duct_max_dim = 30

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
def evalFunction(individual) :
    # This function should take the list individual i.e. its ducts,
    # transform it into an LE-Script, put this script into the file.
    # Then call the auto_eval function and read in the data_frame 
    # Evaluate the data_frame and return a k-element tuple.
    return 1,


# crossover function
def crossFunction(p1, p2) :
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

# mutation function
def mutateFunction(p) :
    # how exactly do we do mutation? 
    # suggestion 50/50 either (delete,add) or (length,dim) and then 50/50 again
    # for length and dim i suggest increasing/decreasing after a normal distribution
    # i.e. the more change the less likely 

    r = random.random()
    if r < 0.25 : # add 
        if len(p) < 10 :
            p.addend(rand_duct)
        else :
            mutateFunction(p) 
    elif r < 0.5 : # delete
        if len(p) > 1 :
            pos = random.randint(0, len(p) - 1)
            del p[pos]
        else :
            mutateFunction(p) 
    elif r < 0.75 : # length
        

    else : # dimensionality 


toolbox = base.Toolbox()

#
# Structure Inits
#

# UNFINISHED: weights has to be adjusted according to the number of objectives and how they should be accounted for 
creator.create("FitnessMax", base.Fitness, weights = (1.0, ))       
creator.create("Pipe", list)

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

# crossover operation
toolbox.register("mate", crossFunction)

# mutation function 
toolbox.register("mutate", mutateFunction)
