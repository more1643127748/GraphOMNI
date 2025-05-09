from openai import OpenAI
import openai
import os
import json
import random
import datetime
import argparse
import logging
from tqdm import tqdm
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

args = parser.parse_args()


def loadqery(args):
    all_id_answer_path = args.log_path+"/content/all_id_answer_dict_" + args.model + ".json"

    if os.path.exists(all_id_answer_path):
        with open(all_id_answer_path, 'r', encoding='utf-8') as file:
            all_id_answer_dict = json.load(file)
    else:
        all_id_answer_dict = {}

    print(len(all_id_answer_dict),'len(all_id_answer_dict)')

    path=args.base_dir+'load_'+args.task+'.json'
    with open(path, 'r', encoding='utf-8') as file:
        data_list = json.load(file)  

    filtered_data_dict = {}

    if isinstance(data_list, list):
        for idx, data_dict in enumerate(data_list, start=1):
            if  data_dict['prompt_type'] == args.prompt and data_dict['serialization_type'] == args.graph_representation and data_dict['difficulty'] == args.mode:
                name_id = data_dict.get("name-id")
                query = data_dict.get("query")
            
                if name_id not in all_id_answer_dict and name_id and query:
                    filtered_data_dict[name_id] = query


    else:
        print("JSON 文件内容不是一个列表。")

    return  filtered_data_dict

    


def convert_prompts_to_jsonl(prompts_dict, output_file_path, model="gpt-4o-mini", sys_msg="You are a helpful assistant.", max_completion_tokens = 1000):
    with open(output_file_path, 'w') as outfile:
        for name, prompt in prompts_dict.items():
            data = {
                "custom_id": name,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": sys_msg},
                        {"role": "user", "content": prompt}
                    ],
                    "max_completion_tokens": max_completion_tokens,
                }
            }
            json.dump(data, outfile)
            outfile.write('\n')


def main():
    model = args.model
    if args.model in ['gpt-4o-mini','gpt-4o']:
        client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
   
    now = datetime.datetime.now()
    full_date = now.strftime("%Y-%m-%d %H:%M:%S")
    
    name = args.task+'-'+args.model+'-'+args.mode+'-'+args.prompt+'-'+args.graph_representation

    file_name = name + "-" + full_date
    log_path=args.log_path+'/log'
    os.makedirs(os.path.join(log_path, args.task ) , exist_ok=True)
    log_path = os.path.join(log_path, args.task+'/'+file_name + ".log")


    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),  
            logging.StreamHandler()  
        ]
    )


    logger = logging.getLogger(__name__)
    

    if  args.task == 'cycle':
        sys_msg = "You are an expert on graph inferencing. Answer the question and provide the answer in the form of 'yes' or 'no' at the end of your response. For example: 'No, there is no cycle in this graph' or 'Yes, there is a cycle in this graph'."
    elif  args.task == 'shortest_path':
        sys_msg = "You are an expert on graph inferencing. Answer the question and provide the answer in the form of 'the shortest path is' at the end of your response.For example: 'The shortest path from node 2 to node 6 is 2,5,4,6.'"
    elif  args.task == 'connectivity':
        sys_msg = "You are an expert on graph inferencing. Answer the question and provide the answer in the form of 'yes' or 'no' at the end of your response.For example: 'The answer is no.' or 'The answer is yes'."
    elif  args.task == 'bfsorder':
        sys_msg = "You are an expert on graph inferencing. Answer the question and provide the answer in the form of 'the BFS traversal order is' at the end of your response.For example: The bfs traversal order starting from node 5 is 5,0,1,2,3,4,7,6."
    elif  args.task == 'triangle':
        sys_msg = "You are an expert on graph inferencing. Answer the question and provide the answer in the form of 'the number of triangles is' at the end of your response.For example: The number of triangles is 2."
    elif  args.task == 'diameter':
        sys_msg = "You are an expert on graph inferencing. Answer the question and provide the answer in the form of 'the diameter is' at the end of your response.For example: The diameter is 3.0."   # 这里是我设置了一些路径




    os.makedirs(args.log_path + f'/batch/{args.task}', exist_ok=True)

    batch_prompts_output_path = args.log_path + f'/batch/{args.task}/{file_name}.jsonl'
    batch_useded_files_path = args.log_path + f'/batch/{args.task}/{file_name}.json'


    prompts_dict = loadqery(args)
    if  prompts_dict == {}:
        print(args,'already done or not ori')
        return
    
    with open(batch_useded_files_path, 'w') as outfile:
        json.dump(prompts_dict, outfile)

    convert_prompts_to_jsonl(prompts_dict, batch_prompts_output_path, sys_msg=sys_msg, model=model, max_completion_tokens=args.max_completion_tokens)


    batch_input_file = client.files.create(
        file=open(batch_prompts_output_path, "rb"),
        purpose="batch"
    )

    batch_input_file_id = batch_input_file.id

    batch_obj = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
     
    )


    config = {"file_name": file_name,
              "max_completion_tokens":args.max_completion_tokens,
              "log_path": log_path,
              "sys_msg": sys_msg,
              "batch_prompts_output_path" : batch_prompts_output_path,
              "batch_useded_files_path" : batch_useded_files_path,
              "model" : model,
              "batch_input_file_id" : batch_input_file_id,
              "batch_id" : batch_obj.id,
    }

    logger.info("Finishing the application with configuration: %s", config)
    logger.info("Application started successfully.")

    

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

    