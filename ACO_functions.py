import numpy as np

# Arguments par défaut :
#alpha = 1  # Influence de la phéromone sur la transition
#beta = 1  # Influence de la distance sur la transition
#gamma = 1  # Paramètre pour la mise à jour des phéromones
#rho = 0.1  # Taux d'évaporation des phéromones

def distanceBeta(num_jobs,tasks_durations, beta=1):
    distance_beta = np.zeros(num_jobs+1)
    distance_beta[1:] = 1/tasks_durations[1:]**beta
    return distance_beta

# Fonction pour calculer la probabilité de transition entre le tâche actualle et les disponibles
# retourne le tableau numpy de toutes les probas des tâches dans available_tasks
def probabilityAvailableTasks(pheromones,current_task,available_tasks,distance_beta, alpha=1, tmt=1.): # tmt va décroitre 
    probas = (pheromones[current_task,available_tasks].toarray().flatten()+tmt)**alpha * distance_beta[available_tasks]
    return probas/np.sum(probas)


def getNextTask(pheromones, current_task, available_tasks, distance_beta, alpha=1, tmt=1.,Me=None):
    probas = probabilityAvailableTasks(pheromones,current_task, available_tasks,distance_beta, alpha=alpha, tmt=tmt)
    chosen = np.random.choice(available_tasks, p=probas)
    if Me is None:
        available_tasks.remove(chosen)
        return chosen
    else:
        chosen=np.random.choice(available_tasks, p=probas,size=Me+1,replace=False)

        return chosen
        

# After finished a task, we update the available tasks
def updateAvailableTasks(childs,done_task, available_tasks, nb_parents,Me=None):
    if done_task == -1: # waiting task
        return available_tasks
    childs=childs[done_task]
    if childs.size==0:
        return available_tasks
    nb_parents[childs]-=1
    new_task_available=childs[nb_parents[childs]==0]
    if Me is None:
        available_tasks.extend(new_task_available)
    else:
        available_tasks=np.concatenate([available_tasks,new_task_available])
    return available_tasks

def dependancyTasks(edges,num_jobs):
    dependancy = [[] for i in range(num_jobs)]
    for i,j in edges:
        if i != 0:
            dependancy[j-1].append(i)
    return dependancy
    
def findProcessor(task,processors):
    for i in range(len(processors)):
        if processors[i][-1] == task:
            return i
    return "cette tâche n'a pas été encore attribuée"

def dispatcher(dependancy,num_processor,task,processors,processors_availibility,processors_successive_duration,job_duration_ls):
    duration = job_duration_ls[task]
    best_processor = -1
    all_done = True
    parent_task = -1
    max_parent_duration_last = -1
    
    #on vérifie si toutes les tâches parents de task ont été effectué
    #print("la tâche choisie est :",task)
    for t in dependancy[task-1]:
        #print("on teste son parent :",t)
        #print("processors",processors)
        if dependancy[t-1] == [] or dependancy[t-1][-1] != "Done":
            all_done = False
            processor = findProcessor(t, processors)  #on trouve le processor en train de faire cette tâche
            #print("processor",processor)
            if processors_availibility[processor] >= max_parent_duration_last:
                parent_task = t   #tâche parent la plus longue à finir avant 
                max_parent_duration_last = processors_availibility[processor]
    
    # Recherche du processeur avec la disponibilité minimale
    best_processor = np.argmin(processors_availibility)
    
    #print("on met la tâche", task,"dans le processor:",best_processor)
        
    #Si toutes les tâches parents ont été terminées :
    if all_done :        
        # Mise à jour des informations du processeur choisi
        processors[best_processor].append(task)
        processors_successive_duration[best_processor].append(duration)
        processors_availibility[best_processor] = duration
        
    else :
        # Mise à jour des informations du processeur choisi
        waiting_time = max_parent_duration_last
        processors[best_processor].append(-1) # waiting time
        processors_successive_duration[best_processor].append(waiting_time)
         
        processors[best_processor].append(task)
        processors_successive_duration[best_processor].append(duration)
        processors_availibility[best_processor] = waiting_time + duration
        
        
    #On décrémente tous les compteurs du temps minimale d'un des processors
    """min_finish_time = float('inf')
    processor = -1
    for i in range(num_processor):
        if processors_availibility[i] <= min_finish_time :
            processor = i
            min_finish_time = processors_availibility[i]"""
    
    # Décrémentation des compteurs de temps des processeurs
    min_finish_time = np.min(processors_availibility)
    processors_availibility -= min_finish_time
    
    for i in range(num_processor):
        #processors_availibility[i] -= min_finish_time
        if processors_availibility[i] == 0 and processors[i] != []:
            last_task = processors[i][-1]  #va de 1 à num_jobs alors que dependancy va de 0 à num_jobs-1
            if dependancy[last_task-1] == [] or dependancy[last_task-1][-1] != "Done" :
                dependancy[last_task-1].append("Done")
    
# Only winner rewards
def updatePheromones(pheromones, best_paths, gamma=1, rho=0.1, tmt=1., next_tmt=1., tmax=10, evaporation=True): # MMAS 
    if evaporation:
        pheromones = pheromones.tocsr()
        pheromones.data = np.clip((pheromones.data+tmt)*(1 - rho), tmt, tmax) -next_tmt
        pheromones=pheromones.tolil()
        
    # remove waiting tasks
    paths = [np.array(leg_path) for leg_path in best_paths]
    paths = [leg_path[leg_path != -1] for leg_path in paths]
    for leg_path in paths:
        pheromones[leg_path[:-1], leg_path[1:]
                   ] += np.ones((leg_path.shape[0]-1))*gamma
    return pheromones

def makespan(processors_successive_duration):
    makespan = -1
    for i in range(len(processors_successive_duration)):
        if sum(processors_successive_duration[i]) >= makespan:
            makespan = sum(processors_successive_duration[i])
    return makespan

def kBestSolutions(k_best_solutions,solutions,num_ants,k):
    makespans = np.zeros(len(solutions))
    
    gather_solutions = k_best_solutions + solutions
    
    for i, solution in enumerate(gather_solutions):
        makespans[i] = makespan(solution[2])
        
    # Obtenir les indices des k meilleures solutions
    indices_k_best = np.argsort(makespans)[:k]
    
    # Récupérer les k meilleures solutions à partir de la liste solutions
    k_best_solutions = [gather_solutions[i] for i in indices_k_best]
    
    
    return k_best_solutions,k_best_solutions[0],makespans[indices_k_best[0]]

def convert_childs_to_edges(childs):
    edges = []
    num_nodes = len(childs)

    # Parcourir chaque nœud (indice i) dans childs
    for i in range(num_nodes):
        children = childs[i]  # Récupérer la liste des enfants du nœud i

        # Pour chaque enfant j de i, créer une arête (i, j)
        for j in children:
            edges.append((i, j))  # Ajouter l'arête (i, j) à la liste des arêtes

    return edges