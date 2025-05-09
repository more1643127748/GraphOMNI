import os
import re
import json
import time
import fire
import torch
import random
import argparse
import numpy as np
import pandas as pd
import networkx as nx
from tqdm import tqdm
from datetime import datetime, timedelta, timezone

# Transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

# External or custom libraries
import openai
from vllm import LLM, SamplingParams
from openllm import predict, loadllm,loadqwen38,Qwen38B_chat
from eval_fun import * 
from dotenv import load_dotenv
load_dotenv()

tasks =[ 'connectivity','bfsorder','triangle', 'diameter','cycle','shortest_path','all']
models=["gpt-4o-mini"]
modes = ["easy", "medium", "hard"]
outputformats=['Graph Modelling Language','Adjacency Set',  'Edge Set', 'Edge List', 'Adjacency Matrix', 'Adjacency List', 'GraphML']      
prompts = ["Algorithm","CoT","k-shot", "Instruct", "none", "0-CoT", "0-Instruct", "0-Algorithm","LTM"]     

parser = argparse.ArgumentParser(description="Omni Benchmark Runner")

# Add arguments with value restrictions using `choices`
parser.add_argument('--model', type=str, default="gpt-4o-mini", choices=models,
                    help=f"Select the model to use (default: Llama3.1). Options: {models}")

parser.add_argument('--mode', type=str, default="easy", choices=modes,
                    help=f"Run difficulty mode (default: easy). Options: {modes}")

parser.add_argument('--prompt', type=str, default="LTM", choices=prompts,
                    help=f"Prompting strategy (default: LTM). Options: {prompts}")

parser.add_argument('--graph_representation', type=str, default="Adjacency Set", choices=outputformats,
                    help=f"Graph input format (default: Adjacency Set). Options: {outputformats}")

parser.add_argument('--task', type=str, default="cycle", choices=tasks,
                    help=f"Graph reasoning task to perform (default: cycle). Options: {tasks}")

# Parse arguments
args, unknown = parser.parse_known_args()


def evaltask(anwser, gtanwser_str,graphinfo):
    if args.task=='cycle':
        gt='true' in gtanwser_str.lower()
        model_acc=eval_cycle(anwser.lower(),gt)
        model_extract=model_acc
        if model_extract == None:
            model_acc=0
        return model_acc,model_extract

    elif args.task=='connectivity':
        numbers = re.findall(r'\d+', gtanwser_str)
        numbers = [int(num) for num in numbers]
        start=numbers[0]
        end=numbers[-1]
        edges  = get_edges_from_str(graphinfo)
        graph=build_graph(edges)
        gt=check_is_connected(graph, start, end)

        model_acc=eval_connectivity(anwser.lower(),gt)
        model_extract=model_acc
        if model_extract == None:
            model_acc=0    
        return model_acc,model_extract      
        
    elif args.task=='bfsorder':
        numbers = re.findall(r'\d+', gtanwser_str)
        numbers = [int(num) for num in numbers]
        start=numbers[0]
        edges  = get_edges_from_str(graphinfo)
        x,model_acc=evaluate_bfsorder(anwser.lower(),edges ,start)
        model_extract=model_acc
        if model_extract ==None:     
            model_acc=0
        return model_acc,model_extract      
    
    elif args.task=='shortest_path': 
        numbers = re.findall(r'\d+', gtanwser_str)
        numbers = [int(num) for num in numbers]
        start=numbers[0]
        end=numbers[-1]

        edges  = get_edges_from_str(graphinfo)
        x,model_acc=evaluate_shortest_path(anwser.lower(),edges ,start, end,numbers)
        model_extract=model_acc
        if model_extract ==None:     
            model_acc=0
        return model_acc,model_extract  

    elif args.task=='triangle': 
        gtanwser=int(gtanwser_str)
        model_acc=eval_triangle_number(anwser.lower(),gtanwser)
        model_extract=model_acc
        if model_extract == None:
            model_acc=0    
        return model_acc,model_extract      
    
    elif args.task=='diameter': 
        gtanwser=float(gtanwser_str)
        model_acc=eval_diameter_number(anwser.lower(),gtanwser)
        model_extract=model_acc
        if model_extract == None:
            model_acc=0    
        return model_acc,model_extract   

    else:
        print('task not include')
        return None      
def getquery(args):

    filename = f'./results/agg_jsonfile/load_{args.task}.json'
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
    else:
        json_data = []
        print(f'./results/agg_jsonfile/load_{args.task}.json not exist')

    return json_data



def main():
    
    json_data=getquery(args)

    file_path = "./closedllm/openailog/content/all_id_answer_dict_"+args.model+".json"
    with open(file_path, 'r+', encoding='utf-8') as file:
        all_id_answer_dict = json.load(file)
    for i in range(len(json_data)):
        json_dict=json_data[i]
        query=json_dict["query"]
        model=args.model
        
        model_response = json_dict.setdefault("model_response", {})
        model_acc = json_dict.setdefault("model_acc", {})
        model_extract = json_dict.setdefault("model_extract", {})

        if model not in model_response:
            name_id = json_dict['name-id']
            if name_id in all_id_answer_dict and model not in model_response.keys():
                anwser=all_id_answer_dict[name_id]
                    
                gtanwser_str=json_dict["gt_answer"]
                graphinfo=json_dict["graph_info"]

                acc,extract=evaltask(anwser,gtanwser_str,graphinfo)
                model_response[model]=anwser
                model_acc[model]=acc
                model_extract[model]=extract
        else:
            print(f"'{model}' exist in json")
        

    filename = f'./results/jsonfile/load_{args.task}.json'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    if args.task=='all':
        for task in tasks:
            for mode in modes:
                for outputformat in outputformats:
                     for prompt in prompts:
                        args.task = task
                        args.mode = mode
                        args.prompt = prompt
                        args.graph_representation=outputformat
                        main()
    else:
        main()

