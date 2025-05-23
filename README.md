# Проект Foodgram.
Foodgram - сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек использованных технологий
#### Frontend - JavaScript, HTML, CSS, React.
#### Backend - python 3.9, Django, PostgreSQL, REST API, Gunicorn, Nginx, Docker, Docker-Compose, Git, GitHub Actions.

# Как развернуть проект
1. Установить Docker.
2. Склонировать, настроить и запустить проект выполняя команды в терминале.

## 1. Установить Docker.
### Установка Docker на Windows 10-11
1. Для запуска проекта неоходимо установить Windows Subsystem for Linux [инструкция с официального сайта Microsoft](https://docs.microsoft.com/ru-ru/windows/wsl/install-win10).
2. Скачайте и установите [Docker](https://www.docker.com/products/docker-desktop/).
3. Запустите Docker Desctop.

Для работы с докером можно будет использовать любой доступный терминал рекомендуeтся работать в [Git Bash](https://git-scm.com/downloads/win).

### Установка Docker на Windows 8 и более старых версий:
1. Скачайте и установите программу для работы с виртуальными машинами, например [VirtualBox](https://www.virtualbox.org/wiki/Downloads).
2. Скачайте образ [Ubuntu](https://ubuntu.com/download/desktop).
3. Установите Ubuntu на виртуальную машину.
4. В виртуальную машину установите Docker по инструкции для Linux.

### Установка Docker на Linux
Первый способ установить Docker на Linux — скачать и выполнить [официальный скрипт](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script) :
1. Скачайте и установите curl:
    ```
    sudo apt update
    sudo apt install curl
    ```
2. Скачайте скрипт для установки докера с официального сайта:
    ```
    curl -fSL https://get.docker.com -o get-docker.sh 
    ```
3. Запустите сохранённый скрипт с правами суперпользователя:
    ```
    sudo sh ./get-docker.sh
    ```
Второй способ установить Docker вручную: [официальная документации Docker](https://docs.docker.com/engine/install/ubuntu/).

4. Установите утилиту Docker Compose:
    ```
    sudo apt install docker-compose-plugin 
    ```

### Установка Docker на macOS
Зайдите [на официальный сайт проекта](https://www.docker.com/products/docker-desktop) и скачайте установочный файл Docker Desktop для вашей платформы — Apple Chip для процессоров M1/M2 и Intel Chip для процессоров Intel.

Откройте скачанный DMG-файл и перетащите Docker в Applications, а потом — запустите программу Docker.

## 2. Клонирование, настройка и запуск проекта.
1. Создать директорию для проекта.
2. Склонировать репозиторий в папку проекта. В терминале перейти в созданную директорию (команда `cd`) и ввести команду:
    ```
    git clone https://github.com/LinarAl/kittygram_final.git
    ```
3. Создать файл .env в папке с проектом (`.../foodgram/`). Пример файла `.env`:
    ```
    SECRET_KEY= 'django_project_secret_key'
    DEBUG=True
    ALLOWED_HOSTS='localhost 127.0.0.1'
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    POSTGRES_DB=django_db
    DB_HOST=db
    DB_PORT=5432
    ```
4. Выполнить команды в терминале.
 
    Находясь в директории проекта перейдите в директорию (`.../foodgram/infra/`) c файлом `docker-compose.yml` запустите Docker Compose:
    
    В теминале :
    ```    
    docker compose up
    ```
    Откройте второе окно терминала и выполните миграции, собирите статику и заполните базу данных ингредиентами:   
    ```
    docker compose exec foodgram_backend python manage.py migrate

    docker compose exec foodgram_backend python manage.py collectstatic
    
    docker compose exec foodgram_backend python manage.py load_ingredients
    ```
    Создайте суперпользователя :
    ```
    docker compose exec foodgram_backend python manage.py createsuperuser
    ```
    ( как **остановить контейнеры** в Docker Compose ) :
    
    ```
        docker compose stop
    ```
5. Проект доступен в браузере по адресу :  http://127.0.0.1:8000/


## 3. Основные ссылки проекта.
- Зона администрирования проекта : http://127.0.0.1:8000/admin/
- API проекта: http://127.0.0.1:8000/api/
- Документация API: http://127.0.0.1:8000/api/docs/  
- Развернуктый проект доступен по ссылке https://yc-foodgram.zapto.org

## Автор Проекта    
[Линар А.](https://github.com/LinarAl)