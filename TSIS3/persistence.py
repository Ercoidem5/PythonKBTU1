import json, os

SETTINGS_FILE='settings.json'
LEADERBOARD_FILE='leaderboard.json'

DEFAULT_SETTINGS={
    'sound': True,
    'car_color': [0,0,255],
    'difficulty': 'normal',
    'username': 'Player'
}


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path,'r',encoding='utf-8') as f:
            return json.load(f)
    except:
        return default


def save_json(path,data):
    with open(path,'w',encoding='utf-8') as f:
        json.dump(data,f,indent=2)


def load_settings():
    return load_json(SETTINGS_FILE, DEFAULT_SETTINGS)


def save_settings(data):
    save_json(SETTINGS_FILE,data)


def load_scores():
    return load_json(LEADERBOARD_FILE,[])


def add_score(entry):
    data=load_scores()
    data.append(entry)
    data=sorted(data,key=lambda x:x['score'],reverse=True)[:10]
    save_json(LEADERBOARD_FILE,data)
