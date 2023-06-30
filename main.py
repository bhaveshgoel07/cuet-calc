import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from flask import Flask, jsonify

df = pd.read_excel("anskey.xlsx")
ans_key = df.set_index('Question ID')['Correct Option ID'].to_dict()

app = Flask(__name__)

@app.route("/parse_html/<path:url>")
def parse_html(url):
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
    answers["score"] = score

    return jsonify(answers), 200 
if __name__ == "__main__":
    app.run(host='0.0.0.0')