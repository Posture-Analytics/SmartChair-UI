import pickle

data_types = {
    "correct_posture": {
        "p00": 1500,
        "p01": 1500,
        "p02": 1500,
        "p03": 1500,
        "p04": 1500,
        "p05": 1500,
        "p06": 1500,
        "p07": 1500,
        "p08": 1500,
        "p09": 1500,
        "p10": 1500,
        "p11": 1500
    },
    "leaning_forward": {
        "p00": 0,
        "p01": 0,
        "p02": 0,
        "p03": 0,
        "p04": 0,
        "p05": 0,
        "p06": 3000,
        "p07": 3000,
        "p08": 3000,
        "p09": 3000,
        "p10": 3000,
        "p11": 3000
    },
    "relaxed_posture": {
        "p00": 3000,
        "p01": 3000,
        "p02": 3000,
        "p03": 3000,
        "p04": 0,
        "p05": 0,
        "p06": 0,
        "p07": 0,
        "p08": 3000,
        "p09": 3000,
        "p10": 3000,
        "p11": 3000
    },
    "unbalanced_posture": {
        "p00": 3000,
        "p01": 0,
        "p02": 3000,
        "p03": 0,
        "p04": 3000,
        "p05": 0,
        "p06": 3000,
        "p07": 0,
        "p08": 3000,
        "p09": 0,
        "p10": 3000,
        "p11": 0
    },
    "not_sitting": {
        "p00": 0,
        "p01": 0,
        "p02": 0,
        "p03": 0,
        "p04": 0,
        "p05": 0,
        "p06": 0,
        "p07": 0,
        "p08": 0,
        "p09": 0,
        "p10": 0,
        "p11": 0
    }
}

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

print('model loaded')

for key in data_types.keys():
    print(key, ":", model.predict([list(data_types[key].values())]))