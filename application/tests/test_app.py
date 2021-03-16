from flask import url_for
from flask_testing import TestCase
from application import app, db
from application.models import Checklist, Task

class TestBase(TestCase):
    def create_app(self):
        app.config.update(
            SQLALCHEMY_DATABASE_URI="sqlite:///",
            SECRET_KEY="TEST_KEY",
            DEBUG=True,
            WTF_CSRF_ENABLED=False
        )
        return app
    
    def setUp(self):
        db.create_all()
        test_list = Checklist(name="TestList")
        db.session.add(test_list)
        test_task = Task(name="TestTask")
        db.session.add(test_task)
        db.session.commit()

    def tearDown(self):
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
        self.assertIn(b"list added!", response.data)

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

class TestRobustDynamicLists
    # Tests to ensure that redirect methods for delete and edit pages
    # can't be fooled by non-existent items.

class TestRoutes(TestBase):
    #Test200 for all routes.
