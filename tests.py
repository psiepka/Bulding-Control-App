from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Company, Build, Employee, JobApp, Post


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password(self):
        u1 = User(nickname='userOne', name='Patryk', surname='Kowalski')
        u1.set_password('haslo123')
        self.assertFalse(u1.check_password('haslo321'))
        self.assertTrue(u1.check_password('haslo123'))

    def test_avatar(self):
        u1 = User(nickname='userOne', name='Patryk', surname='Kowalski', gender='male')
        u2 = User(nickname='userTwo', name='Maia', surname='Zahahara', email='druga@mail.com', gender='women')
        app.config['IMAGES'] = 'jpg'
        self.assertEqual(u1.avatar(), '..\\static\\img\\male.jpg')
        self.assertEqual(u2.avatar(), '..\\static\\img\\female.jpg')

    def test_users_follow(self):
        u1 = User(id=1, nickname='userOne', name='Patryk', surname='Kowalski', email='pierwszy@mail.com', gender='male')
        u2 = User(id=2, nickname='userTwo', name='Maia', surname='Zahahara', email='druga@mail.com', gender='women')
        db.session.add_all([u1, u2])
        db.session.commit()
        self.assertIsNotNone(User.query.filter_by(nickname='userOne'))
        u1.follow(u2)
        db.session.commit()
        self.assertEqual(u1.is_following(u2), True)
        self.assertEqual(u1.followers.count(), 0)
        self.assertEqual(u2.followers.count(), 1)

        u1.unfollow(u2)
        db.session.commit()
        self.assertEqual(u1.is_following(u2), False)
        self.assertEqual(u1.followers.count(), 0)
        self.assertEqual(u2.followers.count(), 0)
        self.assertEqual(u1.followers.all(), [])
        self.assertEqual(u1.followers.all(), [])


    def test_follow_posts(self):
        """
        Checking followers post, build posts, company, posts
        """
        now = datetime.utcnow()

        u1 = User(nickname='userOne', name='Ken', surname='Addams', email='pierwszy@mail.com', gender='male')
        u2 = User(nickname='userTwo', name='Regina', surname='Phalange', email='druga@mail.com', gender='women')
        u3 = User(nickname='userThree', name='Scrappy', surname='Coco', email='trzeci@mail.com', gender='male')

        db.session.add_all([u1, u2, u3])
        db.session.commit()


        p1 = Post(body='First post !', author=u1, timestamp = now)
        p2 = Post(body='Secound post !', author=u2, timestamp = now + timedelta(1))
        p3 = Post(body='Third post !', author=u3, timestamp = now + timedelta(2))
        p4 = Post(body='Fourth post !', author=u1, timestamp = now + timedelta(3))

        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        u1.follow(u2)
        u1.follow(u3)
        u2.follow(u3)
        db.session.commit()

        f1 = u1.followed_posts().count()
        f2 = u2.followed_posts().count()
        f3 = u3.followed_posts().count()

        self.assertEqual(f1, 4)
        self.assertEqual(f2, 2)
        self.assertEqual(f3, 1)


    def test_company_build_employee(self):
        u1 = User(nickname='userOne', name='Ken', surname='Addams', email='pierwszy@mail.com', gender='male')
        u2 = User(nickname='userTwo', name='Regina', surname='Phalange', email='druga@mail.com', gender='women')
        u3 = User(nickname='userThree', name='Scrappy', surname='Coco', email='trzeci@mail.com', gender='male')

        b1 = Build(name='Never ending build', specification='W trakcie', category='drogi, mosty, jelenie',
                    worth=15, place='Chrząszczyrzewoszyce', creater=u2)

        c1 = Company(name='Abibas')

        e1 = Employee(user=u2, firm=c1, admin=True, position='admin')
        e2 = Employee(user=u3, firm=c1, position='poziomek')

        db.session.add_all([u1, u2, u3, c1, b1, e1, e2])
        db.session.commit()

        self.assertEqual(u2.worker_id.company, c1.id)
        self.assertTrue(c1.is_working(u2))
        self.assertEqual(c1.number_workers(), 2)

        c1.add_build(b1)
        db.session.commit()

        self.assertEqual(c1.builds.count(), 1)
        self.assertEqual(b1.contractor, c1)

        c1.del_build(b1)
        db.session.commit()

        self.assertEqual(c1.builds.all(), [])
        self.assertIsNone(b1.contractor)

        p1 = Post(body='First post !', author=u1, build_forum=b1)
        p2 = Post(body='Secound post !', author=u2, build_forum=b1, private_company=True)
        p3 = Post(body='Third post !', author=u3, company_forum=c1)
        p4 = Post(body='Fourth post !', author=u3, company_forum=c1, private_company=True)

        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        b_post_pub = Post.query.filter_by(build_forum=b1, private_company=False).all()
        b_post_priv = Post.query.filter_by(build_forum=b1, private_company=False).all()
        self.assertEqual(len(b_post_pub), 1)
        self.assertEqual(len(b_post_priv), 1)

        self.assertFalse(e1.is_building(b1))

        e1.add_build(b1)
        db.session.commit()
        self.assertTrue(e1.is_building(b1))

        e1.del_build(b1)
        db.session.commit()
        self.assertFalse(e1.is_building(b1))

        self.assertEqual(len(u2.check_offer_user(u1).all()), 0)
        ap1 = JobApp(sender=e1, recipient=u1, salary=15, position='komandos', company_id=c1)
        ap1 = JobApp(sender=e2, recipient=u1, salary=12, position='specjalna', company_id=c1)
        db.session.add(ap1)
        db.session.commit()
        self.assertEqual(len(u2.check_offer_user(u1).all()), 2)
        self.assertEqual(len(u2.check_offer_user(u1).all()), len(u3.check_offer_user(u1).all()))


if __name__ == '__main__':
    unittest.main(verbosity=2)