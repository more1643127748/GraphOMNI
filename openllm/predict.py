from datetime import datetime, timedelta, timezone
import numpy as np
import os
import transformers
import torch
from transformers import LlamaTokenizer, LlamaForCausalLM
from vllm import LLM
from openai import OpenAI
import openai
import os
import json
import random
import datetime
import argparse
import logging
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from vllm import LLM, SamplingParams

from dotenv import load_dotenv
load_dotenv()


MODEL_DIR = "../meta_llama"

def check_and_download_model(model_name):
    model_path = os.path.join(MODEL_DIR, model_name.replace('/', '_'))
    if not os.path.exists(model_path):
        print(f"Model {model_name} not found locally. Downloading...")
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model.save_pretrained(model_path)
        tokenizer.save_pretrained(model_path)
    else:
        print(f"Model {model_name} found locally.")
    return model_path


def loadllm(args):


    model_name = args.model
    max_seq_len = 8192
   
    gpu_memory = 0.9

    if model_name == "Llama3.1":
        print(f"Loading Llama model: {model_name}")
        model_path="meta-llama/Llama-3.1-8B-Instruct"
    
   
        llm = LLM(
            model=model_path,
            max_seq_len_to_capture=max_seq_len,
            task="generate",enforce_eager=True,
            tensor_parallel_size=torch.cuda.device_count()
        )

        if gpu_memory:
            llm.gpu_memory_utilization = 1.0
            print(f"GPU memory utilization set to {llm.gpu_memory_utilization}")

        print(f"Model {model_name} loaded successfully with max_seq_len {max_seq_len}.")
        return llm

    elif model_name == "Mistral":
        print(f"Loading Mistral model: {model_name}")        
        model_path="mistralai/Mistral-7B-Instruct-v0.3"

    elif model_name == "Phi-4":
        print(f"Loading Phi model: {model_name}")        
        model_path="microsoft/phi-4"

    elif model_name == "Qwen2.5":
        print(f"Loading Qwen model: {model_name}")        
        model_path="Qwen/Qwen2.5-7B-Instruct"    

    
    model_path = check_and_download_model(model_path )


    llm = LLM(
        model=model_path,
        max_seq_len_to_capture=max_seq_len,
        task="generate",enforce_eager=True,
    )

    if gpu_memory:
        llm.gpu_memory_utilization = gpu_memory
        print(f"GPU memory utilization set to {gpu_memory}")
    print(f"Model {model_name} loaded successfully with max_seq_len {max_seq_len}.")
    return llm



def predict(llmgenerator,Q,args):
    
    input = Q
    temperature = 0.7

    if args.model in ["Llama3.1", "Mistral", "Phi-4", "Qwen2.5",  'Llama-3.1-8B-Instruct_16384_double']:
        sampling_params = SamplingParams(temperature=temperature, top_p=0.9, max_tokens=2000)  
        outputs = llmgenerator.generate(input,sampling_params)      
        Answer_list = []
        for output in outputs:
            
            Answer_list.append(output.outputs[0].text)
        return Answer_list    

        
    elif args.model in ['llama3']:

        results =llmgenerator.text_completion(
        input,
        max_gen_len=2000,
        temperature=temperature,
        top_p=0.9,)
        Answer_list = []
        for result in  results:
          
            Answer_list.append(result['generation'])
        return Answer_list



def loadqwen38():

    model_name = "Qwen/Qwen3-8B"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    llm = LLM(
        model=model_name,
        max_seq_len_to_capture=16384,
        task="generate",
        enforce_eager=True,
        tensor_parallel_size=torch.cuda.device_count(),
        gpu_memory_utilization=0.95
    )

    return tokenizer, llm

def Qwen38B_chat(tokenizer,model,prompt):
    messages = []
    messages.append({"role": "user", "content": prompt})

    params = SamplingParams(
        max_tokens=16384,
    )

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True
    )

    gens = model.generate(text, sampling_params=params)

    gen = gens[0]

    full_text = gen.outputs[0].text

    tag = "</think>"
    if tag in full_text:
        thinking_content, content = full_text.split(tag, 1)
        thinking_content = thinking_content.strip()
        thinking_content += "</think>"
        content = content.strip()
    else:
        thinking_content = ""
        content = full_text.strip()

    return thinking_content, content