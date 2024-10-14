from matplotlib import pyplot as plt
import networkx as nx
import numpy as np

# Affiche la solution sous la forme "d'emploi du temps"
# processors : liste des listes des taches a effectuer pour chaque cpu (-1=idle)
# durations : liste des durées associées à chacune des ces taches (même structure avec des durées à la place)
def vis_schedule(processors, durations, text=True):

    # Création d'une palette de couleurs pour les tâches
    task_colors = plt.cm.tab10.colors

    # Création du graphique
    plt.figure(figsize=(10, 6))

    # Parcours des processeurs
    for i, (successive_durations, tasks) in enumerate(zip(durations, processors)):
        start_time = 0  # Initialisation du temps de départ pour chaque processeur
        current_task = None  # Tâche actuelle du processeur
        # Parcours des temps de travail ou d'attente pour chaque processeur
        for j, duration in enumerate(successive_durations):
            # Extraction du nom de la tâche et du temps d'attente
            task = tasks[j]
            # Vérification si la tâche actuelle a changé
            if task != current_task:
                current_task = task
                if current_task == -1:
                    current_color = "white"
                else:
                    current_color = task_colors[int(current_task) % len(task_colors)]  # Couleur de la tâche
            # Affichage de la barre horizontale pour le temps de travail ou d'attente
            if duration != -1:
                plt.barh(i, duration, left=start_time, height=0.5, align='center', color=current_color, alpha=0.5)
                if text:
                    if task == -1 :
                        plt.text(start_time + duration / 2, i, f'{"idle"}', ha='center', va='center', color='black')
                    else:
                        plt.text(start_time + duration / 2, i, '{}\n({:.0f})'.format(task, duration), ha='center', va='center', color='black')  
            
            start_time += duration if duration != -1 else 1  # Mise à jour du temps de départ

    # Paramètres d'affichage
    plt.yticks(range(len(durations)), [f'Processeur {i+1}' for i in range(len(durations))])
    plt.xlabel('Temps')
    plt.title('Représentation des temps de travail ou d\'attente pour chaque processeur')
    plt.grid(axis='x')


def displayerPheromones(pheromones):
    
    plt.figure()
    # Création du heatmap
    plt.imshow(pheromones.todense(), cmap='viridis', interpolation='nearest')
    plt.colorbar()

    # Ajout de titres et de labels
    plt.title('Matrice des phéromones')
    plt.xlabel('Colonnes')
    plt.ylabel('Lignes')

def format_makespan(makespan_seconds):
    # Convert makespan from seconds to days, hours, minutes, and remaining seconds
    days = makespan_seconds // (24 * 3600)
    hours = (makespan_seconds % (24 * 3600)) // 3600
    minutes = (makespan_seconds % 3600) // 60
    seconds = makespan_seconds % 60

    # Print the makespan in the desired format
    print(f"Makespan: {makespan_seconds:.0f}s\n/\n {days:.0f} jrs, {hours:.0f} h {minutes:.0f} min et {seconds:.0f} s")

def vizualisationTaskProcessor(processors,processor_successive_duration,best_makespan):
    
    print( "makespan :", best_makespan)

    vis_schedule(processors=processors,durations=processor_successive_duration)

def vizualisationGraphs(priority_list,G,multiples_paths = False):
    if multiples_paths== False:
        best_path = priority_list

        # Création du graphique avec NetworkX
        plt.figure(figsize=(10, 6))

        # Dessiner le graphique G avec une disposition circulaire
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True)

        # Ajouter le chemin de la meilleure solution sur le graphique
        edges_best_path = [(best_path[i], best_path[i+1]) for i in range(len(best_path)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=edges_best_path, edge_color='r', width=2)

        # Ajouter les temps à côté des nœuds
        for node, (x, y) in pos.items():
            if 'weight' in G.nodes[node]:
                plt.text(x-0.05, y+0.05, str(G.nodes[node]['weight'])+"secs", ha='center', fontsize=15)

        # Afficher le graphique
        plt.title('Graphique avec le chemin de la meilleure solution et les temps à côté des nœuds')

        plt.figure()
        # Dessiner le graphe
        nx.draw(G, with_labels=True, node_size=1000, node_color='skyblue', arrowsize=20)

        # Ajouter les étiquettes des nœuds
        pos = nx.spring_layout(G)  # Déterminer la disposition des nœuds
    
    else:
        # Création du graphique avec NetworkX
        plt.figure(figsize=(10, 6))

        # Dessiner le graphique G avec une disposition circulaire
        pos = nx.shell_layout(G)
        # Dessiner le graphe
        nx.draw(G,pos, with_labels=True, node_size=1000, node_color='skyblue', arrowsize=20)
        # Ajouter les temps à côté des nœuds
        for node, (x, y) in pos.items():
            if 'weight' in G.nodes[node]:
                plt.text(x-0.05, y+0.05, str(G.nodes[node]['weight'])+"secs", ha='center', fontsize=15)
        
        def generationDesCouleurs(index):
            couleur = ["r","b","g","y","c","m","k"]
            return couleur[index]
        
        for index, best_path in enumerate(priority_list):
            best_path = np.array(best_path)
            best_path = best_path[best_path != -1]
            # Ajouter le chemin de la meilleure solution sur le graphique
            edges_best_path = [(best_path[i], best_path[i+1]) for i in range(len(best_path)-1)]
            nx.draw_networkx_edges(G, pos, edgelist=edges_best_path, edge_color=generationDesCouleurs(index), width=2)

            
        # Afficher le graphique
        plt.title('Graphique avec le chemin de la meilleure solution et les temps à côté des nœuds')

            

            
        
