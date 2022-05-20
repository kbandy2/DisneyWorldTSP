# -*- coding: utf-8 -*-
"""
Created on Wed May 11 21:14:46 2022

@author: kyleb
"""


import pandas as pd
import urllib3
import ast
from collections import defaultdict
from geopy import distance
import networkx as nx
from networkx.algorithms import approximation

def get_all_attractions():
    http = urllib3.PoolManager()
    
    response = http.request('GET', "https://touringplans.com/magic-kingdom/attractions.json")
    
    mk_attractions = response.data.decode("utf-8")
    
    mk_attractions = ast.literal_eval(mk_attractions)
    
    return mk_attractions

mk_attractions = get_all_attractions()

attraction_names = [i['permalink'] for i in mk_attractions]


def get_attraction_info(attraction):
    http = urllib3.PoolManager()
    url = "https://touringplans.com/magic-kingdom/attractions/" + attraction + ".json"
    response = http.request('GET', url)
    output = response.data.decode("utf-8").replace("null", "0").replace("true", "True").replace("false", "False")
    return ast.literal_eval(output)


coord_dict = defaultdict(int)



for i in attraction_names:
    attraction_info = get_attraction_info(i)
    coord_dict[i] = {"lat": attraction_info['latitude'], "lon": attraction_info['longitude']}

dist_mat = defaultdict(int)

for i in attraction_names:
    for j in attraction_names:
        if i !=j:
            loc1 = (coord_dict[i]["lat"], coord_dict[i]["lon"])
            loc2 = (coord_dict[j]["lat"], coord_dict[j]["lon"])
            mi = distance.distance(loc1, loc2).miles
            dist_mat[(i,j)] = mi
        
G = nx.Graph()

for i in dist_mat:
    G.add_edge(i[0], i[1], weight=dist_mat[i])




tsp = approximation.traveling_salesman_problem

optimal_route = tsp(G, nodes = attraction_names, cycle=False)


optimal_route_df = pd.DataFrame({"Attraction": optimal_route})

optimal_route_df['Attraction Name'] = optimal_route_df["Attraction"].apply(lambda x: get_attraction_info(x)['name'])

optimal_route_df['lat'] = optimal_route_df['Attraction'].apply(lambda x: coord_dict[x]['lat'])
optimal_route_df['lon'] = optimal_route_df['Attraction'].apply(lambda x: coord_dict[x]['lon'])




