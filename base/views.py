from django.shortcuts import render
import requests
import environ
from .functions import get_season, pred, train_model, load_data_and_model

env = environ.Env()
environ.Env.read_env(env_file='.env')

# Create your views here.
def home(request):
    train_model()
    df, model, le_season, le_sickness, le_weather = load_data_and_model()
    request_url = f"https://api.openweathermap.org/data/2.5/weather?appid={env.str('WEATHER')}&q=Bacolor,PH&units=metric"
    weatherData = requests.get(request_url).json()
    temp = weatherData['main']['temp']
    feels = weatherData['main']['feels_like']
    season = get_season()
    weather_info = weatherData['weather'][0]
    weather = weather_info['main']
    predict = pred(season, weather, df, model, le_season, le_sickness, le_weather)
    
    context = {
        # 'f_df': f_df.to_dict('records'),
        'temp': temp,
        'feels':feels,
        'predict': predict[0]
        } 
    
    return render(request, 'landingpage.html', context)
def weather(request):
    train_model()
    df, model, le_season, le_sickness, le_weather = load_data_and_model()
    request_url = f"https://api.openweathermap.org/data/2.5/weather?appid={env.str('WEATHER')}&q=Bacolor,PH&units=metric"
    weatherData = requests.get(request_url).json()
    temp = weatherData['main']['temp']
    feels = weatherData['main']['feels_like']
    season = get_season()
    weather_info = weatherData['weather'][0]
    weather = weather_info['main']
    predict = pred(season, weather, df, model, le_season, le_sickness, le_weather)
    
    context = {
        # 'f_df': f_df.to_dict('records'),
        'weatherData': weatherData,
        'season': season,
        'temp': temp,
        'feels':feels,
        'weather':weather,
        'predict': predict[0]
        } 
    return render(request, 'weather.html', context)