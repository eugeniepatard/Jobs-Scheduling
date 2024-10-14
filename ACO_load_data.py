'''
list "job_ls" store all the job in a list  

list "job_duration_ls" their corresponding duration 

      base on their index (start from 0) in this list, we attribute a new name to each job (the index in "job_ls")

dict "map_node_to_new_index"  keys: job original name, values : their index in "job list"  

nx.Digraph "Graphe_dep"  use index to create the dependency graph

'''
import json
import networkx as nx
import numpy as np
import os

def load_data(file_name):
  #load data
  file_path=os.getcwd()
  with open(file_path + '/' + file_name ) as f:
    data = json.load(f)
  print(type(data))

  #initialisation 

  dependencies_dict = {}
  Graphe_dep = nx.DiGraph()
  job_ls = ['0']
  job_duration_ls = [0]
  job_new_index = 1
  Graphe_dep.add_node(0)
  ls_job = list(data['nodes'].keys()) 
  new_names = np.arange(1,len(ls_job)+1)
  map_node_to_new_idx = dict(zip(ls_job,new_names))

  # graph generate (with one loop)
  for job in data['nodes'].keys():
      duration_ls = data['nodes'][job]['Data'].split(':')
      job_duration = float(duration_ls[0])*60*60+float(duration_ls[1])*60+float(duration_ls[2]) #unit second
      
      Graphe_dep.add_node ( job_new_index )

      job_ls.append(job)
      job_duration_ls.append(job_duration)
      
      Dependencies_ls = []
      for parent in data['nodes'][job]["Dependencies"]:
        Dependencies_ls.append(map_node_to_new_idx[str(parent)])
        Graphe_dep.add_edge(map_node_to_new_idx[str(parent)],job_new_index, weight=job_duration)
      
      dependencies_dict[str(job_new_index)] = Dependencies_ls
      job_new_index+=1
  return Graphe_dep,job_duration_ls,job_ls

def preprocess(graph_file, output_folder):
  print("preprocessing file '" + graph_file + "' in '"+output_folder+"'...")


  with open(graph_file) as f:
    data = json.load(f)
  print('loaded')
  Graphe_dep = nx.DiGraph()

  job_duration_ls = [0]
  job_new_index = 1
  Graphe_dep.add_node(0)
  
  ls_job = list(data['nodes'].keys()); new_names = np.arange(1,len(ls_job)+1)
  map_node_to_new_idx = dict(zip(ls_job,new_names))
  childs = np.zeros(len(ls_job)+1, dtype=object)
  childs = [[] for node in range(childs.size)]

  # graph generate (with one loop)
  for job in tqdm(data['nodes'].keys()):
      duration_ls = data['nodes'][job]['Data'].split(':')
      job_duration = float(duration_ls[0])*60*60+float(duration_ls[1])*60+float(duration_ls[2]) #unit second
      
      Graphe_dep.add_node ( job_new_index )

      job_duration_ls.append(job_duration)
      
      Dependencies_ls = []
      for parent in data['nodes'][job]["Dependencies"]:
        Dependencies_ls.append(map_node_to_new_idx[str(parent)])
        Graphe_dep.add_edge(map_node_to_new_idx[str(parent)],job_new_index, weight=job_duration)
        
        childs[map_node_to_new_idx[str(parent)]].append(job_new_index)
      
      job_new_index+=1

  num_jobs = int(Graphe_dep.number_of_nodes()-1)
  nb_parents = np.array([len(list(Graphe_dep.predecessors(node))) for node in range(num_jobs+1)]) 
  
  longest_path = nx.dag_longest_path_length(Graphe_dep)

  os.makedirs(output_folder, exist_ok=True)
  np.savez_compressed(output_folder + "/arr.npz", tasks_durations=job_duration_ls, nb_parents=nb_parents, longest_path=longest_path, num_jobs=num_jobs)

  del Graphe_dep

  import pickle
  
  dic = open(output_folder+ "/dic.pkl","wb")
  pickle.dump(childs,dic)
  dic.close()


def load_preprocessed(folder):
  f = np.load(folder+"/arr.npz")
  tasks_durations = f["tasks_durations"]
  nb_parents = f["nb_parents"]
  longest_path = int(f["longest_path"])
  num_jobs = int(f["num_jobs"])
  f.close()

  import pickle
  with open(folder+"/dic.pkl", 'rb') as fp:
    childs = pickle.load(fp)


  childs=[np.array(_) for _ in childs] # ne surtout pas le faire dans le preprocessing

  
  return tasks_durations, nb_parents, longest_path, num_jobs, childs

if __name__=="__main__":
  from tqdm import tqdm
  # preprocess("Graphs/smallComplex.json","Preprocessed/smallComplex")
  # preprocess("Graphs/MediumComplex.json","Preprocessed/MediumComplex")
  # preprocess("Graphs/largeComplex.json","Preprocessed/largeComplex")
  # preprocess("Graphs/xlargeComplex.json","Preprocessed/xlargeComplex")
  preprocess("Graphs/smallRandom.json","Preprocessed/smallRandom")
  # print(load_preprocessed("Preprocessed/xlargeComplex"))
  exit()