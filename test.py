from unittest import TestCase
from app import app
from models import db, User

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True

db.drop_all()
db.create_all()

class BloglyTestCase(TestCase):
    def setUp(self):
        User.query.delete()
    
    def tearDown(self):
        db.session.rollback()

    def test_home(self):
        with app.test_client() as client:
            resp = client.get('/')
            self.assertEqual(resp.status_code, 302)

    def test_users(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1>Users</h1>", html)
            
    def test_add_user(self):
        with app.test_client() as client:
            resp = client.post('/users/new', data={'first_name':'Gumbo', 'last_name':'Smith', 'image_url' : 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.willowspringsdachshunds.com%2Four-standard-wirehaired-dachshunds&psig=AOvVaw2Ef5HRwuR8JE1BUPUTgeMH&ust=1703732054208000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCPjfotXOroMDFQAAAAAdAAAAABAD'})
            self.assertEqual(resp.status_code, 302)