import sqlite3
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Function to count the number of posts in the database
def count_post():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    post_count = cursor.execute('SELECT COUNT(id) FROM posts').fetchone()
    connection.close()
    return post_count[0]


# Function to count the total connection to the database
def count_db_connection():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    db_connection_count = cursor.execute('SELECT SUM(connection) FROM posts').fetchall()
    connection.close()
    return db_connection_count[0][0]


# Function to increment database connection by 1 per article visit
def increment_db_connection(post_id):
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute('UPDATE posts SET connection = connection + 1 WHERE id = ?',
                (post_id,)).fetchone()
    connection.commit()
    connection.close()


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


''' 
Define how each individual article is rendered and increment the db connection count by 1 per article visit.
If the post ID is not found a 404 page is shown 
'''
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    # Increment the db connection
    increment_db_connection(post_id)
    if post is None:
        # Log accessing non-existing article
        app.logger.info('A non-existing article is accessed! "404"')
        return render_template('404.html'), 404
    else:
        # Log accessing existing article
        app.logger.info('Article ' + '"' + post['title'] + '"' + ' retrieved!')
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    # Log accessing About Us page
    app.logger.info('"About Us" page was retrieved!')
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content, connection ) VALUES (?, ?, ?)',
                               (title, content, '0'))
            connection.commit()
            connection.close()

            # Log newly created article
            app.logger.info('A new article ' + '"' + title + '"' + ' was created!')
            return redirect(url_for('index'))

    return render_template('create.html')


# Define the Healthcheck endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response


# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    response = app.response_class(
        response=json.dumps({"db_connection_count": count_db_connection(), "post_count": count_post()}),
        status=200,
        mimetype='application/json'
    )
    return response


# start the application on port 3111
if __name__ == "__main__":
    # app.run(host='0.0.0.0', port='3111')

    # Create the log file and format each log
    logging.basicConfig(
        format='%(levelname)s:%(name)s:%(asctime)s, %(message)s',
        level=logging.DEBUG,
        datefmt='%m-%d-%Y, %H:%M:%S'
    )

    # Created a new line with the localhost since 0.0.0.0 does not work in Windows
    app.run(host='127.0.0.1', port='3111')
