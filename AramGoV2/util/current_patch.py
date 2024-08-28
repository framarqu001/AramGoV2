import requests


def get_patch():
    url = 'https://ddragon.leagueoflegends.com/api/versions.json'
    response = requests.get(url)
    response = response.json()
    return response[0]
