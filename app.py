from flask import Flask, render_template, redirect, request,url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask("__name__")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)
app.app_context().push()

class todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    complete = db.Column(db.Boolean, default = False)


@app.route('/')
def hello():
    todo_list = todo.query.all()
    total_todo = todo.query.count()
    completed_todo = todo.query.filter_by(complete=True).count()
    remaining_todo = todo.query.filter_by(complete=False).count()
    # return render_template('./dashboard/index.html', todo_list = todo_list, total_todo = total_todo, completed_todo = completed_todo, remaining_todo = remaining_todo)
    return render_template('./dashboard/index.html', **locals() )
    
@app.route('/add', methods=['POST', 'GET'])
def add():
    title = request.form.get('title')
    description = request.form.get('description')
    if title and description:
        new_todo = todo(title=title, description=description, complete=False)
        db.session.add(new_todo)
        db.session.commit()
    return redirect(url_for('hello'))

@app.route('/delete/<int:id>', methods = ['POST', 'GET'])
def delete(id):
    todoo = todo.query.filter_by(id=id).first()
    db.session.delete(todoo)
    db.session.commit()
    return redirect(url_for('hello'))


@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    todoo = todo.query.filter_by(id=id).first()
    if request.method == 'GET':
        return render_template('./dashboard/update.html', todo=todoo)
    elif request.method == 'POST':
        todoo.title = request.form.get('title')
        todoo.description = request.form.get('description')
        db.session.commit()
    return redirect(url_for('hello'))

@app.route('/toggle/<int:id>', methods=['GET'])
def toggle(id):
    todoo = todo.query.filter_by(id=id).first()
    todoo.complete = not todoo.complete
    db.session.commit()
    return redirect(url_for('hello'))

@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('q')
    todo_list = todo.query.filter(todo.title.like('%' + q + '%') | todo.description.like('%' + q + '%')).all()
    if todo_list:
        return jsonify([{'id': todo.id, 'title': todo.title, 'description': todo.description} for todo in todo_list])
    else:
        return jsonify([{"Error":"Not Found"}])

@app.route('/about')
def about():
    return render_template('./dashboard/about.html')
    

if (__name__) == '__main__':
    app.run(debug=True)