from mpi4py import MPI
import numpy as np
import ACO_load_data
import scipy as sp
from ACO_functions import *
from ACO_visualization import *
import copy

comm = MPI.COMM_WORLD
num_processes = comm.Get_size()
rank = comm.Get_rank()
print("rank",rank)

plot=False
big=True

from ACO_load_data import load_preprocessed
if not big:
    # if Me==0:
    #     G,tasks_durations,_ = load_data('Graphs/xsmallComplex.json')
    #     # G,tasks_durations,_ = load_data('Graphs/xxlargeComplex.json')
    #     # G,tasks_durations,_ = load_data('Graphs/smallRandom.json')
    #     # G,tasks_durations,_ = load_data('Graphs/mediumRandom.json')
    #     tasks_durations = np.array(tasks_durations)
    # G,tasks_durations=comm.bcast(G,root=0),comm.bcast(tasks_durations,root=0)
    job_durations_ls, nb_parents_0, longest_path, num_jobs, G = load_preprocessed("Preprocessed/smallRandom")
else:
    plot=False
    job_durations_ls, nb_parents_0, longest_path, num_jobs, G = load_preprocessed("Preprocessed/smallRandom")

edges = convert_childs_to_edges(G)

# Paramètres de l'algorithme ACO
num_ants = 10  # Nombre de fourmis  
num_iterations = 80  # Nombre d'itérations
num_processor = 3
pheromones_init = 1
k_best = 4

# Paramètres des phéromones
alpha = 1  # Influence de la phéromone sur la transition
beta = 1  # Influence de la distance sur la transition
gamma = 1  # Paramètre pour la mise à jour des phéromones
rho = 0.1  # Taux d'évaporation des phéromones
tmt = 1.
tmt_offset = 10
tmax = 10

# Fonction pour paralléliser le calcul des fourmis
def parallel_ant_calculation(pheromones,distance_beta,iteration,nb_parents_0,availaible_task_0):
    local_solutions = []
    for ant in range(rank, num_ants, num_processes):
        # Calcul de la fourmi pour ce processus
        path = [0]    # chemin choisie par la fourmi currente
        dependancy = dependancyTasks(edges, num_jobs)
        nb_parents = np.copy(nb_parents_0)
        available_tasks = copy.deepcopy(availaible_task_0)
        
        processors = [[] for _ in range(num_processor)]
        processors_availibility = np.zeros(num_processor)
        processors_successive_duration = [[] for _ in range(num_processor)]

        while available_tasks:
            # Sélection de la prochaine tâche en fonction de la probabilité de transition
            chosen_task = getNextTask(pheromones, path[-1], available_tasks, distance_beta, alpha, tmt=1 / (iteration + tmt_offset))
            path.append(chosen_task)
            updateAvailableTasks(G, chosen_task, available_tasks, nb_parents)
            dispatcher(dependancy, num_processor, chosen_task, processors, processors_availibility, processors_successive_duration, job_durations_ls)

        local_solutions.append([path, processors, processors_successive_duration])
    return local_solutions

# Algorithme ACO parallélisé
def main():
    best_solution = None
    best_makespan = float('inf')
    distance_beta = distanceBeta(num_jobs, job_durations_ls, beta=beta)
    makespan_updates = []
    # Initialisation des phéromones
    pheromones = sp.sparse.lil_matrix((num_jobs+1, num_jobs+1))
            

    available_tasks_0 =list(np.arange(1,num_jobs+1)[nb_parents_0[1:]==0])
    #print("available_task_0", available_tasks_0)
    for iteration in range(num_iterations):
        print(iteration * 100 / num_iterations)
        local_solutions = parallel_ant_calculation(pheromones,distance_beta,iteration,nb_parents_0,available_tasks_0)
        all_solutions = comm.gather(local_solutions, root=0)

        if rank == 0:
            solutions = [solution for sublist in all_solutions for solution in sublist]
            k_best_solutions = []
            for solution in solutions:
                makespan_val = makespan(solution[2])
                if makespan_val <= best_makespan:
                    best_solution = solution
                    best_makespan = makespan_val
                    makespan_updates.append(best_makespan)

            k_best_solutions, best_solution, best_makespan = kBestSolutions(k_best_solutions,solutions,num_ants,k_best)
        #print("dependancy",dependancy)
            
        # Mise à jour des phéromones
        for k in range(len(k_best_solutions)):
            pheromones = updatePheromones(pheromones,[k_best_solutions[k][0]], gamma=gamma, rho=rho, evaporation=True if k==0 else False )

    

        # Synchronisation des phéromones
        pheromones = comm.bcast(pheromones, root=0)

    return G, pheromones, best_solution, best_makespan, makespan_updates


if __name__ == "__main__":
    G, pheromones, best_solution, best_makespan, makespan_update = main()
    #vizualisationGraphs(best_solution[0],G)
    if rank ==0:
        vizualisationTaskProcessor(best_solution[1], best_solution[2], best_makespan)
        displayerPheromones(pheromones)
        #plt.figure()
        #plt.plot(makespan_update)
        plt.show()
