from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///sqlite.db')
db = SQLAlchemy(app)
app.app_context().push()

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    complete = db.Column(db.Boolean, default=False)

@app.route('/')
def hello():
    todo_list = Todo.query.all()
    total_todo = Todo.query.count()
    completed_todo = Todo.query.filter_by(complete=True).count()
    remaining_todo = Todo.query.filter_by(complete=False).count()
    return render_template('./dashboard/index.html', **locals())

@app.route('/add', methods=['POST', 'GET'])
def add():
    title = request.form.get('title')
    description = request.form.get('description')
    if title and description:
        new_todo = Todo(title=title, description=description, complete=False)
        db.session.add(new_todo)
        db.session.commit()
    return redirect(url_for('hello'))

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('hello'))

@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    todo = Todo.query.get_or_404(id)
    if request.method == 'GET':
        return render_template('./dashboard/update.html', todo=todo)
    elif request.method == 'POST':
        todo.title = request.form.get('title')
        todo.description = request.form.get('description')
        db.session.commit()
    return redirect(url_for('hello'))

@app.route('/toggle/<int:id>', methods=['GET'])
def toggle(id):
    todo = Todo.query.get_or_404(id)
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for('hello'))

@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('q')
    todo_list = Todo.query.filter(Todo.title.like(f'%{q}%') | Todo.description.like(f'%{q}%')).all()
    if todo_list:
        return jsonify([{'id': todo.id, 'title': todo.title, 'description': todo.description} for todo in todo_list])
    else:
        return jsonify([{"Error":"Not Found"}])

@app.route('/about')
def about():
    return render_template('./dashboard/about.html')

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False))
