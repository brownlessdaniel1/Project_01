from flask import url_for
from flask_testing import TestCase
from application import app, db
from application.models import Checklist, Task

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
        db.create_all()
        test_list = Checklist(name="TestList")
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
        self.assertIn(b"Add tasks!", response.data)

    # Test task create
    def testCreateTask(self):
        response = self.client.post(
            url_for("editList", list_name="TestList"),
            data = dict(user_input="TestTask2"),
            follow_redirects=True
        )
        self.assertIn(b"task added!", response.data)

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
        # Test UPDATE
        # Lists - renameable.
        # tasks - tickable.


class TestDelete(TestBase):
    pass
    # Delete list -> Create Page.
    # Delete task -> edit list page.


class TestValidators(TestBase):
    # Validators for both list name and task name.
    pass


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
    

