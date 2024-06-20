function run(){
  `python manage.py runserver`
}

function save(){
  pip freeze > requirements.txt
}

function app(){
  python manage.py startapp "$1"
}

function migrate(){
  python manage.py makemigrations
  python manage.py migrate
}

function build(){
  pip install -r requirements.txt
}

function template(){
  cd "$1"
  mkdir templates
  mkdir "$1"
  cd ..
}