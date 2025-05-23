import os
import json
import numpy as np
import networkx as nx
from transformers import AutoTokenizer, GPT2Tokenizer, LlamaTokenizer
from transformers import logging

logging.set_verbosity_error()

import re 


def get_edges_from_str(matrix_str):
    """    
    :param matrix_str: str, 
    :return: list of tuples, 
    """

    if matrix_str.strip() == "[]":
        return []
    
    rows = matrix_str.split("]")


    matrix_list = []
    for row in rows:
        numbers = re.findall(r'\d+', row) 
        if numbers:  
    
            matrix_list.append(list(map(int, numbers)))  

    num_rows = len(matrix_list)
    if any(len(row) != num_rows for row in matrix_list):  
        raise ValueError(f"{[len(row) for row in matrix_list]}")


    matrix = np.array(matrix_list)


    edges = [(i, j) for i in range(matrix.shape[0]) for j in range(i+1, matrix.shape[1]) if matrix[i, j] == 1]

    return edges




logging.set_verbosity_error()

def count_tokens(text):
    from transformers import AutoTokenizer, LlamaTokenizer


    bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    llama_tokenizer = LlamaTokenizer.from_pretrained("/u3/w3pang/HAO_Graphllm/llm/llama2")


    if not hasattr(llama_tokenizer, 'pad_token') or llama_tokenizer.pad_token is None:
        llama_tokenizer.pad_token = llama_tokenizer.eos_token


    bert_tokens = bert_tokenizer.encode(text, add_special_tokens=True, truncation=False)
    llama_tokens = llama_tokenizer.encode(text, truncation=False)


    max_token_count = max(len(bert_tokens), len(llama_tokens))


    return max_token_count


def create_adj_matrix(nodes, edges):
    n = len(nodes)
    adj_matrix = np.zeros((n, n), dtype=int)
    
    for source, target in edges:
        adj_matrix[source][target] = 1
        adj_matrix[target][source] = 1  
    
    return adj_matrix
def get_adjlist_from_str(matrix_str):



    if matrix_str.strip() == "[]":
        return []
    
    rows = matrix_str.split("]")


    matrix_list = []
    for row in rows:
        numbers = re.findall(r'\d+', row)  
        
        if numbers:  

            matrix_list.append(list(map(int, numbers)))  


    num_rows = len(matrix_list)
    if any(len(row) != num_rows for row in matrix_list):  
        raise ValueError(f" {[len(row) for row in matrix_list]}")


    matrix = np.array(matrix_list)


    adj_list = {i: [] for i in range(len(matrix))}
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] > 0:  
                
                adj_list[i].append(j)
    return adj_list

def parse_gml(gml_str):
    nodes = {}
    edges = []
    
    node_pattern = re.compile(r'node\s*\[\s*id\s+(\d+)\s*label\s*"(\d+)"\s*\]')
    edge_pattern = re.compile(r'edge\s*\[\s*source\s+(\d+)\s*target\s+(\d+)\s*\]')
    
    for match in node_pattern.finditer(gml_str):
        node_id, label = match.groups()
        nodes[int(node_id)] = label

    for match in edge_pattern.finditer(gml_str):
        source, target = match.groups()
        edges.append((int(source), int(target)))

    return nodes, edges

def getgraphinfo(query_msd,serialization_type,name_id):
    query_msd=query_msd.lower()
    split_parts = query_msd.split(serialization_type.lower())
    graphinfo = split_parts[-1].split("q:")
    if len(graphinfo)==2:
        graphinfo = graphinfo[0]
        graphinfo=graphinfo.replace('is','')
        graphinfo = graphinfo.strip()
    else:
        print('graphinfo not right')


    if serialization_type=='Adjacency Matrix':
            edges=get_edges_from_str(graphinfo)
            if name_id=='shortest_path-easy-none-Adjacency Matrix-210':
                print(query_msd)
                print('-------------------')               
                print(split_parts[-1])
                print('-------------------')
                print(graphinfo)
                print('-------------------')


            return graphinfo, edges

    elif serialization_type=='Graph Modelling Language':
            nodes, edges = parse_gml( graphinfo)
            matrixstr=create_adj_matrix(nodes, edges)

            return str(matrixstr), edges



def getamgmlquery(query_data_list,nameid,prompt_type,task_type,serialization_type,difficulty):

    for query_item in query_data_list:

        query_name_id = query_item.get('name-id')
        query_msd = query_item.get('query')
        
        if query_name_id==nameid and '-'.join([task_type, difficulty, prompt_type, serialization_type]) in nameid:

            matrixstr, edges=getgraphinfo(query_msd,serialization_type,nameid)
    
    if query_name_id=='shortest_path-easy-none-Adjacency Matrix-210':
        print(query_msd)
    return matrixstr, edges

