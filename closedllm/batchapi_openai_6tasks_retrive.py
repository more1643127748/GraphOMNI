from openai import OpenAI
import openai
import os
import re
import json
import random
import datetime
import argparse
import logging
from tqdm import tqdm
from openai import OpenAI
import openai
import os
import json
import random
import datetime
import argparse
import logging
from tqdm import tqdm
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')


tasks =[ 'connectivity','bfsorder','triangle', 'diameter','cycle','shortest_path','all']
models=["gpt-4o-mini"]
modes = ["easy", "medium", "hard"]
outputformats=['Graph Modelling Language','Adjacency Set',  'Edge Set', 'Edge List', 'Adjacency Matrix', 'Adjacency List', 'GraphML']      
prompts = ["Algorithm","CoT","k-shot", "Instruct", "none", "0-CoT", "0-Instruct", "0-Algorithm","LTM"]     

parser = argparse.ArgumentParser( )

# Add arguments with value restrictions using `choices`
parser.add_argument('--model', type=str, default="gpt-4o-mini", choices=models,  help=f"Select the model to use (default: Llama3.1). Options: {models}")
parser.add_argument('--mode', type=str, default="easy", choices=modes, help=f"Run difficulty mode (default: easy). Options: {modes}")
parser.add_argument('--prompt', type=str, default="LTM", choices=prompts,  help=f"Prompting strategy (default: LTM). Options: {prompts}")
parser.add_argument('--graph_representation', type=str, default="Adjacency Set", choices=outputformats, help=f"Graph input format (default: Adjacency Set). Options: {outputformats}")
parser.add_argument('--task', type=str, default="cycle", choices=tasks, help=f"Graph reasoning task to perform (default: cycle). Options: {tasks}")
parser.add_argument("--max_completion_tokens", type=int, default=3000)
parser.add_argument("--base_dir", type=str, default="../results/agg_jsonfile/", help="Base directory containing the data")
parser.add_argument("--log_path", type=str, default="./openailog", help="Path to save the log file")

parser.add_argument("--max_tokens", type=int, default=3000)
parser.add_argument("--base_dir", type=str, default="../results/open_jsonfile/", help="Base directory containing the data")
parser.add_argument("--log_path", type=str, default="./openailog", help="Path to save the log file")

args = parser.parse_args()


def find_batch_ids_in_logs(args):
    log_folder_path = r'./openailog/log/' + args.task
    batch_id_pattern = re.compile(r"'batch_id':\s*'(\S+)'")
    batch_name_pattern = re.compile(r"'file_name':\s*'([^']+)'")
    batch_id_dict = {}

    for root, dirs, files in os.walk(log_folder_path):
        for file in files:
            if file.endswith('.log') and args.model + '-' + args.mode + '-' + args.prompt + '-' + args.graph_representation in file:
                log_file_path = os.path.join(root, file)

                with open(log_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if not lines:
                        continue
                    
                    last_line = lines[-1].strip()

                    if 'Application started successfully.' in last_line:
                        for line in lines:
                            batch_match = batch_id_pattern.search(line)
                            batch_name_match = batch_name_pattern.search(line)
                            
                            if batch_match and batch_name_match:
                                batch_id = batch_match.group(1)
                                batch_name = batch_name_match.group(1)
                                batch_id_dict[batch_name] = batch_id

    return batch_id_dict



def extract_data_from_jsonl(file_paths):
    result_dict = {}  
    
    for jsonlpath in file_paths:
        with open(jsonlpath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    
                    custom_id = data['custom_id']
                    content = data['response']['body']['choices'][0]['message']['content']
                    
                    result_dict[custom_id] = content
                
                except KeyError as e:
                    print(f"KeyError: Missing key {e} in file {jsonlpath}, line skipped.")
                except json.JSONDecodeError:
                    print(f"JSONDecodeError: Failed to decode JSON in file {jsonlpath}, line skipped.")
    
    return result_dict



def main():
    model = args.model
    now = datetime.datetime.now()
    full_date = now.strftime("%Y-%m-%d %H:%M:%S")
    
    

    file_name = args.model+'-'+args.mode+'-'+args.prompt+'-'+args.graph_representation
    os.makedirs(args.log_path + f'/content/{args.task}', exist_ok=True)


    if args.model in ['gpt-4o-mini','gpt-4o']:
        client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
   
    batch_ids_dict=find_batch_ids_in_logs(args)
    log_file_path = "./openailog/content/errors.txt"  

    result_dict = {}  
    jsonlpaths=[]
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        for batch_name, batch_id in batch_ids_dict.items():
            retrieve = client.batches.retrieve(batch_id)
            
            if retrieve.status == 'completed':

                result_dict[batch_id] = retrieve.output_file_id 

                content = client.files.content(result_dict[batch_id]) 
                
                jsonlpath = f"./openailog/content/{args.task}/{batch_name}_batchoutput.jsonl"
                content.write_to_file(jsonlpath)
                jsonlpaths.append(jsonlpath)
            
            else:
                error_message = f"Batch Name: {batch_name}, Batch ID: {batch_id}, Status: {retrieve.status}, Retrieve: {retrieve}\n"
                log_file.write(error_message)  
                print(batch_name, batch_id, retrieve.status) 
    
    if len(jsonlpaths) !=0:  
        if args.model in file_name:
            id_answer_dict=extract_data_from_jsonl(jsonlpaths)
            file_path = "./openailog/content/all_id_answer_dict_"+args.model+".json"
            if os.path.exists(file_path):
                with open(file_path, 'r+', encoding='utf-8') as file:
                    all_id_answer_dict = json.load(file)
                    print(len( all_id_answer_dict),'len( all_id_answer_dict)')
                    for key, value in id_answer_dict.items():
                        if key not in all_id_answer_dict.keys():
                             all_id_answer_dict[key] = value
                             
                    file.seek(0)
                    json.dump(all_id_answer_dict, file, ensure_ascii=False, indent=4)
            else:
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(id_answer_dict, file, ensure_ascii=False, indent=4)
                    

def updatefinaljson(args):
    file_path = "./openailog/content/all_id_answer_dict_"+args.model+".json"
    ori_path='../open_jsonfile/load_'+args.task+'.json'
    with open(ori_path, 'r', encoding='utf-8') as file:
        ori_list = json.load(file)  
    with open(file_path, 'r+', encoding='utf-8') as file:
        all_id_answer_dict = json.load(file)
                                
    for item in ori_list:
        name_id = item['name-id']
        if name_id in all_id_answer_dict and args.model not in item['model_response'].keys():
            item['model_response'][args.model]=all_id_answer_dict[name_id]




if __name__ == '__main__':
    
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
