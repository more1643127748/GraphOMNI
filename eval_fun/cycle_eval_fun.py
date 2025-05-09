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

def eval_cycle(ans, gt):

    """
    Evaluate the presence of a cycle in the answer text compared to the ground truth.
    Args:
        ans (str): Answer text containing statements about cycles.
        gt (bool): Ground truth indicating whether a cycle exists (True for cycle, False otherwise).
    Returns:
        int: Returns 1 if the evaluation matches the ground truth, otherwise 0.
    """
    gt = eval(gt.capitalize())  

    vote = 0  
    no_index = next((match.start() for match in re.finditer(r'\bno\b', ans)), -1)
    negative_positions = [
        no_index,
        ans.find("false"),
        ans.find("there is no cycle"),
    ]
    earliest_negative = min((pos for pos in negative_positions if pos != -1), default=float('inf'))
    positive_positions = [
        ans.find("yes"),
        ans.find("true"),
        ans.find("there is a cycle"),
    ]
    # Find the earliest position of a positive indicator
    earliest_positive = min((pos for pos in positive_positions if pos != -1), default=float('inf'))
    # Compare positions of positive and negative phrases based on ground truth
    if (gt is True and earliest_positive < earliest_negative) or (gt is False and earliest_negative < earliest_positive):
        vote = 1  # Correct evaluation
    return vote


def extract_relevant_sentences(ans):
    """
    Extract relevant sentences from the answer text based on predefined keywords.
    Args:
        ans (str): Answer text containing statements about cycle.
    Returns:
        list: List of sentences that contain relevant cycle indicators.
    """
    lines = [line.strip().lower().strip('.!?') for line in ans.split('\n') if line.strip()]
    relevant_sentences = []
    first_paragraph = ans.split('\n\n')[0] if '\n\n' in ans else ans  # Extract first paragraph
    first_paragraph_sentences = [line.strip().lower().strip('.!?') for line in first_paragraph.split('\n') if line.strip()]
    
    keywords = [
        "yes", " no."," no ", "no", "true", "false", "there is a cycle", "there is no cycle", 
        "answer is", "exist", "not exist", "no cycle","multiple cycle", "a cycle","cycles","contain any cycle","contain cycle","cycle can be detected"]
    
    for i, line in enumerate(lines):
        if any(re.search(r'\b' + re.escape(phrase) + r'\b', line) for phrase in keywords):
            relevant_sentences.append(line)
    
    # Check for output statement
    output_match = re.search(r'#.*?output[:\s]+(true|false)', ans, re.IGNORECASE)
    if output_match:
        relevant_sentences.insert(0, f"output: {output_match.group(1).lower()}")
    
    return relevant_sentences, first_paragraph_sentences


def eval_cycle(ans, gt):
    """
    Evaluate cycle based on extracted sentences and ground truth.
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
    
    truelist=["yes", "true", "there is a cycle", "answer is yes", "cycle is exist",'final answer is: $\boxed{1}$',
              'found a cycle','graph contains a cycle', "contains multiple cycles",'has a cycle', 
              'have a cycle','graph contains cycles','cycle can be detected through following path','there are multiple cycles',
              'indicates a cycle in the graph','indicating the presence of a cycle','a cycle exists in this',
              'cycles are detected through paths','has multiple cycles','contains a single cycle','contains multiple cycles'
              'indicate the presence of multiple cycle','indicate the presence of multiple cycles','multiple cycles are present',
              'following cycles are detected','contains two disjoint cycles','indicating a cycle in the graph','multiple cycles are detected']
    falselist=[" no."," no ", "false", "there is no cycle", "not contain any cycles","answer is no",'final answer is: $\boxed{0}$']

    notsurelist=["if ", "whether ","if the ", "whether the"]

   
    first_paragraph_sentences=filter_sentences( first_paragraph_sentences, truelist, notsurelist)
    
    

    relevant_sentences=filter_sentences( relevant_sentences, truelist, notsurelist)


    first_text = " ".join(first_paragraph_sentences)
    if any(phrase in first_text for phrase in truelist):
        return int(gt)
    if any(phrase in first_text for phrase in falselist):
        return int(not gt)
    
    last_text = " ".join(relevant_sentences)
    if any(phrase in last_text for phrase in truelist):
        return int(gt)
    if any(phrase in last_text for phrase in falselist):
        return int(not gt)
    
    return None

