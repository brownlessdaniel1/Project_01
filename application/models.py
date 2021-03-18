from datetime import datetime
from application import db


class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    date_created = db.Column(db.Date, nullable=False, default=datetime.today())
    date_done = db.Column(db.String(10), nullable=False, default="-")
    tasks = db.relationship("Task", backref="checklist")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    date_done = db.Column(db.String(10), nullable=False, default="-")
    list_id = db.Column(db.Integer, db.ForeignKey("checklist.id"), nullable=False)

def getListId(list_name):
    return Checklist.query.filter_by(name=list_name).first().id

def getTaskId(task_name):
    return Task.query.filter_by(name=task_name).first().id

def getListsNames():
    names_list = [item.name for item in Checklist.query.all()]
    return names_list

def getTasks(list_id):
    return  Task.query.filter_by(list_id=list_id).all()

def listExists(list_name):
    return Checklist.query.filter_by(name=list_name).first() is not None

def taskExists(list_name, task_name):
    if listExists(list_name) and Task.query.filter_by(name=task_name).first():
        return True

def doneListNames():
    done_lists = Checklist.query.filter_by(done=True)
    done_lists_names = [item.name for item in done_lists] 
    return done_lists_names

    map(append(item), done_lists)

def notDoneListNames():
    not_done_lists = Checklist.query.filter_by(done=False)
    not_done_list_names = [item.name for item in not_done_lists] 
    return not_done_list_names

def checkListDone(list_name):
    list_id = getListId(list_name)
    return Task.query.filter_by(list_id=list_id, done=False).count() == 0

def markDoneIfNeeded(list_name):
    if checkListDone(list_name):
        Checklist.query.filter_by(name=list_name).done = True
    return "Done!"
