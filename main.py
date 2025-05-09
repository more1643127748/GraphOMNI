
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
from datasets import load_dataset

from vllm import LLM, SamplingParams
from openllm import predict, loadllm,loadqwen38,Qwen38B_chat
from eval_fun import * 
from dotenv import load_dotenv
load_dotenv()

tasks =[ 'connectivity','bfsorder','triangle', 'diameter','cycle','shortest_path','all']
models=["Llama3.1","Mistral","Phi-4","Qwen2.5","Qwen3-8B"]
modes = ["easy", "medium", "hard"]
outputformats=['Graph Modelling Language','Adjacency Set',  'Edge Set', 'Edge List', 'Adjacency Matrix', 'Adjacency List', 'GraphML']      
prompts = ["Algorithm","CoT","k-shot", "Instruct", "none", "0-CoT", "0-Instruct", "0-Algorithm","LTM"]     

parser = argparse.ArgumentParser(description="Omni Benchmark Runner")

# Add arguments with value restrictions using `choices`
parser.add_argument('--model', type=str, default="Llama3.1", choices=models,
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


def merge_task_jsons_by_task(task,source_root, target_folder):
    tasks = [task]
    
    os.makedirs(target_folder, exist_ok=True)
    for task in tasks:
        task_folder = os.path.join(source_root, task)
        merged_data = []
        if not os.path.exists(task_folder):
            print(f"Warning: {task_folder} not found, skipping.")
            continue
        for filename in os.listdir(task_folder):
            if filename.endswith('.json'):
                file_path = os.path.join(task_folder, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        merged_data.extend(data)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        output_path = os.path.join(target_folder, f"load_{task}.json")
        with open(output_path, 'w', encoding='utf-8') as out_file:
            json.dump(merged_data, out_file, indent=2, ensure_ascii=False)
        print(f"{task} merged JSON saved to: {output_path}")

def evaltask(answer, gtanswer_str,graphinfo):
    if args.task=='cycle':
        gt='true' in gtanswer_str.lower()
        model_acc=eval_cycle(answer.lower(),gt)
        model_extract=model_acc
        if model_extract == None:
            model_acc=0
        return model_acc,model_extract
    elif args.task=='connectivity':
        numbers = re.findall(r'\d+', gtanswer_str)
        numbers = [int(num) for num in numbers]
        start=numbers[0]
        end=numbers[-1]
        edges  = get_edges_from_str(graphinfo)
        graph=build_graph(edges)
        gt=check_is_connected(graph, start, end)
        model_acc=eval_connectivity(answer.lower(),gt)
        model_extract=model_acc
        if model_extract == None:
            model_acc=0    
        return model_acc,model_extract      
        
    elif args.task=='bfsorder':
        numbers = re.findall(r'\d+', gtanswer_str)
        numbers = [int(num) for num in numbers]
        start=numbers[0]
        edges  = get_edges_from_str(graphinfo)
        x,model_acc=evaluate_bfsorder(answer.lower(),edges ,start)
        model_extract=model_acc
        if model_extract ==None:     
            model_acc=0
        return model_acc,model_extract      
    
    elif args.task=='shortest_path': 
        numbers = re.findall(r'\d+', gtanswer_str)
        numbers = [int(num) for num in numbers]
        start=numbers[0]
        end=numbers[-1]
        edges  = get_edges_from_str(graphinfo)
        x,model_acc=evaluate_shortest_path(answer.lower(),edges ,start, end,numbers)
        model_extract=model_acc
        if model_extract ==None:     
            model_acc=0
        return model_acc,model_extract  
    elif args.task=='triangle': 
        gtanswer=int(gtanswer_str)
        model_acc=eval_triangle_number(answer.lower(),gtanswer)
        model_extract=model_acc
        if model_extract == None:
            model_acc=0    
        return model_acc,model_extract      
    
    elif args.task=='diameter': 
        gtanswer=float(gtanswer_str)
        model_acc=eval_diameter_number(answer.lower(),gtanswer)
        model_extract=model_acc
        if model_extract == None:
            model_acc=0    
        return model_acc,model_extract   
    else:
        print('task not include')
        return None      
  
def main():
    
    if args.model=="Qwen3-8B":
        tokenizer,model=loadqwen38()
    else:
        llmmodel=loadllm(args)
    
    
    file1 = f'./results/im_jsonfile/{args.task}/{args.task}-{args.mode}-{args.prompt}-{args.graph_representation}.json'

    if not os.path.exists(file1):
        print('json_data not found load from hug')
        ds = load_dataset("G-A-I/GraphOmni", split=args.task)
        json_data = ds.to_list()
        os.makedirs(os.path.dirname(file1), exist_ok=True)
    else:
        with open(file1, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

    new_json_data=[]
    for i in range(len(json_data)):        
        json_dict=json_data[i]
        if json_dict['difficulty'] == args.mode and json_dict['serialization_type']==args.graph_representation and json_dict['prompt_type'] ==args.prompt and json_dict['task_type'] ==args.task:
            query=json_dict["query"]
            model=args.model
            model_response = json_dict.setdefault("model_response", {})
            model_acc = json_dict.setdefault("model_acc", {})
            model_extract = json_dict.setdefault("model_extract", {})
            if model not in model_response:
                #answer="yes"
                if args.model=="Qwen3-8B":
                    thinking_content, answer  = Qwen38B_chat(tokenizer,model,query)
                else:
                    answer = predict(llmmodel, [query], args)[0]
                    
                gtanswer_str=json_dict["gt_answer"]
                graphinfo=json_dict["graph_info"]
                acc,extract=evaltask(answer,gtanswer_str,graphinfo)
                model_response[model]=answer
                model_acc[model]=acc
                model_extract[model]=extract
            else:
                print(f"'{model}' exist in json")     
            
            new_json_data.append(json_dict)
            break
            
    filename = './results/im_jsonfile/'+args.task+'/'+args.task+'-'+args.mode+'-'+args.prompt+'-'+args.graph_representation+'.json'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(new_json_data, file, ensure_ascii=False, indent=4)
    
    merge_task_jsons_by_task(args.task,source_root='./results/im_jsonfile', target_folder='./results/agg_jsonfile')
    



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
