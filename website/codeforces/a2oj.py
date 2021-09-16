from bs4 import BeautifulSoup
import requests, json


def get_ladders():
    ladders = []
    url = "https://www.a2oj.com/Ladders.html"

    data = requests.get(url, verify=False).text
    soup = BeautifulSoup(data, features="lxml")
    tables = soup.findAll("table")

    for table_no in range(2):
        for row in tables[table_no].find_all("tr")[1:]:
            t = {}
            tds = row.find_all("td")
            name = tds[1].get_text()
            link = tds[1].find('a').get('href')
            t['name'] = name
            t['link'] = link
            ladders.append(t)
    return ladders


def get_categories():
    categories = []
    url = "https://www.a2oj.com/Categories.html"

    data = requests.get(url, verify=False).text
    soup = BeautifulSoup(data, features="lxml")
    tables = soup.findAll("table")

    for row in tables[0].find_all("tr")[1:]:
        t = {}
        tds = row.find_all("td")
        name = tds[1].get_text()
        link = str(tds[1]).split('href="')[1].split('"')[0]
        t['name'] = name
        t['link'] = link
        categories.append(t)
    return categories


def get_set_from_ladder_category(link):
    url = f"https://www.a2oj.com/{link}"

    data = requests.get(url, verify=False).text
    soup = BeautifulSoup(data, features="lxml")
    tables = soup.findAll("table")

    try:
        problems = tables[1]
    except:
        problems = tables[0]

    problem_set = []
    for row in problems.find_all("tr")[1:]:
        tds = row.find_all("td")
        judge = tds[2].get_text()
        name = tds[1].get_text()
        # print(judge, tds[1])
        prob = tds[1].find("a").get('href')
        if judge == 'Codeforces':
            prob = prob.split('problem/')[-1]
        elif judge == 'SPOJ':
            prob = prob.split('problems/')[-1].replace('/', '')
        # elif judge == 'CodeChef':
        #     prob = prob.split('problems/')[-1]
        else:
            continue

        problem_set.append({'judge': judge, 'name': name, 'code': prob})

    return problem_set


def get_all_problems():
    ladders = get_ladders()
    categories = get_categories()

    problem_sets = []
    
    for ladder in ladders:
        name = ladder['name']
        link = ladder['link']
        problem_set = get_set_from_ladder_category(link)
        problem_sets.append({'name': name, 'set': problem_set, 'type': 'ladder'})

    for cat in categories:
        name = cat['name']
        link = cat['link']
        problem_set = get_set_from_ladder_category(link)
        problem_sets.append({'name': name, 'set': problem_set, 'type': 'category'})

    json.dump(problem_sets, open('problem_sets.json', 'w'))


get_all_problems()


