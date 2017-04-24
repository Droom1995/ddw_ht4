import nltk
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import operator

casts=pd.read_csv("casts.csv",header=None, delimiter=";",  names=list(range(0,5)))
films_cast = {}
actors = set()
count = 100
for index, row in casts.iterrows():
    count -= 1
    if count == 0:
        break
    if row[1] in films_cast:
        films_cast[row[1]].append(row[2])
    else:
        films_cast[row[1]] = []

new_casts = films_cast.copy()
for key, value in films_cast.items():
    if len(value)<5:
        del new_casts[key]
    else:
        for actor in value:
            actors.add(actor)
films_cast = new_casts
# input text

G=nx.Graph()

for key, value in films_cast.items():
    for actor in value:
        for neigbor in value:
            if neigbor != actor:
                G.add_edge(actor, neigbor)

print("Number of nodes/edges: ", G.number_of_nodes(), G.number_of_edges())
print("Density: ", nx.density(G))
con_comps = []
# print("Connected components:")
for component in nx.connected_components(G):
    #     print(component)
    con_comps.append(component)
print("Number of connected components: ", len(con_comps))

pos = graphviz_layout(G, prog="fdp")
plt.title("Centralities")
nx.draw(G, pos, labels={v: str(v) for v in G},
        cmap=plt.get_cmap("bwr"),
        node_color=[nx.degree_centrality(G)[k] for k in nx.degree_centrality(G)], scale=2)
plt.savefig("centralities.png")
centralities = [nx.degree_centrality, nx.closeness_centrality,
                nx.betweenness_centrality, nx.eigenvector_centrality]
print("Top central actors:")
for centrality in centralities:
    print(sorted(centrality(G).items(), key=operator.itemgetter(1), reverse=True)[:5])
    nx.set_node_attributes(G, centrality.__name__, centrality(G))

paths = dict()
average_bacon = 0
for s in G:
    paths[s] = nx.single_source_shortest_path(G, s)
    average_bacon += paths[s]
print("Top Kevin Bacon actors:")
print(sorted(paths.items(), key=operator.itemgetter(1), reverse=True)[:5])
print("Top anti-Kevin Bacon actors:")
print(sorted(paths.items(), key=operator.itemgetter(1), reverse=False)[:5])
print("Average distance:")
print(average_bacon/G.number_of_nodes())
nx.set_node_attributes(G, "Bacon number", paths)
communities = {node: cid + 1 for cid, community in enumerate(nx.k_clique_communities(G, 3)) for node in community}

pos = graphviz_layout(G, prog="fdp")
nx.draw(G, pos,
        labels={v: str(v) for v in G},
        cmap=plt.get_cmap("rainbow"),
        node_color=[communities[v] if v in communities else 0 for v in G])
plt.savefig("communities.png")
nx.set_node_attributes(G, "community", communities)
# write to GEXF
nx.write_gexf(G, "export.gexf")
