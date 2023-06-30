from bs4 import BeautifulSoup
import requests
import re

url = "https://cdn3.digialm.com//per/g28/pub/2083/touchstone/AssessmentQPHTMLMode1//2083O23161/2083O23161S30D10898/16866461286355551/HR04223891_2083O23161S30D10898E3.html"
page = requests.get(url)
page_content = BeautifulSoup(page.content, "lxml")
# sections = page_content.find_all('div',class_="section-lbl")
# print(sections[0].text)

# questions = page_content.find_all('table',class_="questionPnlTbl")
# question_number = re.findall(r'Q.\d+', questions[88].text)[0]
# print(question_number)

main_info = page_content.find_all('div',class_="main-info-pnl")
user_info = {}
user_info["Application Number"] = re.search(r"Application No (\w+)", main_info[0].text).group(1)
user_info["Candidate Name"] = re.search(r"(?<=Candidate Name )\w+ \w+", main_info[0].text).group()
user_info["Roll No"] = re.search(r"Roll No (\w+)", main_info[0].text).group(1)

date_pattern = r"\d{2}/\d{2}/\d{4}" 
dates = re.findall(date_pattern, main_info[0].text)

user_info["Test Date"] = dates[0]
time_range_pattern = r"\d{1,2}:\d{2} [APM]{2} - \d{1,2}:\d{2} [APM]{2}"  # Regular expression pattern to match time range in the format "H:MM AM/PM - H:MM AM/PM"
time_range = re.search(time_range_pattern, main_info[0].text)
user_info["Test Time"] = time_range[0]
print(user_info)
