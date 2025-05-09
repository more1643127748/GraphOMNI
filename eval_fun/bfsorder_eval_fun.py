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
def extract_and_check_numbers_bfsorder(content, start):

    pattern = rf"(traversal order starting from node {start}|bfs traversal order would be|bfs traversal starting at node {start}|bfs order from starting node {start}|traversal order for the given graph starting from node {start}|bfs order from {start}|bfs traversal order for the given graph|the order of traversal|bfs starting at node {start}|the result will be|bfs order starting from node {start}|final order is|bfs traversal order of this graph|the order is|traversal order starting at node {start}|traversal order starts at node {start}|anwser is|the result is|bfs traversal is|traversal order from node {start}|traversal order starts from node {start}|traversal order is|bfs order is|traversal order will be|answer is|the resulting order is|bfs traversal order ends here)(.*?)(?=\.|$)"

    
    result = {}  
    


    paragraphs = content.split("\n\n")
    merged_paragraphs = []


    for i in range(len(paragraphs)):

        cleaned_paragraph = re.sub(r'\s+', ' ', paragraphs[i].strip())


        if len(cleaned_paragraph) < 20 and i > 0:

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
                        numbers=re.findall(r'\d+', match[1].strip())
                        numbers=[int(num) for num in numbers]
                        if len(numbers)!=[]:
                            if len(numbers)>=2:
                                if numbers[0]==start and numbers[1]==start:
                                    numbers=numbers[1:]
                            result[(line,match[0].strip())]=numbers

    
    return result


def evaluate_bfsorder(ans,edges,start):
    ans=re.sub(r'([,;.!?])\s+', r'\1', ans)
    ans = re.sub(r'(:\s*)\n', r'\1', ans)
    ans= ans.replace("*", "")
    ans= ans.replace("$", "")
    ans= ans.replace(":", " is")
    ans= ans.replace("  ", " ")

    startstr = str(start)  
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
        ans1=validate_bfs(graph, start, numbers)
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
        ans1=validate_bfs(graph, start, numbers)
        if ans1:
            vote2 = 1  
            if not ans1_found:
                vote1 = 1  
                ans1_found = True  
        return vote1,vote2
    

    paths_dict = extract_and_check_numbers_bfsorder(ans, startstr)
    if paths_dict=={}:
        return None,None

    for key, value in paths_dict.items():
        if value!= None:

            ans1=validate_bfs(graph, start, value)
            if ans1:
                vote2 = 1 
                if not ans1_found:
                    vote1 = 1  
                    ans1_found = True  

    return vote1,vote2

