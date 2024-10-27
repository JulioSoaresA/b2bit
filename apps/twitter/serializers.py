from rest_framework import serializers
from .models import Post, Like, Follow
from users.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    # Validação de campos obrigatórios
    def validate_title(self, value):
        if len(value) > 255:
            raise serializers.ValidationError("Title cannot be longer than 255 characters.")
        return value

    def validate_content(self, value):
        if len(value) > 500:
            raise serializers.ValidationError("Content cannot be longer than 500 characters.")
        return value

    # Validação para a imagem (se for enviada)
    def validate_image(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:  # Limite de 5MB
                raise serializers.ValidationError("Image file size should not exceed 5MB.")
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("Uploaded file must be an image.")
        return value


class PostListSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    likes_count = serializers.IntegerField()


    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content', 'image', 'created_at', 'likes_count']
        read_only_fields = ['id', 'created_at', 'likes_count']


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Like
        fields = ['user', 'post', 'created_at']
        read_only_fields = ['created_at']

class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'created_at']


class FollowedListSerializer(serializers.ModelSerializer):
    followed_username = serializers.CharField(source='followed.username', read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'followed_username', 'created_at']


class FollowerListSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source='follower.username', read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower_username', 'created_at']