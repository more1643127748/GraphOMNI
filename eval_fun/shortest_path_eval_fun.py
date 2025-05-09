import re
from .verification import *


def extract_numbers_before_node(input_str):

    match = re.search(r'(.*?) node', input_str)
    if match:

        before_node = match.group(1)

        numbers = re.findall(r'\d+', before_node)
        return [int(num) for num in numbers]
    else:
        numbers=re.findall(r'\d+', input_str)
        numbers=[int(num) for num in numbers]
        return numbers
def extract_and_check_numbers_path(content, start,end):

    pattern = rf"(path between node {start} and node {end}|and the path is|path from node {start} to node {end}|shortest path is|answer is)(.*?)(?=\.|$)"
    

    
    result = {}  


    paragraphs = content.split("\n\n")
    merged_paragraphs = []


    for i in range(len(paragraphs)):

        cleaned_paragraph = re.sub(r'\s+', ' ', paragraphs[i].strip())


        if len(cleaned_paragraph) < 6 and i > 0:

            merged_paragraphs[-1] += " " + cleaned_paragraph
        else:

            merged_paragraphs.append(cleaned_paragraph)


    merged_content = "\n\n".join(merged_paragraphs)
    
    paragraphs = merged_content.split("\n\n")

    for paragraph in paragraphs:

        paragraph.replace("\n", "")

        lines = paragraph.split(".")
        for line in lines:

            line=line

            match = re.search(pattern, line)

            if match:
                matches = re.findall(pattern, line)
                for match in matches:

                    if re.search(r'\d', match[1].strip()):  
                        numbers=re.findall(r'\d+', match[1].strip())
                        numbers=[int(num) for num in numbers]
                        if len(numbers)>=2:
                            if numbers[0]==start and numbers[1]==end and len(numbers)>=4:
                                numbers=numbers[2:]

                            result[(line,match[0].strip())]=numbers


    
    return result



def evaluate_shortest_path(ans,edges,start, end,gt):
    ans=re.sub(r'([,;.!?])\s+', r'\1', ans)
    ans = re.sub(r'(:\s*)\n', r'\1', ans)
    ans= ans.replace("*", "")
    ans= ans.replace("$", "")
    ans= ans.replace(":", " is")
    ans= ans.replace("  ", " ")
    ans= ans.replace("`[", "")
    ans= ans.replace("$\boxed{", "")

    graph=build_graph(edges) 
    ans1_found = False

    lines = ans.splitlines()
    if not lines:
        return None,None
    

    first_line = lines[0]
    vote1,vote2=0,0


    if re.match(r'^[\d\W]+$', first_line):  

        numbers = re.findall(r'\d+', first_line)
        numbers=[int(num) for num in numbers]
        ans1=validate_shortest_path(graph, start, end,  numbers)
        if ans1:
            vote2 = 1   
            if not ans1_found:
                vote1 = 1   
                ans1_found = True   
        return vote1,vote2

    paragraphs = re.split(r'\n\s*\n', ans.strip())  
    first_paragraph = paragraphs[0].strip()   

    if re.match(r'^[\d\W]+$', first_paragraph):   
        numbers = re.findall(r'\d+', first_paragraph)
        numbers=[int(num) for num in numbers]
        ans1=validate_shortest_path(graph, start, end,  numbers)
        if ans1:
            vote2 = 1   
            if not ans1_found:
                vote1 = 1   
                ans1_found = True  
        return vote1,vote2
    if len(gt) == 2:
        for line in lines:

            parts = line.split(".")  
            
            for part in parts:
                if f"path between node {start} and node {end}." in part or f"path from node {start} to node {end} is" in part:
                    if any(keyword in part for keyword in ["one edge", "single edge", "1 edge"]):
                        return 1, 1

    paths_dict =  extract_and_check_numbers_path(ans, start,end)
               
               
    if paths_dict=={}:
        return None,None


    vote1,vote2=0,0
    for key, value in paths_dict.items():
        if value!= None:

            ans1=validate_shortest_path(graph, start, end, value)
            if ans1:
                vote2 = 1  
                
                if not ans1_found:
                    vote1 = 1  
                    
                    ans1_found = True  

    return vote1,vote2



