from django.shortcuts import render
import requests
import environ
from .functions import get_season, get_df, pred

env = environ.Env()
environ.Env.read_env(env_file='.env')

# Create your views here.
def home(request):
    context = {}
    
    return render(request, 'landingpage.html', context)
def weather(request):
    f_df = get_df()
    request_url = f"https://api.openweathermap.org/data/2.5/weather?appid={env.str('WEATHER')}&q=Bacolor,PH&units=metric"
    weatherData = requests.get(request_url).json()
    season = get_season()
    temp = weatherData['main']['temp']
    feels = weatherData['main']['feels_like']
    weather_info = weatherData['weather'][0]
    weather = weather_info['main']
    predict = pred(season, weather)
    
    context = {
        'f_df': f_df.to_dict('records'),
        'weatherData': weatherData,
        'season': season,
        'temp': temp,
        'feels':feels,
        'predict':predict
        } 
    return render(request, 'weather.html', context)