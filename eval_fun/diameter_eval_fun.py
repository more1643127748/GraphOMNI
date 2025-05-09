import re

def merge_short_paragraphs(text, length_threshold=30):
    paragraphs = re.split(r'\n\s*\n', text.strip())
    
    if not paragraphs:
        return text.strip()  

    merged_paragraphs = [paragraphs[0].strip()]  
    for i in range(1, len(paragraphs)):
        paragraph = paragraphs[i].strip()
        if len(paragraph) <= length_threshold:
            merged_paragraphs[-1] += " " + paragraph
        else:
            merged_paragraphs.append(paragraph)

    first_paragraph = merged_paragraphs[0]
    last_paragraph = merged_paragraphs[-1]

    return first_paragraph + "\n\n" + last_paragraph



def extract_and_check_numbers_dimater(content):
    pattern = rf"(diameter is|the maximum of these shortest paths is|diameter of the given graph|diameter of our graph|diameter of this graph|diameter of the graph|the diameter of the provided graph|diameter of the graph is|answer is|diameter of this graph is|the longest shortest path is|has diameter|anwser is|output)(.*?)(?=\.|$)"
    
    result = {}  

    paragraphs = content.split("\n\n")
    merged_paragraphs = []

    for i in range(len(paragraphs)):
        cleaned_paragraph = re.sub(r'\s+', ' ', paragraphs[i].strip())

        if len(cleaned_paragraph) < 20 and i > 0:
            merged_paragraphs[-1] += "." + cleaned_paragraph
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
                        numbers = re.findall(r'\d+\.\d+|\d+', match[1].strip())  # 找到所有小数和整数

                        numbers=[float(num) for num in numbers]
                        if len(numbers)==1:
                            result[(line,match[0].strip())]=float(numbers[0])
                        elif len(numbers)>1:
                            result[(line,match[0].strip())]=float(numbers[-1])

    
    return result
def eval_diameter_number(text,gt): 
    text=re.sub(r'([,;.!?])\s+', r'\1', text)
    text = re.sub(r'(:\s*)\n', r'\1', text)
    text= text.replace("*", "")
    text= text.replace("$", "")
    text= text.replace(":", " is")
    text= text.replace(".0", "")
    text= text.replace("  ", " ")
    
    vote=None

    if re.match(r'^[\d\W]+$', text):  # \W表示匹配非字母数字字符
        numbers = re.findall(r'\d+\.\d+|\d+', text)  # 找到所有小数和整数
        if numbers!=[]:
            if float(numbers[0])==gt and len(numbers)==1:
                return 1
            else:
                return 0    
    lines = text.splitlines()
    if not lines:
        return None
    
    first_line = lines[0]
    if re.match(r'^[\d\W]+$', first_line):  
        numbers = re.findall(r'\d+\.\d+|\d+', first_line)  
        if numbers!=[]:
            if float(numbers[0])==gt and len(numbers)==1:
                return 1
            else:
                return 0

    paragraphs = re.split(r'\n\s*\n', text.strip())  
    first_paragraph = paragraphs[0].strip()  # 
    if re.match(r'^[\d\W]+$', first_paragraph):  
        # 提取第一行中的所有数字
        numbers = re.findall(r'\d+\.\d+|\d+', first_paragraph)  
        if numbers!=[]:
            if float(numbers[0])==gt and len(numbers)==1:
                return 1
            else:
                return 0
    



    result = merge_short_paragraphs( text.strip())

    diam_dict=extract_and_check_numbers_dimater(result )
    for key, value in  diam_dict.items():
            if value==gt:
                #print(key, value,gt)
                return 1
    if not any(value == gt for value in diam_dict.values()):
            return 0


    diam_dict=extract_and_check_numbers_dimater(text)
    if diam_dict=={}:
        return None
    for key, value in  diam_dict.items():
        if value==gt:
            #print(key, value,gt)
            return 1
    if not any(value == gt for value in diam_dict.values()):
        return 0
