from flask import request, render_template, url_for, redirect
from datetime import datetime
from application.models import Checklist, Task, getListId, getTaskId, getTasks, listExists, taskExists, doneListNames, notDoneListNames, getListsNames, getTaskCount, getDoneTaskCount, doneTaskNames, notDoneTaskNames
from application.forms import TaskForm, ListForm, RenameForm
from application import db, app

# db.drop_all()
db.create_all()

# Create list
@app.route("/", methods=["GET", "POST"])
def home():
    # Create

    message = "Add a new list, or select a list to edit."
    error_text = ""

    list_input = ListForm()
    if request.method == "POST" and list_input.validate_on_submit():
        new_list = Checklist(name=list_input.user_input.data)
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for("editList", list_name=new_list.name))
    else:
        if list_input.user_input.errors:
            error_text = list_input.user_input.errors[0]

    # Read
    list_details = {}
    for item in Checklist.query.all():
        list_details[item.name] = [getDoneTaskCount(item.name), getTaskCount(item.name), item.date_created, item.date_done]
    

    # Display config:

    done_lists = doneListNames()
    non_done_lists = notDoneListNames()

    if len(done_lists) == 0:
        done_lists_exists = False
    else:
        done_lists_exists = True
    if len(non_done_lists) == 0:
        non_done_lists_exists = False
    else:
        non_done_lists_exists = True

    return render_template('home.html', non_done_lists_exists=non_done_lists_exists, non_done_lists=non_done_lists, form=list_input, list_details=list_details, done_lists_exists=done_lists_exists, done_lists=done_lists, message=message, error_text=error_text)

# Create task
@app.route("/edit_list/<list_name>", methods=["GET", "POST"])
def editList(list_name):

    if not listExists(list_name):
        return redirect(url_for("home"))

    list_id = getListId(list_name)

    message = "Add tasks!"
    error_text = ""

    task_input = TaskForm()
    if request.method == "POST" and task_input.validate_on_submit():
        new_task = Task(name=task_input.user_input.data, list_id=list_id)
        db.session.add(new_task)
        db.session.commit()
        task_input.user_input.data = ""
        message = "task added!"
    else:
        if task_input.user_input.errors:
            error_text = task_input.user_input.errors[0]
    
    # Read
    task_details = {}
    for item in Task.query.all():
        task_details[item.name] = [item.date_done]
    

    # Display config:

    done_tasks = doneTaskNames(list_id=list_id)
    non_done_tasks = notDoneTaskNames(list_id=list_id)

    if len(done_tasks) == 0:
        done_tasks_exists = False
    else:
        done_tasks_exists = True
    if len(non_done_tasks) == 0:
        non_done_tasks_exists = False
    else:
        non_done_tasks_exists = True
    
    return render_template("edit_list.html", list_name=list_name, non_done_tasks_exists=non_done_tasks_exists, non_done_tasks=non_done_tasks, form=task_input, task_details=task_details, done_tasks_exists=done_tasks_exists, done_tasks=done_tasks, message=message, error_text=error_text)
    
    
# Update List
@app.route("/rename/<list_name>", methods=["GET", "POST"])
def renameList(list_name):

    if not listExists(list_name):
        return redirect(url_for("home"))

    message = f"Enter a new name for {list_name}"
    error_text = ""

    rename_list = RenameForm()
    if request.method == "POST" and rename_list.validate_on_submit():
        list_pending_update = Checklist.query.filter_by(name=list_name).first()
        list_pending_update.name = rename_list.user_input.data        
        db.session.commit()
        message = "list renamed!"
        return redirect(url_for("home"))
    else:
        if rename_list.user_input.errors:
            error_text = rename_list.user_input.errors[0]

    # Read
    list_details = {}
    for item in Checklist.query.all():
        list_details[item.name] = [getDoneTaskCount(item.name), getTaskCount(item.name), item.date_created, item.date_done]

    # Display config:

    done_lists = doneListNames()
    non_done_lists = notDoneListNames()

    if len(done_lists) == 0:
        done_lists_exists = False
    else:
        done_lists_exists = True
    if len(non_done_lists) == 0:
        non_done_lists_exists = False
    else:
        non_done_lists_exists = True

    return render_template('rename_list.html', list_name=list_name, non_done_lists_exists=non_done_lists_exists, non_done_lists=non_done_lists, form=rename_list, list_details=list_details, done_lists_exists=done_lists_exists, done_lists=done_lists, message=message, error_text=error_text)

