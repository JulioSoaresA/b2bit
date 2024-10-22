from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Like, Follow


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # Remover o campo password2, pois não faz parte do modelo
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined')


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
    likes_count = serializers.SerializerMethodField()


    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content', 'image', 'created_at', 'likes_count']
        read_only_fields = ['id', 'created_at', 'likes_count']
    
    def get_likes_count(self, obj):
        return obj.get_likes_count()


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