import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from flask import Flask, jsonify

df = pd.read_excel("anskey.xlsx")
ans_key = df.set_index('Question ID')['Correct Option ID'].to_dict()


url = "https://cdn3.digialm.com//per/g28/pub/2083/touchstone/AssessmentQPHTMLMode1//2083O23103/2083O23103S4D18993/16855509770969224/UP32566223_2083O23103S4D18993E1.html"
page = requests.get(url)
page_content = BeautifulSoup(page.content, "lxml")
questions = page_content.find_all('table',class_="questionPnlTbl")
score = 0
answers = {}
count = 0
for question in questions:
    pattern = r'Question ID :(\d+)'
    match = re.search(pattern, question.text)
    question_id = match.group(1)
    
    
    pattern = r'Chosen Option :(\d+)'
    match = re.search(pattern, question.text)
    #add iff condition to skip not answered questions
    
    
    try:
        chosen_option = match.group(1)
        count += 1
    except:
        count += 1
        answers["q"+str(count)] = "not answered"
        
        continue

    correct_ans_id = str(ans_key[int(question_id)])

    pattern = r'Option '+chosen_option+' ID :(\d+)'
    match = re.search(pattern, question.text)
    chosen_option_id = match.group(1)
    if chosen_option_id == correct_ans_id:
        answers["q"+str(count)] = "correct"
        score += 5
    else:
        answers["q"+str(count)] = "incorrect"
        score -= 1

print(answers)