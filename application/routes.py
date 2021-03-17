from flask import request, render_template, url_for, redirect
from application.models import Checklist, Task
from application.forms import TaskForm, ListForm
from application import db, app

# db.drop_all()
db.create_all()

@app.route("/", methods=["GET", "POST"])
def home():
    list_input = ListForm()
    message = "Add a new list, or select a list to edit."
    if request.method == "POST" and list_input.validate_on_submit():
        new_list = Checklist(name=list_input.user_input.data)
        db.session.add(new_list)
        db.session.commit()
        list_input.user_input.data=""
        message = "list added!"
    else:
        if list_input.user_input.errors:
            message = list_input.user_input.errors[0]

    lists = Checklist.query.all()
    lists_to_be_displayed = []
    for item in lists:
        lists_to_be_displayed.append(item.name)

    return render_template('home.html', lists=lists_to_be_displayed, form=list_input, message=message)

@app.route("/edit_list/<list_name>", methods=["GET", "POST"])
def editList(list_name):
    if not Checklist.query.filter_by(name=list_name).first():    # Robust to nonexistent links.
        return redirect(url_for("home"))
    list_id = str(Checklist.query.filter_by(name=list_name).first().id)
    task_input = TaskForm()
    message = "Add tasks!"

    if request.method == "POST" and task_input.validate_on_submit():
        new_task = Task(name=task_input.user_input.data, list_id=list_id)
        db.session.add(new_task)
        db.session.commit()
        task_input.user_input.data = ""
        message = "task added!"
    else:
        if task_input.user_input.errors:
            message = task_input.user_input.errors[0]

    tasks = Task.query.filter_by(list_id=list_id).all()
    tasks_to_be_displayed = []
    for item in tasks:
        tasks_to_be_displayed.append(item.name)

    return render_template("edit.html", list_name=list_name, tasks=tasks_to_be_displayed, form=task_input, message=message)

@app.route("/delete_list/<list_name>", methods=["GET", "POST"])
def deleteList(list_name):
    if not Checklist.query.filter_by(name=list_name).first(): # Robust to nonexistent links.
        return redirect(url_for("home"))
    list_pending_deletion = Checklist.query.filter_by(name=list_name).first()
    tasks_pending_deletion = Task.query.filter_by(list_id=list_pending_deletion.id).all()
    for task in tasks_pending_deletion:
        db.session.delete(task)
    db.session.delete(list_pending_deletion)
    db.session.commit()

    return redirect(url_for("home"))

@app.route("/delete_task/<list_name>/<task_name>")
def deleteTask(list_name, task_name):
    if not Task.query.filter_by(name=task_name).first():    # Robust to nonexistent links.
        return redirect(url_for("home"))
    task_pending_deletion = Task.query.filter_by(name=task_name).first()
    db.session.delete(task_pending_deletion)
    db.session.commit()

    list_name = Checklist.query.filter_by(id=task_pending_deletion.list_id).first().name

    return redirect(url_for("editList", list_name=list_name))
