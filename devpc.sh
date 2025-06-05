source venv/bin/activate
export https_proxy=http://127.0.0.1:7890;export http_proxy=http://127.0.0.1:7890;export all_proxy=socks5://127.0.0.1:7890
export DJANGO_SETTINGS_MODULE=django_project.settings



alias pm="python manage.py"
alias runserver="pm runserver"
alias runserver_init_data="./runserver_init_data.sh"