# Update List
@app.route("/mark_done/<list_name>")
def markDoneList(list_name):

    if not listExists(list_name):
        return redirect(url_for("home"))
    
    list_pending_update = Checklist.query.filter_by(name=list_name).first()
    list_pending_update.done = True
    list_pending_update.date_done = str(datetime.today())[0:10]

    list_id = getListId(list_name)
    tasks_pending_update = getTasks(list_id)
    for item in tasks_pending_update:
        item.done = True
        item.date_done = str(datetime.today())[0:10]
        db.session.commit()
    db.session.commit()

    return redirect(url_for("home"))

# Update List 
@app.route("/mark_not_done/<list_name>")
def markNotDoneList(list_name):
    if not listExists(list_name):
        return redirect(url_for("home"))
    
    list_pending_update = Checklist.query.filter_by(name=list_name).first()
    list_pending_update.done = False
    list_pending_update.date_done = "-"
    db.session.commit()

    return redirect(url_for("home"))

# Update Task
@app.route("/mark_done/<list_name>/<task_name>")
def markDoneTask(list_name, task_name):

    if not taskExists(list_name, task_name):
        return redirect(url_for("editList", list_name=list_name))
    
    task_pending_update = Task.query.filter_by(name=task_name, list_id=getListId(list_name)).first()
    task_pending_update.done = True
    task_pending_update.date_done = str(datetime.today())[0:10]
    db.session.commit()

    

    # set list.done = true if all tasks are done.
    
    if getTaskCount(list_name) == getDoneTaskCount(list_name):

        list_pending_update = Checklist.query.filter_by(name=list_name).first()
        list_pending_update.done = True
        list_pending_update.date_done = str(datetime.today())[0:10]
        db.session.commit()  


    return redirect(url_for("editList", list_name=list_name))

# Update Task
@app.route("/mark_not_done/<list_name>/<task_name>")
def markNotDoneTask(list_name, task_name):

    if not taskExists(list_name, task_name):
        return redirect(url_for("editList", list_name=list_name))    
    
    task_pending_update = Task.query.filter_by(name=task_name, list_id=getListId(list_name)).first()
    task_pending_update.done = False
    task_pending_update.date_done = "-"
    db.session.commit()

    # set list.done = False if not all tasks are done.
    
    if getTaskCount(list_name) != getDoneTaskCount(list_name):
        list_pending_update = Checklist.query.filter_by(name=list_name).first()
        list_pending_update.done = False
        list_pending_update.date_done = "-"
        db.session.commit()

    return redirect(url_for("editList", list_name=list_name))

# Delete List
@app.route("/delete_list/<list_name>")
def deleteList(list_name):

    if not listExists(list_name):
        return redirect(url_for("home"))
    
    list_id = getListId(list_name)
    list_pending_deletion = Checklist.query.filter_by(id=list_id).first()
    tasks_pending_deletion = getTasks(getListId(list_name))

    for task in tasks_pending_deletion:
        db.session.delete(task)
    db.session.delete(list_pending_deletion)
    db.session.commit()

    return redirect(url_for("home"))

# Delete Task
@app.route("/delete_task/<list_name>/<task_name>")
def deleteTask(list_name, task_name):

    if not taskExists(list_name, task_name):
        return redirect(url_for("home"))

    list_id = getListId(list_name)
    task_pending_deletion = Task.query.filter_by(list_id=list_id, name=task_name).first()
    db.session.delete(task_pending_deletion)
    db.session.commit()

    return redirect(url_for("editList", list_name=list_name))
