# import time
# import atexit
# import requests, json
# from apscheduler.schedulers.background import BackgroundScheduler
# from .views import
#
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=  , trigger="interval", seconds=60)
# scheduler.start()
#
# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())
#
#
# def get_region(ip):
#     API_KEY = '83e02d8e505e64b7cdfd2125e5bb1b93b987b0f12cf12fa67788bab52bead496'
#     req = requests.get(f"https://api.ipinfodb.com/v3/ip-city/?key={API_KEY}&ip={ip}&format=json")
#     print(req.json()["timeZone"])
#
# print(get_region('8.8.8.8'))