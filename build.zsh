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

function delete(){
  find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/.venv/*" -delete
}

function template(){
  cd "$1"
  mkdir templates
  mkdir "$1"
  cd ..
}

function imports(){
  python manage.py loaddata db.json
}
function exports(){
  python manage.py dumpdata > db.json
}
function user(){
  python manage.py createsuperuser --email bercasiocharles14@gmail.com
}

function dockerbuild(){
  docker build --tag healthharmony .
}

function dockerrun(){
  docker run --publish 8000:8000 healthharmony
}

function seed(){
  python manage.py seed "$1"
}

function test(){
  python manage.py test
}
