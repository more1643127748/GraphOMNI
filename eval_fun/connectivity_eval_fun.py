import re

def filter_sentences(sentences, truelist, notsurelist):

    filtered_sentences = []
    
    for sentence in sentences:
        should_remove = False  
        
        for prefix in notsurelist:
            for trueli in truelist:
                if prefix+trueli in sentence:
                    should_remove = True
                    break 
        
            if should_remove:
                break  
        
        if not should_remove:
            filtered_sentences.append(sentence)  
    
    return filtered_sentences   

def eval_connectivity(ans, gt):

    vote = 0  # Initialize vote result
    
    # Split text into paragraphs and lines, strip extra spaces or symbols
    paragraphs = [p.strip() for p in ans.split('\n\n') if p.strip()]
    lines = [line.strip().lower().strip('.!?') for line in ans.split('\n') if line.strip()]
    
    if lines:
        first_line = lines[0]
        last_lines = lines[-2:] if len(lines) > 1 else [lines[-1]]
        
        # Check if first line is a direct yes/no or true/false response
        if first_line in {"yes", " no."," no ", "no", "true", "false"}:
            if (first_line in {"yes", "true"} and gt) or (first_line in {" no."," no ", "no", "false"} and not gt):
                return 1
            else:
                return 0
        
        last_text = " ".join(last_lines)
        
        if any(re.search(r'\b' + re.escape(phrase) + r'\b', last_text) for phrase in ["yes", "true", "there is a path", "the answer is yes"]):
            return int(gt)
        if any(re.search(r'\b' + re.escape(phrase) + r'\b', last_text) for phrase in [" no."," no ", "no", "false", "there is no path", "the answer is no"]):
            return int(not gt)
    
    # Check last line of the first paragraph
    if paragraphs:
        first_paragraph_lines = paragraphs[0].split('\n')
        first_paragraph_last_lines = first_paragraph_lines[-2:] if len(first_paragraph_lines) > 1 else [first_paragraph_lines[-1]]
        first_paragraph_last_text = " ".join(first_paragraph_last_lines).strip().lower()
        if any(phrase in first_paragraph_last_text for phrase in ["yes", "true", "there is a path", "the answer is yes"]) and gt:
            return 1
        if any(phrase in first_paragraph_last_text for phrase in [" no."," no ", "no", "false", "there is no path", "the answer is no"]) and not gt:
            return 1
    output_match = re.search(r'#.*?output[:\s]+(true|false)', ans, re.IGNORECASE)
    if output_match:
        output_value = output_match.group(1).lower() 
        if (output_value in { "true"} and gt) or (output_value in {"false"} and not gt):
                return 1
        else:
                return 0

    # Locate the position of negative indicators in the answer
    no_index = next((match.start() for match in re.finditer(r'\bno\b', ans) if 'path' in ans[max(0, match.start()-50):match.start()+50]), -1)
    # List of positions for various negative phrases
    negative_positions = [
        no_index,
        ans.find("false") if 'path' in ans[max(0, ans.find("false")-50):ans.find("false")+50] else -1,
        ans.find("there is no path"),
        ans.find("the answer is no"),
    ]
    # Find the earliest negative indicator position
    earliest_negative = min((pos for pos in negative_positions if pos != -1), default=float('inf'))
    
    # List of positions for various positive phrases
    positive_positions = [
        ans.find("yes") if 'path' in ans[max(0, ans.find("yes")-50):ans.find("yes")+50] else -1,
        ans.find("true") if 'path' in ans[max(0, ans.find("true")-50):ans.find("true")+50] else -1,
        ans.find("there is a path") if 'if there is a path' in ans[max(0, ans.find("there is a path")-50):ans.find("true")+50] else -1,
        ans.find("the answer is yes"),
    ]
    # Find the earliest positive indicator position
    earliest_positive = min((pos for pos in positive_positions if pos != -1), default=float('inf'))
    
    # Compare positions of positive and negative phrases based on ground truth
    if (gt is True and earliest_positive < earliest_negative) or (gt is False and earliest_negative < earliest_positive):
        vote = 1  # Correct evaluation
    
    return vote


import re

def extract_relevant_sentences(ans):
    """
    Extract relevant sentences from the answer text based on predefined keywords.
    Args:
        ans (str): Answer text containing statements about connectivity.
    Returns:
        list: List of sentences that contain relevant connectivity indicators.
    """
    lines = [line.strip().lower().strip('.!?') for line in ans.split('\n') if line.strip()]
    relevant_sentences = []
    first_paragraph = ans.split('\n\n')[0] if '\n\n' in ans else ans  # Extract first paragraph
    first_paragraph_sentences = [line.strip().lower().strip('.!?') for line in first_paragraph.split('\n') if line.strip()]
    
    keywords = [
        "yes", " no."," no ", "no", "true", "false", "there is a path", "the path", 
        "answer is", "exist", "not exist", "no path", "a path"]
    
    for i, line in enumerate(lines):
        if any(re.search(r'\b' + re.escape(phrase) + r'\b', line) for phrase in keywords):
            # Ensure 'path' appears in the current, previous, or next line
            relevant_sentences.append(line)
    
    # Check for output statement
    output_match = re.search(r'#.*?output[:\s]+(true|false)', ans, re.IGNORECASE)
    if output_match:
        relevant_sentences.insert(0, f"output: {output_match.group(1).lower()}")
    
    return relevant_sentences, first_paragraph_sentences


def eval_connectivity(ans, gt):
    """
    Evaluate connectivity based on extracted sentences and ground truth.
    Args:
        relevant_sentences (list): List of sentences containing relevant indicators.
        first_paragraph_sentences (list): Sentences from the first paragraph for priority judgment.
        gt (bool): Ground truth, where True means connected and False means not connected.
    Returns:
        int: Returns 1 if the evaluation matches the ground truth, otherwise 0.
    """
    relevant_sentences, first_paragraph_sentences=extract_relevant_sentences(ans)
    if not relevant_sentences:
        return None
    
    
    if re.sub(r'[^a-zA-Z0-9]', '', ans) in ["yes", "true","yes.", "true."]:
        return int(gt)    
    if re.sub(r'[^a-zA-Z0-9]', '', ans) in ["no", "false","no.", "false."]:
        return int(gt)

    # Prioritize output statement
    if "output: true" in relevant_sentences:
        return int(gt)
    if "output: false" in relevant_sentences:
        return int(not gt)
    
    truelist=["yes", "true", "there is a path", "answer is yes", "path is exist",'final answer is: $\boxed{1}$']
    falselist=[" no."," no ", "false", "there is no path", "answer is no",'there is no direct path','final answer is: $\boxed{0}$']

    notsurelist=["if ", "whether ","if the ", "whether the"]
    

    first_paragraph_sentences=filter_sentences( first_paragraph_sentences, truelist, notsurelist)



    relevant_sentences =   filter_sentences( relevant_sentences, truelist, notsurelist)

    # Prioritize first paragraph sentences
    first_text = " ".join(first_paragraph_sentences)
    if any(phrase in first_text for phrase in truelist):
        return int(gt)
    if any(phrase in first_text for phrase in falselist):
        return int(not gt)
    
    # Fallback to all relevant sentences
    last_text = " ".join(relevant_sentences)
    if any(phrase in last_text for phrase in truelist):
        return int(gt)
    if any(phrase in last_text for phrase in falselist):
        return int(not gt)
    
    return None

