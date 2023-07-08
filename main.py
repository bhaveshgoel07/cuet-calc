import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from flask import Flask, jsonify
import urllib.parse


df = pd.read_excel("anskey.xlsx")
ans_key = df.set_index('Question ID')['Correct Option ID'].to_dict()

app = Flask(__name__)

@app.route("/parse_html/<path:url>")
def parse_html(url):
    page = requests.get(url)
    page_content = BeautifulSoup(page.content, "lxml")
    questions = page_content.find_all('table',class_="questionPnlTbl")
    sections = page_content.find_all('div',class_="section-lbl")
    main_info = page_content.find_all('div',class_="main-info-pnl")
    user_info = {}
    try:
        user_info["Application Number"] = re.search(r"Application No (\w+)", main_info[0].text).group(1)
    except:
        user_info["Application Number"] = " "
    try:
        user_info["Candidate Name"] = re.search(r"(?<=Candidate Name )\w+ \w+", main_info[0].text).group()
    except:
        user_info["Candidate Name"] = re.search(r"(?<=Candidate Name )\w+", main_info[0].text).group()
    user_info["Roll No"] = re.search(r"Roll No (\w+)", main_info[0].text).group(1)

    date_pattern = r"\d{2}/\d{2}/\d{4}" 
    dates = re.findall(date_pattern, main_info[0].text)

    user_info["Test Date"] = dates[0]
    time_range_pattern = r"\d{1,2}:\d{2} [APM]{2} - \d{1,2}:\d{2} [APM]{2}"  # Regular expression pattern to match time range in the format "H:MM AM/PM - H:MM AM/PM"
    time_range = re.search(time_range_pattern, main_info[0].text)
    user_info["Test Time"] = time_range[0]
    
    score = 0
    answers = ""
    output = {}
    output["Total Sections"] = len(sections)
    correct = 0
    incorrect = 0
    unanswered = 0
    count = 0
    section_number = 0
    for question in questions:
        question_number = re.findall(r'Q.\d+', question.text)[0]
        if question_number == "Q.1":
            output["Section"+str(section_number+1)+" Name"] =  sections[section_number].text.replace('\u00a0', '').replace('Section :', '')+" "
            if section_number != 0:
                
                output["Section"+str(int(section_number))+" Score"] = score
                output["Section"+str(int(section_number))+" Answers"] = answers
                output["Section"+str(int(section_number))+" Correct Answers"] = correct
                output["Section"+str(int(section_number))+" Incorrect Answers"] = incorrect
                output["Section"+str(int(section_number))+" Unanswered Answers"] = unanswered
                output["Section"+str(int(section_number))+" Total Questions"] = count
                count = 0
                correct = 0
                incorrect = 0
                unanswered = 0
                answers = ""
                score = 0
            section_number += 1
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
            answers += question_number + "-Unanswered   "
            unanswered +=1
            
            continue
        try:
            correct_ans_id = str(ans_key[int(question_id)])
        except:
            continue
        pattern = r'Option '+chosen_option+' ID :(\d+)'
        match = re.search(pattern, question.text)
        chosen_option_id = match.group(1)
        if correct_ans_id == str(0):
            score+=5
            answers += question_number + "-Correct   "
            correct += 1
            continue
        if chosen_option_id == correct_ans_id:
            answers += question_number + "-Correct   "
            correct += 1
            score += 5
        else:
            answers += question_number + "-Incorrect   "
            incorrect += 1
            score -= 1
    output["Section"+str(int(section_number))+" Score"] = score
    output["Section"+str(int(section_number))+" Answers"] = answers
    output["Section"+str(int(section_number))+" Correct Answers"] = correct
    output["Section"+str(int(section_number))+" Incorrect Answers"] = incorrect
    output["Section"+str(int(section_number))+" Unanswered Answers"] = unanswered
    output["Section"+str(int(section_number))+" Total Questions"] = count
    
    # Custom function to replace spaces with "%20" using urllib.parse.quote()
    def replace_spaces(text):
        return urllib.parse.quote(text, safe='')

    # ... existing code ...

    # Generate the output URL by combining the base URL and encoded parameters
    base_url = "https://aceipm.com/scorecard2/"

    # Create a dictionary for storing the URL parameters
    url_params = {
        "candidatename": replace_spaces(user_info["Candidate Name"]),
        "appno": user_info["Application Number"],
        "rollno": user_info["Roll No"],
        "testdate": user_info["Test Date"],
        "testtime": user_info["Test Time"]

    }

    # Iterate over the sections to extract relevant information
    for section_num in range(1, len(sections) + 1):
        section_name = output.get("Section{} Name".format(section_num), "")
        section_score = output.get("Section{} Score".format(section_num), "")
        section_answers = output.get("Section{} Answers".format(section_num), "")
        section_correct = output.get("Section{} Correct Answers".format(section_num), "")
        section_incorrect = output.get("Section{} Incorrect Answers".format(section_num), "")
        section_unanswered = output.get("Section{} Unanswered Answers".format(section_num), "")
        section_total_questions = output.get("Section{} Total Questions".format(section_num), "")

        # Add the section information to the URL parameters
        url_params["subject{}".format(section_num)] = replace_spaces(section_name)
        url_params["totalq{}".format(section_num)] = section_total_questions
        url_params["correct{}".format(section_num)] = section_correct
        url_params["incorrect{}".format(section_num)] = section_incorrect
        url_params["unanswered{}".format(section_num)] = section_unanswered
        url_params["totalscore{}".format(section_num)] = section_score
        url_params["descriptive{}".format(section_num)] = replace_spaces(section_answers)

    # Generate the output URL by combining the base URL and encoded parameters
    output_url = base_url + "?" + urllib.parse.urlencode(url_params)
    output_url = output_url.replace("%2520", "%20")
    
    data1 = jsonify(user_info, output)
    data_df = pd.DataFrame(data1)
    data_df.to_csv("data.csv")
    

    # output_url = "https://aceipm.com/scorecard"+output["Total Sections"]+"/?candidatename="+user_info['Candidate Name']+"&appno="+user_info["Application Number"]+"&rollno="+user_info["Roll No"] +"&testdate="+user_info["Test Date"]+"&testtime="+user_info["Test Time"]+"&subject"
    return data, 200 
if __name__ == "__main__":
    app.run(host='0.0.0.0')