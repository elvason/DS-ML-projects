import requests


#obtain appids of currently most popular games
def get_appids():
  r = requests.get("https://steamspy.com/api.php?request=top100in2weeks")
  appids = list(r.json().keys())
  return appids

