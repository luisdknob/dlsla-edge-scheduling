import random

class Population:
    """ This class represents a population of individuals in the genetic algorithm.
    It stores GA information such as the list of chromosomes and the number of individuals
    that are selected each generation for matting (crossover).
    """
    def __init__(self, pop_size, max_generations, mutation_rate, node, initial_time):
        """ Creates a Population object.

        Parameters
        ==========
        pop_size : int
            Number of individuals that constitute the population

        max_generations : int
            Limit of iterations the genetic algorithm can iterate to find a better solution

        mutation_rate : float
            Probability of offspring suffering from mutation

        node_id : int
            Node identifier
        """

        # Node identifier
        self.node = node
        self.initial_time = initial_time
        self.chromosomes_id = 0

        self.pop_size = pop_size
        self.max_generations = max_generations
        self.individuals_for_mating = max(pop_size // 2 if pop_size // 2 % 2 == 0 else pop_size // 2 - 1, 2)
        #self.individuals_for_mating = pop_size
        self.offspring_size = self.individuals_for_mating // 2
        self.mutation_rate = mutation_rate

        # List of individuals that represent solutions for the problem
        self.chromosomes = []

        # List of pareto fronts
        self.fronts = []

        #self.chromosomes.append(Chromosome(population=self, genes=self.node['queueMessages']))

        # Creating valid solutions
        for i in range(0, pop_size):

            # Randomly picking genes for the chromosome (solution)
            genes = node['queueMessages'].copy()
            random.shuffle(genes)

            # Adds the solution to the population
            self.chromosomes.append(Chromosome(population=self, genes=genes))

        #print("new run")

    def compute_fronts(self):
        """ Populates a list of pareto fronts using the individuals within the population.
        """

        ########################################
        ## Computing population's first front ##
        ########################################
        front = []
        for ind1 in self.chromosomes:
            for ind2 in self.chromosomes:
                if ind1.check_dominance(ind2):
                    ind1.dominates.append(ind2)
                    ind2.dominated_by.append(ind1)

        for ind in self.chromosomes:
            # Adding individual to the first front if it is not dominated by any other individual
            if len(ind.dominated_by) == 0:
                ind.front = 1
                front.append(ind)

        self.fronts = [front]


        ###################################################################################
        ## Computing n remaining fronts until all individuals are categorized in a front ##
        ###################################################################################
        individuals_without_front = [ind for ind in self.chromosomes if ind.front == 0]

        while len(individuals_without_front) > 0:
            front = []

            for dominator in self.fronts[-1]:
                for ind in individuals_without_front:
                    if dominator in ind.dominated_by:
                        ind.dominated_by.remove(dominator)

            for ind in individuals_without_front:
                if len(ind.dominated_by) == 0:
                    ind.front = len(self.fronts)+1
                    front.append(ind)


            # Adding the computed front to the population's front list
            self.fronts.append(front)

            # Re-checking if there are individuals without front
            individuals_without_front = [ind for ind in self.chromosomes if ind.front == 0]


    def compute_crowding_distance(self):
        """ Computes the crowding distance of each individual within the population.
        """

        # Resetting individuals crowding distance
        for ind in self.chromosomes:
            ind.crowding_distance = 0.0

        # Selecting problem objectives
        objectives = [obj for obj in self.chromosomes[0].fitness]

        # Re-computing individuals' crowding distance
        for front in self.fronts:
            for objective in objectives:

                # Sorting individuals in the front based on their fitness score for each objective
                sorted_front = sorted(front, key=lambda i: i.fitness[objective])

                # First and last individuals get 'crowding_distance=infinity'
                sorted_front[0].crowding_distance = float('inf')
                sorted_front[-1].crowding_distance = float('inf')

                norm = sorted_front[-1].fitness[objective] - sorted_front[0].fitness[objective]
                if norm == 0:
                    norm = 1

                # Computing crowding distance for the other individuals in the front
                for pos, ind in enumerate(sorted_front):
                    if pos != 0 and pos != len(sorted_front)-1:
                        ind.crowding_distance += (sorted_front[pos+1].fitness[objective] - sorted_front[pos-1].fitness[objective]) / norm


    def rank_selection(self):
        """ Selects the N fittest individuals from the population.
        """
        return(self.chromosomes[-self.individuals_for_mating:])


    def uniform_crossover(self, parents):
        """ Generates the offspring using the genes from the selected
        individuals (offspring suffers mutation given a random probability).

        Parameters
        ==========
        parents : list
            List of individuals from which we will create the offspring
        """

        #print(len(self.chromosomes), self.pop_size, self.individuals_for_mating, len(parents))

        for y in range(0, len(parents)-1):

            #for _ in range(0,2):

            new_individual_genes = []
            garbage = []

            for i in range(0,len(parents[0].genes)):
                flag = 0
                randon_i = random.randint(0,1) 
                index = randon_i + y
                inverse = ((randon_i + 1) % 2) + y

                #print(y, index, inverse)
                value = parents[index].genes[i]
                value_inverse = parents[inverse].genes[i]

                if value not in new_individual_genes:
                    if value_inverse != value and value_inverse not in garbage and value_inverse not in new_individual_genes:
                        garbage.append(value_inverse)
                    if value in garbage:
                        garbage.remove(value)
                    new_individual_genes.append(value)
                elif value_inverse not in new_individual_genes:
                    if value_inverse in garbage:
                        garbage.remove(value_inverse)
                    new_individual_genes.append(value_inverse)
                else:
                    random_value = random.choice(garbage)
                    new_individual_genes.append(random_value)
                    garbage.remove(random_value)

            if 1 - self.mutation_rate <= random.random():
                    new_individual_genes = self.mutation(new_individual_genes)
        
            # Creating the individual with the set of genes
            new_individual = Chromosome(population=self, genes=new_individual_genes)
            #print(new_individual.get_genes())
            new_individual.compute_fitness()

            # Adds the new individual to the population
            self.chromosomes.append(new_individual)


    def mutation(self, individual_genes):
        """ Changes random genes from an individual to promote diversity in the population.
        
        Parameters
        ==========
        individual : list
            Genes from the individual that will suffer from mutation

        Returns
        =======
        individual_genes : list
            Modified set of genes
        """
        n_bits_to_change = random.randint(1, len(individual_genes)//2)
        for i in range(0, n_bits_to_change):
            first_index = random.randint(0, len(individual_genes)-1)
            second_index = random.randint(0, len(individual_genes)-1)
            temp_element = individual_genes[first_index]
            individual_genes[first_index] = individual_genes[second_index]
            individual_genes[second_index] = temp_element

        return(individual_genes)


    def get_best_candidate(self):
        """ Selects the best candidate within the population. To do so,
        we get the individual that belongs to the first front with fewer
        SLA violations. In case of draw, we pick the individual that suggests
        performing fewer migrations.

        Returns
        =======
        best_candidate : Chromosome
            Best chromosome within the population
        """

        best_candidate = sorted(self.fronts[0], key=lambda ind:
            (ind.fitness['sla_violations'], ind.fitness['total_time'],  ind.fitness['changes']))
            #(ind.fitness['sla_violations'], ind.fitness['total_time'], ind.fitness["diff_acc_sla"], ind.fitness['changes']))

        return(best_candidate)


class Chromosome:

    def __init__(self, population, genes):
        """ Creates a Chromosome object. For this problem, chromosomes (solutions)
        are encoded in the following way:

        example_chromosome = [6, 3, 4]

        Here, each position of the list 'example_chromosome' represents a service placement. For
        instance, the first position (example_chromosome[0]) represents the placement of Service_1.
        The values in each position of the list represent the Edge Nodes that will host the services.
        In that case, example_chromosome[0]=6 tell us that Service_1 will be hosted by EdgeNode_6.

        Parameters
        ==========
        population : Population
            Population to which the chromosome belongs to

        genes : List
            Set of genes that compose the chromosome
        """

        self.population = population

        # Chromosome identifier
        self.id = population.chromosomes_id
        self.population.chromosomes_id += 1

        # List of individuals that pareto dominate the chromosome
        self.dominated_by = []

        # List of individuals that are pareto dominated by the chromosome
        self.dominates = []

        # Determinates to which population front the individual belongs to (0 = Not computed yet)
        self.front = 0

        # Individual's crowding distance
        self.crowding_distance = 0

        # Individual fitness scores for each objective
        self.fitness = None

        self.genes = genes


    def __str__(self):
        return(f'{self.id}')


    def __repr__(self):
        return(f'{self.id}')

    def get_genes(self):
        return [ (x["replica"], x["application"]) for x in self.genes ]

    def compute_fitness(self):
        """ Calculates the fitness of the individual.

        Objectives:
            (1) Minimize the number of SLA violations
            (2) Minimize the total time to deploy all applications
            (3) Minimize the number of changes on queue

        Returns
        =======
        fitness : Dictionary
            Fitness scores of the individual on each objective
        """

        # Storing the actual service placement scheme so that any changes
        # made to compute the individual fitness score won't affect the simulation
        

        # Initiating variables that will compute each objective
        sla_violations = 0
        total_time = self.population.initial_time
        bandwidth = self.population.node['bandwidth']
        layer_queue = self.population.node['layer_queue'].copy()
        diff_acc_sla = 0

        # print("a", total_time, bandwidth)

        for gene in self.genes:
            for digest, size in gene["layers"].items():
                if digest not in layer_queue:
                    total_time += size[0]/bandwidth
                    layer_queue.append(digest)
            if total_time > gene["sla"]:
                sla_violations += 1
            #diff_acc_sla += abs(gene["sla"]-total_time)
        #     print("gene", gene["application"], total_time)

        # print("b", total_time)

        actual_queue = [x["replica"] for x in self.population.node['queueMessages']]
        new_queue = [x["replica"] for x in self.genes]
        changes = 0

        for app in actual_queue:
            i = new_queue.index(app)
            new_queue.pop(i)
            changes += i

        #################################
        ## Computing the fitness score ##
        #################################
        #self.fitness = {'total_time': total_time, 'diff_acc_sla': diff_acc_sla, 'sla_violations': sla_violations, 'changes': changes}
        self.fitness = {'total_time': total_time, 'sla_violations': sla_violations, 'changes': changes}

        #print(self.fitness)
        #########################
        ## Computing Penalties ##
        #########################
        # overloaded_servers = 0

        # for server in EdgeNode.all():
        #     if server.demand > server.capacity:
        #         overloaded_servers += 1

        # # Penalty function that increases the fitness score (larger->worst) based on the number of
        # # overloaded servers. This strategy adapts the function presented by Alice Smith and David Coit in:
        # # https://www.researchgate.net/profile/Thomas-Baeck/publication/2509987_Penalty_Functions/links/004635183b02f19de2000000/Penalty-Functions.pdf
        # for objective, score in self.fitness.items():
        #     self.fitness[objective] = score + (10**9 * overloaded_servers)


        ####################################
        ## Restoring the actual placement ##
        ####################################
        #restore_placement(actual_placement)


        return(self.fitness)


    def check_dominance(self, other_individual):
        """ Checking dominance between two individuals.

        Parameters
        ==========
        other_individual : Chromosome
            Chromosome that will be compared during the dominance check

        Returns
        =======
        Dominance Result : boolean
            Boolean expression that tells us if the individual is whether dominated by its neighbor of not
        """

        # Fitness values from the first individual (represented by 'self')
        x1 = self.fitness['total_time']
        y1 = self.fitness['sla_violations']
        z1 = self.fitness['changes']
        #w1 = self.fitness["diff_acc_sla"]


        # Fitness values from the first individual (represented by 'other_individual')
        x2 = other_individual.fitness['total_time']
        y2 = other_individual.fitness['sla_violations']
        z2 = other_individual.fitness['changes']
        #w2 = other_individual.fitness["diff_acc_sla"]

        #return((y1 <= y2 and z1 <= z2 and x1 <= x2 and w1 <= w2) and (y1 < y2 or z1 < z2 or x1 < x2 or w1 < w2))
        return((y1 <= y2 and z1 <= z2 and x1 <= x2) and (y1 < y2 or z1 < z2 or x1 < x2))


def genetic_algorithm(pop_size, max_generations, mutation_rate, node, initial_time):

    ################################################################
    ## Creating the population of valid solutions for the problem ##
    ################################################################
    pop = Population(pop_size, max_generations, mutation_rate, node, initial_time)

    ###################################################################
    ## Computing fitness scores of each individual in the population ##
    ###################################################################

    for chromosome in pop.chromosomes:
        chromosome.compute_fitness()

        # Resetting individuals front (it will be re-computed next)
        chromosome.front = 0


    #################################
    ## Computing population fronts ##
    #################################
    pop.compute_fronts()


    #################################
    ## Computing crowding distance ##
    #################################
    pop.compute_crowding_distance()

    
    #############################################################
    ## Iterating MAX_GENERATION times to evolve the population ##
    #############################################################
    #print("running")

    for i in range(0, pop.max_generations):

        #########################################
        ## Selection of individuals for mating ##
        #########################################
        selected_parents = pop.rank_selection()

        ####################################################################
        ## Crossover between selected individuals to create the offspring ##
        ####################################################################
        pop.uniform_crossover(selected_parents)


        ################################################################
        ## Resetting the front from each individual in the population ##
        ################################################################
        for chromosome in pop.chromosomes:
            chromosome.front = 0


        #################################
        ## Computing population fronts ##
        #################################
        pop.compute_fronts()


        #################################
        ## Computing crowding distance ##
        #################################
        pop.compute_crowding_distance()


        #########################################################################
        ## Sorting the population based on their fronts and crowding distances ##
        #########################################################################
        pop.chromosomes = sorted(pop.chromosomes, key=lambda ind: (ind.front, -ind.crowding_distance))

        
        ################################################################
        ## Removing the least fittest individuals from the population ##
        ################################################################
        del pop.chromosomes[-pop.offspring_size:]
        #a = pop.get_best_candidate()

        #print(a[-1].fitness, len(pop.node["queueMessages"]))
    
        # print("round")
        # for candidate in pop.chromosomes:
        #     print(candidate.fitness, candidate.id)
        # best_candidate = pop.get_best_candidate()
        # print("best")
        # print(best_candidate[0].fitness, best_candidate[0].id)

    best_candidate = pop.get_best_candidate()
    #return (best_candidate[0].fitness["total_time"],best_candidate[0].fitness["sla_violations"],best_candidate[0].genes,best_candidate[0].fitness["diff_acc_sla"])
    return (best_candidate[0].fitness["total_time"],best_candidate[0].fitness["sla_violations"],best_candidate[0].genes,best_candidate[0].fitness["changes"])
