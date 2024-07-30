from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
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
    df = pd.read_csv('healthharmony/static/assets/models/save.csv')
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

def load_data_and_model():
    df = pd.read_csv('healthharmony/static/assets/models/save.csv')

    #Encoders
    le_season = LabelEncoder()
    le_weather = LabelEncoder()
    le_sickness = LabelEncoder()

    # Transform categorical variables and store in the DataFrame
    df['le_season'] = le_season.fit_transform(df['Season'])
    df['le_weather'] = le_weather.fit_transform(df['Weather'])
    df['le_sickness'] = le_sickness.fit_transform(df['Sickness'])
    df = df.drop(['Season', 'Weather', 'Sickness'], axis=1)

    model = joblib.load('healthharmony/static/assets/models/weather.joblib')

    return df, model, le_season, le_sickness, le_weather

def pred(season, weather, df, model, le_season, le_sickness, le_weather):
    season_encoded = le_season.transform([season.lower()])
    weather_encoded = le_weather.transform([weather.lower()])
    
    # Concatenate the encoded features into a 2D array
    X = np.array([[season_encoded, weather_encoded]])  # Ensure X is a 2D array
    X = X.reshape(1, -1)  # Reshape to match expected input shape for prediction
    
    # Predict probabilities using the loaded model
    y_prob = model.predict_proba(X)
    labels = le_sickness.classes_
    preds = []

    for prob in y_prob:
        # Create a list of (class_label, probability) tuples
        class_prob = list(zip(labels, prob))
        
        # Sort the tuples by probability in descending order
        sort_prob = sorted(class_prob, key=lambda x: x[1], reverse=True)
        top_10_classes = [label for label, _ in sort_prob[:5]]
        preds.append(top_10_classes)

    preds = np.array(preds)
    return preds

def train_model():
    df = pd.read_csv('healthharmony/static/assets/models/data.csv')
    df = df[['Season', 'Weather', 'Sickness']]
    df['Weather'] = df['Weather'].str.lower()
    df['Season'] = df['Season'].str.lower()
    df['Sickness'] = df['Sickness'].str.lower()
    dfna = df[df.isna().any(axis=1)]
    weather=df['Weather'].unique()
    new_rows = []

    # Iterate over rows with NaN values
    for index, row in dfna.iterrows():
        # Iterate over unique 'Weather' values
        for weth in weather:
            # Create a new dictionary with modified 'Weather'
            new_row = {'Season': row['Season'], 'Weather': weth, 'Sickness': row['Sickness']}
            # Append the new dictionary to the list
            new_rows.append(new_row)
    newdf = pd.DataFrame(new_rows)
    final = pd.concat([df, newdf])
    final = final.dropna()
    final = final.reset_index(drop=True)
    df = final

    df.to_csv('healthharmony/static/assets/models/save.csv')

    le_season = LabelEncoder()
    le_weather = LabelEncoder()
    le_sickness = LabelEncoder()
    df['le_season'] = le_season.fit_transform(df['Season'])
    df['le_weather'] = le_weather.fit_transform(df['Weather'])
    df['le_sickness'] = le_sickness.fit_transform(df['Sickness'])
    f_df = df.drop(['Season', 'Weather', 'Sickness'], axis=1)

    X = f_df.drop('le_sickness', axis=1)
    y = f_df['le_sickness']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    

    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, 'healthharmony/static/assets/models/weather.joblib')
