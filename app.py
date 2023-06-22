import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
# Глобальный объект request для доступа к входящим данным запроса, которые будут подаваться через форму HTML.
# Функция url_for() для генерирования URL-адресов.
# Функция flash() для появления сообщения при обработке запроса.
# Функция redirect() для перенаправления клиента в другое расположение.
from werkzeug.exceptions import abort

from key import SecretKey

# Эта функция get_db_connection() открывает соединение с файлом базы данных database.db, 
# а затем устанавливает атрибут row_factory в sqlite3. Row, чтобы получить доступ к столбцам на основе имен. 
# Это означает, что подключение к базе данных будет возвращать строки, которые ведут себя как обычные словари Python. 
# И наконец, функция возвращает объект подключения conn, который вы будете использовать для доступа к базе данных.
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

#Эта новая функция имеет аргумент post_id, который определяет, какой пост блога предназначен для возврата.
#Внутри функции вы используете функцию get_db_connection() для открытия подключения к базе данных и выполнения запроса SQL, 
# чтобы получить пост блога, связанный с указанным значением post_id. Вы добавляете метод fetchone() для получения результата 
# и хранения его в переменной post, а затем закрываете подключение. Если переменная post имеет значение None​​​, 
# т. е. результат не найден в базе данных, вы используете функцию abort(), импортированную вами ранее, 
# для ответа с помощью кода ошибки 404, и функция завершит выполнение. Если же пост был найден, вы возвращаете значение переменной post.
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

app = Flask(__name__)
app.config['SECRET_KEY'] = SecretKey

#В этой новой версии функции index() сначала откройте подключение к базе данных, используя функцию get_db_connection(), которую вы определили ранее. 
#После этого выполните запрос SQL, чтобы выбрать все записи из таблицы posts. Вы применяете метод fetchall(), 
# чтобы доставить все строки результата запроса. Это вернет список постов, внесенных в базу данных на предыдущем шаге.
#Вы закрываете подключение к базе данных, используя метод close(), и возвращаете результат отображения шаблона index.html. 
# Вы также передаете объект posts в качестве аргумента, который содержит результаты, полученные из базы данных. 
# Это откроет вам доступ к постам блога в шаблоне index.html.
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

#В этой новой функции просмотра вы добавляете правило переменной <int:post_id>, 
# чтобы указать, что часть после слеша (/) представляет собой положительное целое число (отмеченное конвертером int), 
# которое вам необходимо в функции просмотра. Flask распознает это и передает его значение аргументу ключевого слова post_id​​ 
# вашей функции просмотра post(). Затем вы используете функцию get_post() для получения поста блога, связанного с заданным ID, 
# и хранения результата в переменной post, которую вы передаете шаблону post.html. 
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

# Это создает маршрут /create, который принимает запросы GET и POST. 
# Запросы GET принимаются по умолчанию. Для того чтобы также принимать запросы POST, 
# которые посылаются браузером при подаче форм, вы передаете кортеж с приемлемыми типами запросов в аргумент methods декоратора @app.route().
@app.route('/create', methods=('GET', 'POST'))
def create():
    #Выражением if вы обеспечиваете, что следующий за ним код выполняется только в случае, 
    #если запрос является запросом POST через сравнение request.method == 'POST'​​​.
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        #Затем вы извлекаете отправленные заголовок и содержание из объекта request.form, 
        # который дает вам доступ к данным формы в запросе. Если заголовок не указан, будет выполнено условие if not title, 
        # и отобразится сообщение для пользователя с информацией о необходимости заголовка. С другой стороны, если заголовок указан, 
        # вы открываете подключение с помощью функции get_db_connection() и вставляете полученные заголовок и содержание в таблицу posts.
        if not title:
            flash('Title is requred')
        #Затем вы вносите изменения в базу данных и закрываете подключение. После добавления поста блога в базу данных вы перенаправляете клиента 
        # на страницу индекса с помощью функции redirect(), передавая URL, сгенерированный функцией url_for() со значением 'index'​​ 
        # в качестве аргумента.
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')

# Пост, который вы редактируете, определяется с помощью URL, а Flask будет передавать номер ID функции edit() через аргумент id. 
# Вы добавляете это значение к функции get_post(), чтобы доставить пост, связанный с указанным ID, из базы данных. 
# Новые данные будут поступать в запросе POST, который обрабатывается внутри условия if request.method == 'POST'.
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

# Эта функция просмотра принимает только запросы POST. Это означает, что навигация по маршруту /ID/delete в вашем браузере вернет ошибку, 
# так как веб-браузеры по умолчанию настроены на запросы GET.
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))