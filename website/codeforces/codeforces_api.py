import json

import requests

# handle = 'M_Agour'
# api_key = '112d1d0fe812d9a93752d0d11bc1a82547cdcde2'
# secret = 'a21b4e763ffe0ad57e39be2bac9e1f061847ec98'
#
# # print(f'https://codeforces.com/api/user.status?handle={handle}&apiKey={api_key}&time=1631623688#{secret}')
# req = f'https://codeforces.com/api/user.status?handle={handle}'


def get_problem_set():
    return requests.get("https://codeforces.com/api/problemset.problems").json()


def get_user_submissions(handle):
    return requests.get(f'https://codeforces.com/api/user.status?handle={handle}').json()


def generate_problems_info():
    set = get_problem_set()
    problem_name_rating = {}
    for i in set['result']["problems"]:
        name = i['name']
        contestId = i['contestId']
        index = i['index']
        try:
            rating = i['rating']
        except :
            rating = 9999
        merged = f"{contestId}/{index}"

        problem_name_rating[merged] = name, rating

    return problem_name_rating


def generate_problems_stats():
    set = get_problem_set()
    problem_solve_count = {}

    for i in set['result']["problemStatistics"]:
        contestId = i['contestId']
        index = i['index']
        count = i['solvedCount']
        merged = f"{contestId}/{index}"
        problem_solve_count[merged] = count
    return problem_solve_count


def get_solved_problems(handle):
    solved = []
    user = get_user_submissions(handle)
    try:
        for i in user['result']:
            p = i['problem']
            if i["verdict"] == 'OK':
                solved.append(f"{p['contestId']}/{p['index']}")
        return solved
    except:

        try:
            if user['comment'] == f'handle: User with handle {handle} not found':
                return solved
            else:
                return solved
        except:
            return solved


def generate_ordered_problems_id_name_solved():

    info = generate_problems_info()
    solved = generate_problems_stats()
    ordered_by_most_solved = [(i, info[i][0], info[i][1], solved[i]) for i in info.keys()]
    ordered_by_most_solved.sort(key=lambda x: x[3], reverse=True)
    return ordered_by_most_solved




# generate_problems_id_name_solved()