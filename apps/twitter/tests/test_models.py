from django.test import TestCase
from django.contrib.auth.models import User
from twitter.models import Post, Like, Follow


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@gmail.com', password='password')
        self.post = Post.objects.create(user=self.user, title='Test Post', content='This is a test post content.', image='core/static/posts/img/default.jpg')

    def test_post_creation(self):
        """Test that a Post object is created correctly."""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is a test post content.')
        self.assertEqual(self.post.image, 'core/static/posts/img/default.jpg')
        self.assertEqual(self.post.user.username, 'testuser')

    def test_post_string_representation(self):
        """Test the string representation of the Post model."""
        self.assertEqual(str(self.post), 'Test Post')

    def test_get_likes_count(self):
        """Test the `get_likes_count` method of Post model."""
        self.assertEqual(self.post.get_likes_count(), 0)
        Like.objects.create(user=self.user, post=self.post)
        self.assertEqual(self.post.get_likes_count(), 1)


class LikeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@gmail.com', password='password')
        self.post = Post.objects.create(user=self.user, title='Test Post', content='This is a test post content.')
        self.like = Like.objects.create(user=self.user, post=self.post)

    def test_like_creation(self):
        """Test that a Like object is created correctly."""
        self.assertEqual(self.like.user.username, 'testuser')
        self.assertEqual(self.like.post.title, 'Test Post')

    def test_like_string_representation(self):
        """Test the string representation of the Like model."""
        self.assertEqual(str(self.like), 'testuser likes This is a test post content.')

    def test_like_and_remove_like_post(self):
        """Test that liking a post increases the like count and removing a like decreases the like count."""
        like = Like.objects.create(user=self.user, post=self.post)
        self.assertEqual(Like.objects.count(), 2)
        
        # Test that liking a post increases the like count
        self.assertEqual(self.post.get_likes_count(), 2)
        
        # Test that like is removed
        like.delete()
        self.assertEqual(Like.objects.count(), 1)
        
        # Test that like count is decreased
        self.assertEqual(self.post.get_likes_count(), 1)
        


class FollowModelTest(TestCase):
    def setUp(self):
        self.follower = User.objects.create_user(username='follower', email='follower@gmail.com', password='password')
        self.followed = User.objects.create_user(username='followed', email='followed@gmail.com', password='password')
        self.follow = Follow.objects.create(follower=self.follower, followed=self.followed)

    def test_follow_creation(self):
        """Test that a Follow object is created correctly."""
        self.assertEqual(self.follow.follower.username, 'follower')
        self.assertEqual(self.follow.followed.username, 'followed')

    def test_follow_string_representation(self):
        """Test the string representation of the Follow model."""
        self.assertEqual(str(self.follow), 'follower follows followed')
    
    def test_follow_unfollow_user(self):
        """Test that following a user increases the follow count and unfollowing decreases the follow count."""
        follow = Follow.objects.create(follower=self.follower, followed=self.followed)
        self.assertEqual(Follow.objects.count(), 2)
        
        # Test that unfollowing decreases the follow count
        follow.delete()
        self.assertEqual(Follow.objects.count(), 1)