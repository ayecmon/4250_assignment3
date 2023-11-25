from bs4 import BeautifulSoup
from pymongo import MongoClient

#Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['crawler']
pages = db.pages
professors_info = db.professors

#parse faculty info
def parse_permanent_faculty(html):
    soup = BeautifulSoup(html, 'html.parser')

    faculty_divs = soup.find_all('div', class_ = 'clearfix')
    professors = []

    for faculty_div in faculty_divs:
        faculty_info = {}

        #Extracting Faculty Name
        faculty_name = faculty_div.find('h2')
        if faculty_name:
            faculty_info['name'] = faculty_name.text.strip()

            #Extracting information
            info_tags = faculty_div.find_all('strong')

            for tag in info_tags:
                key = tag.text.strip().rstrip(':')
                value_tag = tag.find_next_sibling(text = True)

                if value_tag:
                    value = value_tag.strip()

                    #Extracting Phone Number
                    if key == 'Phone' and not value:
                        continue

                    #Email
                    if key == 'Email':
                        email = tag.find_next_sibling('a')
                        if email:
                            faculty_info['Email'] = email['href'].replace('mailto:', '').strip()
                    elif key == 'Web':
                        web = tag.find_next_sibling('a')
                        if web:
                            faculty_info['Web'] = web['href'].strip()
                    else:
                        faculty_info[key.lower()] = value
            
            if faculty_info:
                professors.append(faculty_info)
    return professors

target_url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
page = pages.find_one({"url" : target_url})
html = page['html']

faculty_info = parse_permanent_faculty(html)

#Inserting professors' information in MongoDB database
for professor in faculty_info:
    professors_info.insert_one(professor)
                            