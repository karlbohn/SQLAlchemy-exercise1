from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

"""Models for Blogly."""
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, default="https://www.shutterstock.com/image-vector/user-profile-icon-vector-avatar-600nw-2247726673.jpg")
    
    @property
    def full_name(self):
        """Returns user's name"""
        return f'{self.first_name} {self.last_name}'
    
def connect_db(app):
    """Connects database to Flask app"""
    
    db.app = app
    db.init_app(app)