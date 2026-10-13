#!/bin/zsh
echo "a lancer avec source ./create_venv.sh"

python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver &
