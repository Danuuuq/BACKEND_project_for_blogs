# Проект "Блогикум".

Блогикум - социальная сеть для публикации личных дневников.  
*Проект реализован самостоятельно на курсе от Я.Практикум "Python-разработчик расширенный".*  
*Фронтенд реализован авторами курса*

## Доработки в рамках 4-го спринта

1. Регистрация пользователей
2. Добавление публикаций пользователями
3. Добавление фотографий к публикациям
4. Удаление и редактирование публикаций
5. Комментирование публикаций других пользователей
6. Сброс пароля по почте(бета-версия)
7. Пагинация, вывод только 10 последних публикаций

## Порядок запуска сайта

Клонируйте репозиторий себе на компьютер/сервер:

```bash
git clone git@github.com:user_name/django_sprint4.git
```

Создайте виртуальное окружение:

```bash
python3 -m venv venv
```

Активируйте виртуальное окружение:

*Windows:*
```bash
source venv/Scripts/activate
```
*Linux:*
```bash
source venv/Bin/activate
```

Установите зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

## Описание функционала сайта:

1. **Главная страницы.** Отображаются последние публикации отсортированные
   по дате, с пагинацией по 10 публикаций на странице.
2. **Страницы публикации.** Выводит детальное содержание публикации
   с возможностью добавлять комментарии. Пользователь может
   редактировать или удалить свою публикацию, добавить изображения.
   Пользователи оставившие комментарии, могут удалять или отредактировать их.
3. **Страница пользователя.** Содержит его публикации, если они сняты или
   дата публикации в будущем, то их видит только пользователь страницы.
   Пользователь страницы, может редактировать свою учетную запись и пароль
4. **Страница категории.** Содержит публикации из данной категории.
5. **Изображение.** К каждой публикации можно добавить или удалить
   изображение, при удалении с публикации, она также удаляется из директории.
6. **Страницы ошибок.** Для ошибок используются шаблоны для этого 
   описаны *view* функции из приложения *pages*.
7. **Представление.** Представление для публикаций в приложении *blog*
   написаны с помощью CBV с проверками условий и оптимизацией запросов к БД.
8. **Пагинация.** Пагинация на страницах пользователя и категорий реализована
   с помощью `ListView' и 'SingleObjectMixin'.

