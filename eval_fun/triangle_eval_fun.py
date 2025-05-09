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


# Mapping English words to their corresponding numbers.
english_to_number = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30
}

def convert_english_numbers(text):
    """
    Converts English number words in a text to their numeric equivalents.

    Args:
        text (str): Input text containing English number words.

    Returns:
        str: Text with English number words replaced by their numeric equivalents.
    """
    words = text.split()
    for i, word in enumerate(words):
        cleaned_word = re.sub(r'[^a-zA-Z]', '', word).lower()
        if cleaned_word in english_to_number:
            words[i] = str(english_to_number[cleaned_word])
    return ' '.join(words)

def extract_and_check_numbers_triangle(content):
    pattern1 = r"(number of triangles|number of triangle|total number of triangles|the number of triangles in the graph is|output of the above code is|the output is|answer is|output will be|answer is|total is|output will be|output is|a is|output of the function is)(.*?)(?=\.|$)"
    pattern2 = r"^(.*?)triangles?" 

    
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
            line=convert_english_numbers(line)
            match = re.search(pattern1, line)
            if match:
                matches = re.findall(pattern1, line)
                for match in matches:


                        formerresult=re.split(r'[,.:;!?(){}\[\]]', match[1].strip())[0]
                        numbers = re.findall(r'\d+\.\d+|\d+', formerresult)  

                        numbers=[int(num) for num in numbers]
                        if numbers!=[]:
                            if 'node' not in  formerresult  and 'form' not in  formerresult:
                                if len(numbers)>1:
                                    result[(line,match[0].strip())]=int(numbers[-1])                                 
                                elif len(numbers)==1:
                                    result[(line,match)]=int(float(numbers[0]))          
            match = re.search(pattern2, line)
            if match:
                matches = re.findall(pattern2, line)
                for match in matches:
                        latterresult=re.split(r'[,.:;!?(){}\[\]]', match)[-1]
                        numbers = re.findall(r'\d+\.\d+|\d+',  latterresult)  


                        numbers=[int(num) for num in numbers ]
                        if numbers!=[]:
                            if 'node' not in latterresult and 'form' not in latterresult:
                                if len(numbers)>1:
                                    result[(line,match)]=int(numbers[-1])
                                elif len(numbers)==1:
                                    result[(line,match)]=int(float(numbers[0]))
    
    return result
def eval_triangle_number(text,gt):
        

    phrases = [
    "no triangles in the given graph",
    "no triangles are found",
    "this graph contains no triangles",
    " this means there are no triangles",
    "there are no triangles"
    ]

    if any(phrase in text for phrase in phrases):
        return 0

    
    if re.match(r'^[\d\W]+$', text): 
        numbers = re.findall(r'\d+\.\d+|\d+', text)  
        if numbers!=[]:
            if int(float(numbers[0]))==gt and len(numbers)==1:
                return 1
            else:
                return 0
    lines = text.splitlines()
    if not lines:
        return None
    
    # 获取第一行
    first_line = lines[0]
    if re.match(r'^[\d\W]+$', first_line):  

        numbers = re.findall(r'\d+\.\d+|\d+', first_line)  
        if numbers!=[]:
            if int(float(numbers[0]))==gt and len(numbers)==1:
                return 1
            else:
                return 0
        
    paragraphs = re.split(r'\n\s*\n', text.strip())  
    first_paragraph = paragraphs[0].strip()  # 

    if re.match(r'^[\d\W]+$', first_paragraph):  
        numbers = re.findall(r'\d+\.\d+|\d+', first_paragraph)  
        if numbers!=[]:
            if int(float(numbers[0]))==gt and len(numbers)==1:
                return 1
            else:
                return 0
            
    text=re.sub(r'([,;.!?])\s+', r'\1', text)
    text = re.sub(r'(:\s*)\n', r'\1', text)
    text= text.replace("*", "")
    text= text.replace("$", "")
    text= text.replace(":", " is")
    text= text.replace(",", ", ")
    text= text.replace("`", "")
    text= text.replace("  ", " ")
    text= text.replace("$\boxed{", "")
    text= text.replace("\( \boxed{", "")


    result = merge_short_paragraphs( text.strip())
    diam_dict=extract_and_check_numbers_triangle(result )
    for key, value in  diam_dict.items():
            if value==gt:
                return 1
    if not any(value == gt for value in diam_dict.values()):
            return 0

    triangle_dict=extract_and_check_numbers_triangle(text)
    if triangle_dict=={}:
        return None
    for key, value in  triangle_dict.items():
        if value==gt:
            return 1
    if not any(value == gt for value in triangle_dict.values()):
        return 0
