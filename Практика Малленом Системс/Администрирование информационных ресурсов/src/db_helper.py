from flask import Flask, render_template, request, redirect
import psycopg2
from datetime import datetime

app = Flask(__name__)

def db():
    return psycopg2.connect(host="localhost", database="Web_Site_DB", user="postgres", password="123")

@app.route('/')
def index():
    with db() as conn:
        with conn.cursor() as cur:
            # Возвращаем related_links
            cur.execute('SELECT title, content, related_links FROM articles LIMIT 1')
            article = cur.fetchone()
            cur.execute('SELECT author, message, created_at FROM comments WHERE is_approved = TRUE ORDER BY created_at DESC')
            comments = cur.fetchall()
    return render_template('index.html', article=article, comments=comments)

@app.route('/add', methods=['POST'])
def add():
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO comments (author, message) VALUES (%s, %s)', 
                        (request.form.get('author') or 'Аноним', request.form.get('message')))
            conn.commit()
    return redirect('/')

@app.route('/admin')
def admin():
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT title, content, related_links FROM articles LIMIT 1')
            article = cur.fetchone()
            cur.execute('SELECT id, author, message FROM comments ORDER BY created_at DESC')
            comments = cur.fetchall()
    return render_template('admin.html', article=article, comments=comments)

@app.route('/update', methods=['POST'])
def update():
    with db() as conn:
        with conn.cursor() as cur:
            # Обновление всех полей, включая ссылку
            cur.execute('UPDATE articles SET title=%s, content=%s, related_links=%s WHERE id=1', 
                        (request.form.get('title'), request.form.get('content'), request.form.get('links')))
            cur.execute('INSERT INTO admin_logs (action) VALUES (%s)', ('Обновление контента статьи',))
            conn.commit()
    return redirect('/admin')

@app.route('/del/<int:id>')
def delete(id):
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM comments WHERE id=%s', (id,))
            cur.execute('INSERT INTO admin_logs (action) VALUES (%s)', (f'Удаление комментария ID {id}',))
            conn.commit() 
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)