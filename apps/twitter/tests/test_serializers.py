from django.test import TestCase
from django.contrib.auth.models import User
from twitter.serializers import UserRegistrationSerializer, LikeSerializer, FollowSerializer
from twitter.models import Post, Like, Follow

class UserRegistrationSerializerTest(TestCase):
    def setUp(self):
        self.user = User(
            username = 'testuser',
            email = 'testuser@example.com',
        )
        
        self.user_serializer = UserRegistrationSerializer(instance=self.user)
    
    def test_user_serializer_fields(self):
        """Test the fields of the UserRegistrationSerializer."""
        data = self.user_serializer.data
        self.assertEqual(set(data.keys()), set(['username', 'email']))
    
    def test_user_serializer_fields_content(self):
        """Test the content of the UserRegistrationSerializer fields."""
        data = self.user_serializer.data
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)


class LikeSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', email='testuser@example.com')
        self.post = Post.objects.create(user=self.user, title='Test Post', content='Test Content')
        self.like = Like(user=self.user, post=self.post)
        
        self.like_serializer = LikeSerializer(instance=self.like)
    
    def test_like_serializer_fields(self):
        """Test the fields of the LikeSerializer."""
        data = self.like_serializer.data
        self.assertEqual(set(data.keys()), set(['user', 'post', 'created_at']))
    
    def test_like_serializer_fields_content(self):
        """Test the content of the LikeSerializer fields."""
        data = self.like_serializer.data
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['post'], self.post.id)


class FollowSerializerTest(TestCase):
    def setUp(self):
        self.follower = User.objects.create(username='follower', email='follower@example.com')
        self.followed = User.objects.create(username='followed', email='followed@example.com')
        self.follow = Follow.objects.create(follower=self.follower, followed=self.followed)
        
        self.follow_serializer = FollowSerializer(instance=self.follow)
    
    def test_follow_serializer_fields(self):
        """Test the fields of the FollowSerializer."""
        data = self.follow_serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'follower', 'followed', 'created_at']))
    
    def test_follow_serializer_fields_content(self):
        """Test the content of the FollowSerializer fields."""
        data = self.follow_serializer.data
        self.assertEqual(data['follower']['username'], self.follower.username)
        self.assertEqual(data['follower']['email'], self.follower.email)
        self.assertEqual(data['followed'], self.followed.id)
