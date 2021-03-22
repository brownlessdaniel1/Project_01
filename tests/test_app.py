from flask import url_for
from flask_testing import TestCase
from application import app, db
from application.models import Checklist, Task
from datetime import datetime

class TestBase(TestCase):
    def create_app(self):                                   # Pre every test
        app.config.update(
            SQLALCHEMY_DATABASE_URI="sqlite:///",
            SECRET_KEY="TEST_KEY",
            DEBUG=True,
            WTF_CSRF_ENABLED=False
        )
        return app

    def setUp(self):                                        # Pre test
        date_raw = datetime.today()
        date = date_raw.strftime("%Y-%m-%d")
        self.date_string = str(date).encode("ascii")
        db.create_all()
        test_list = Checklist(name="TestList")
        self.test_list_id = 1
        db.session.add(test_list)
        db.session.commit()
        test_task = Task(name="TestTask", list_id="1")
        db.session.add(test_task)
        db.session.commit()

    def tearDown(self):                                     # Post test

        db.session.remove()
        db.drop_all()


class TestCreate(TestBase):

    # Test list create works.
    def testCreateList(self):
        response = self.client.post(
            url_for("home"),
            data = dict(user_input="NewList"),
            follow_redirects=True
        )
        self.assertTrue(Checklist.query.filter_by(name="NewList").first())
    
    def testCreateDate(self):
        response = self.client.get(url_for("home", list_name="NewList"), follow_redirects=True)
        self.assertIn(self.date_string, response.data)    

    # Test task create
    def testCreateTask(self):
        response = self.client.post(
            url_for("editList", list_name="TestList"),
            data = dict(user_input="NewTask"),
            follow_redirects=True
        )
        self.assertTrue(Task.query.filter_by(name="NewTask").first())


class TestRead(TestBase):
    # Test read new list.
    def testReadList(self):
        response = self.client.get(url_for("home"), follow_redirects=True)
        self.assertIn(b"TestList", response.data)

    # Test read new task
    def testReadTask(self):
        response = self.client.get(url_for("editList", list_name="TestList"), follow_redirects=True)
        self.assertIn(b"TestTask", response.data)


class TestUpdate(TestBase):
    pass

    # test that rename list works.
    def testRenameListUpdate(self):
        response = self.client.post(
            url_for("renameList", list_name="TestList"),
            data = dict(user_input="NewListName"),
            follow_redirects=True
        )
        self.assertIn(b"NewListName!", response.data)

    # test renamed list corresponds to same list_id
    def testRenameListUpdate(self):
        response = self.client.post(
            url_for("renameList", list_name="TestList"),
            data = dict(user_input="NewListName"),
            follow_redirects=True
        )
        self.assertEqual(self.test_list_id, Checklist.query.filter_by(name="NewListName").first().id)

    # Test that mark done -> date now in page.
    def testMarkDoneList(self):
        self.client.get(url_for("markDoneList", list_name="TestList"), follow_redirects=True)
        self.assertEqual(True, Checklist.query.filter_by(name="TestList").first().done)   
    
    def testMarkDoneListVisualResponse(self):
        response = self.client.get(url_for("markDoneList", list_name="TestList"), follow_redirects=True)
        self.assert200(response)
 

    # test that mark not done -> date now not in page / "-" in page
    def testMarkNotDoneList(self):
        Checklist.query.filter_by(name="TestList").first().done = True
        response = self.client.get(url_for("markNotDoneList", list_name="TestList"), follow_redirects=True)
        self.assertEqual(False, Checklist.query.filter_by(name="TestList").first().done)   

    def testMarkNotDoneListVisualResponse(self):
        Checklist.query.filter_by(name="TestList").first().done = True
        response = self.client.get(url_for("markNotDoneList", list_name="TestList"), follow_redirects=True)
        self.assertIn(b"-", response.data)

    def testMarkDoneTask(self):
        self.client.get(url_for("markDoneTask", list_name="TestList", task_name="TestTask"), follow_redirects=True)
        self.assertEqual(True, Task.query.filter_by(name="TestTask").first().done)
    
    def testMarkNotDoneTask(self):
        Task.query.filter_by(name="TestTask").first().done = True
        response = self.client.get(url_for("markNotDoneTask", list_name="TestList", task_name="TestTask"), follow_redirects=True)
        self.assertEqual(False, Task.query.filter_by(name="TestTask").first().done)


    # mark done list -> mark done tasks
    def testMarkDoneListMarksTasks(self):
        response = self.client.get(url_for("markDoneList", list_name="TestList"), follow_redirects=True)
        self.assertEqual(True, Task.query.filter_by(list_id=self.test_list_id).first().done)


    # mark done all tasks -> mark done list
    def testMarkDoneTasksMarksList(self):
        Task.query.filter_by(name="TestTask").first().done = False
        self.client.get(url_for("markDoneTask", list_name="TestList", task_name="TestTask"))
        self.assertEqual(True, Checklist.query.filter_by(name="TestList").first().done)
    

    # mark done list + not mark done all tasks -> mark not done list.
    def testMarkNotAllTasksDoneMarksNotDoneList(self):
        Task.query.filter_by(name="TestTask").first().done = True
        self.client.get(url_for("markNotDoneTask", list_name="TestList", task_name="TestTask"))
        self.assertEqual(False, Checklist.query.filter_by(name="TestList").first().done)


