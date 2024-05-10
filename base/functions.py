from datetime import datetime
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import joblib
import numpy as np

def get_season():
    month = datetime.now().month
    if month >= 12 or month <= 5:
        return "Dry"
    else:
        return "Rainy"

def get_df():
    df = pd.read_csv('static/assets/models/save.csv')
    le_season = LabelEncoder()
    le_weather = LabelEncoder()
    le_sickness = LabelEncoder()
    
    df['le_season'] = le_season.fit_transform(df['Season'])
    df['le_weather'] = le_weather.fit_transform(df['Weather'])
    df['le_sickness'] = le_sickness.fit_transform(df['Sickness'])
    
    f_df = df.drop(['Season', 'Weather', 'Sickness'], axis=1)
    f_df['le_sickness'] = le_sickness.inverse_transform(f_df['le_sickness'])
    f_df['le_weather'] = le_weather.inverse_transform(f_df['le_weather'])
    f_df['le_season'] = le_season.inverse_transform(f_df['le_season'])
    return f_df

def pred(season, weather):
    df = pd.read_csv('static/assets/models/save.csv')
    le_season = LabelEncoder()
    le_weather = LabelEncoder()
    le_sickness = LabelEncoder()
    
    df['le_season'] = le_season.fit_transform(df['Season'])
    df['le_weather'] = le_weather.fit_transform(df['Weather'])
    df['le_sickness'] = le_sickness.fit_transform(df['Sickness'])

    model = joblib.load('static/assets/models/weather.joblib')
    weather = weather.str.lower()
    weather = le_season.fit_transform(weather)
    season = season.str.lower()
    season = le_season.fit_transform(season)

    y_prob = model.predict_proba([[season, weather]])
    labels = le_sickness.classes_
    preds = []

    for prob in y_prob:
        # Create a list of (class_label, probability) tuples
        class_prob = list(zip(labels, prob))
        
        # Sort the tuples by probability in descending order
        sort_prob = sorted(class_prob, key=lambda x: x[1], reverse=True)
        top_10_classes = [label for label, _ in sort_prob[:10]]
        preds.append(top_10_classes)

    preds = np.array(preds)
    return preds
