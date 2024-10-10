First of all clone this project 
create local env  by using 
python -m venv env 

then activate the local env 
using these commands 

cd env
cd scripts 
.\activate 

cd..
cd..
then isntall the requirements 
by the following commands 

pip install -r requirements.txt

then 
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
