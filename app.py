import os
from bs4 import BeautifulSoup
import requests
from stdiomask import getpass

session = requests.Session()
loginPage = "http://acm.vgtu.lt/login/"
mainPage = "http://acm.vgtu.lt/courses/my/"

def get_csrf_token(soup):
    return soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

def login(username, password):
    response = session.get(loginPage)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = get_csrf_token(soup)
    data = {
        'csrfmiddlewaretoken': csrf_token,
        'auth-username': username,
        'auth-password': password,
        'login_view-current_step': 'auth'
    }
    session.post(loginPage, data=data)

def download_source_code(href, name, index):
    cppPage = f"http://acm.vgtu.lt{href}source/open/solution.cpp"
    response = session.get(cppPage)
    soup = BeautifulSoup(response.content, 'html.parser')
    filename = f"{name.replace('/', '_')} {index}.cpp"
    file_path = os.path.join(script_dir, filename)
    with open(file_path, "w") as file:
        file.write(soup.text)

username = input("ID: ")
password = getpass(prompt="Password: ", mask="*")

login(username=username, password=password)

response = session.get(mainPage)
html = BeautifulSoup(response.content, 'html.parser')
solution_list = html.find('table', class_='ir-course-list').find_all('tr')

script_dir = os.path.dirname(os.path.abspath(__file__))

for item in solution_list:
    anchor_tag = item.find('a')
    if anchor_tag:
        href = anchor_tag.get('href')
        name = anchor_tag.text
        link = f"http://acm.vgtu.lt{href.strip()}standings/"
        response = session.get(link)
        solutions = BeautifulSoup(response.content, 'html.parser')
        me_list = solutions.find('tr', class_='ir-me')

        if me_list is not None:
            href_tags = me_list.find_all('td')

            index = 1
            for div in me_list.find_all('div', class_='ir-box'):
                if 'ir-scorebox' in div.get('class') and 'ir-scorebox-accepted' in div.get('class') and len(div.text.strip()) == 1:
                    td = div.parent
                    href = td.get('href') if td is not None else None
                    download_source_code(href, name, index)
                index += 1