class TestDelete(TestBase):
    # Delete list -> Create Page.
    def testDeleteList(self):
        response = self.client.get(url_for("deleteList", list_name="TestList"), follow_redirects=True)
        self.assertFalse(Checklist.query.filter_by(name="TestList").first())

    # Delete task -> edit list page.
    def testDeleteTask(self):
        response = self.client.get(url_for("deleteTask", list_name="TestList", task_name="TestTask"), follow_redirects=True)
        self.assertFalse(Task.query.filter_by(name="TestTask").first())


class TestValidators(TestBase):

    # Test list available name check validator.
    def testAvailableNameCheckValidator(self):
        response = self.client.post(
            url_for("home"),
            data = dict(user_input="TestList"),
            follow_redirects=True
        )
        self.assertIn(b"That name is already in use. Please use another.", response.data)

    # Test list restricted word check validator
    def testRestrictedWordCheckValidator(self):
        response = self.client.post(
            url_for("home"),
            data = dict(user_input="admin"),
            follow_redirects=True
        )
        self.assertIn(b"Invalid name - please try another!", response.data)

    # Test list name special character check validator
    def testSpecialCharacterCheckValidator(self):
        response = self.client.post(
            url_for("home"),
            data = dict(user_input="special_characters!"),
            follow_redirects=True
        )
        self.assertIn(b"Input cannot include special characters", response.data)
    
    # Test list name min length validator
    def testMinLengthValidator(self):
        response = self.client.post(
            url_for("home"),
            data = dict(user_input="  "),
            follow_redirects=True
        )
        self.assertIn(b"This field is required.", response.data)

    # Test list name max length validator
    def testMaxLengthValidator(self):
        response = self.client.post(
            url_for("home"),
            data = dict(user_input="this string is more than twenty characters long"),
            follow_redirects=True
        )
        self.assertIn(b"Field cannot be longer than 20 characters.", response.data)


class testRobustDynamicLinks(TestBase):

    # Test robustness of /edit/<list_name>
    def testRobustEdit(self):
        response = self.client.get(url_for("editList", list_name="NonexistentList"))
        self.assertIn(url_for("home"), response.location)

    def testRobustRenameList(self):
        response = self.client.get(url_for("renameList", list_name="NonexistentList"))
        self.assertIn(url_for("home"), response.location)

    def testRobustMarkDoneList(self):
        response = self.client.get(url_for("markDoneList", list_name="NonexistentList"))
        self.assertIn(url_for("home"), response.location)
    
    def testRobustMarkNotDoneList(self):
        response = self.client.get(url_for("markNotDoneList", list_name="NonexistentList"))
        self.assertIn(url_for("home"), response.location)

    def testRobustMarkDoneTask(self):
        response = self.client.get(url_for("markDoneTask", list_name="NonexistentList", task_name="NonexistentTask"))
        self.assertIn(url_for("home"), response.location)

    def testRobustMarkNotDoneTask(self):
        response = self.client.get(url_for("markNotDoneTask", list_name="NonexistentList", task_name="NonexistentTask"))
        self.assertIn(url_for("home"), response.location)


    def testRobustDeleteList(self):
        response = self.client.get(url_for("deleteList", list_name="NonexistentList"))
        self.assertIn(url_for("home"), response.location)

    def testRobustDeleteTask(self):
        response = self.client.get(url_for("deleteTask", list_name="TestList", task_name="NonexistentTask"))
        self.assertIn(url_for("home"), response.location)


class TestRoutes(TestBase):
    def testHomeGet200(self):
        response = self.client.get(url_for("home"))
        self.assert200(response)

    def testEditListGet200(self):
        response = self.client.get(url_for("editList", list_name="TestList"))
        self.assert200(response)

    def testRenameList200(self):
        response = self.client.get(url_for("renameList", list_name="TestList"))
        self.assert200(response)

    def testMarkDoneList302(self):
        response = self.client.get(url_for("markDoneList", list_name="TestList"))
        self.assertEqual(302, response.status_code)

    def testMarkNotDoneList302(self):
        response = self.client.get(url_for("markNotDoneList", list_name="TestList"))
        self.assertEqual(302, response.status_code)
    
    def testMarkDoneTask302(self):
        response = self.client.get(url_for("markDoneTask", list_name="TestList", task_name="TestTask"))
        self.assertEqual(302, response.status_code)

    def testMarkNotDoneTask302(self):
        response = self.client.get(url_for("markNotDoneTask", list_name="TestList", task_name="TestTask"))
        self.assertEqual(302, response.status_code)
    
    def testDeleteListGet302(self):
        response = self.client.get(url_for("deleteList", list_name="TestList"))
        self.assertEqual(302, response.status_code)
    
    def testDeleteTaskGet302(self):
        response = self.client.get(url_for("deleteTask", list_name="TestList", task_name="TestTask"))
        self.assertEqual(302, response.status_code)
