from datetime import datetime
import unittest
from hashlib import md5

from app import app, db
from app.models import Post, User


class UserModelCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hash(self):
        user = User(username='susan', email='susan@example.com')
        user.set_password('cat')
        self.assertTrue(user.check_password('cat'))
        self.assertFalse(user.check_password('dog'))

    def test_avatar(self):
        user = User(username='susan', email='susan@example.com')
        digest = md5(user.email.lower().encode('utf-8')).hexdigest()
        self.assertEqual(
            user.avatar(128),
            f'https://www.gravatar.com/avatar/{digest}?d=identicon&s=128')

    def test_follow_and_unfollow(self):
        follower = User(username='john', email='john@example.com')
        followed = User(username='susan', email='susan@example.com')
        db.session.add_all([follower, followed])
        db.session.commit()

        follower.follow(followed)
        follower.follow(followed)
        db.session.commit()
        self.assertTrue(follower.is_following(followed))
        self.assertEqual(followed.followers.count(), 1)

        follower.unfollow(followed)
        follower.unfollow(followed)
        db.session.commit()
        self.assertFalse(follower.is_following(followed))
        self.assertEqual(followed.followers.count(), 0)

    def test_followed_posts(self):
        follower = User(username='john', email='john@example.com')
        followed = User(username='susan', email='susan@example.com')
        unrelated = User(username='mary', email='mary@example.com')
        db.session.add_all([follower, followed, unrelated])
        db.session.commit()
        follower.follow(followed)

        own_post = Post(
            body='Own post', author=follower,
            timestamp=datetime(2024, 1, 1))
        followed_post = Post(
            body='Followed post', author=followed,
            timestamp=datetime(2024, 1, 2))
        unrelated_post = Post(
            body='Unrelated post', author=unrelated,
            timestamp=datetime(2024, 1, 3))
        db.session.add_all([own_post, followed_post, unrelated_post])
        db.session.commit()

        self.assertEqual(
            follower.followed_posts().all(), [followed_post, own_post])


if __name__ == '__main__':
    unittest.main()
