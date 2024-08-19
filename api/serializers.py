from rest_framework import serializers
from .models import Message, UserData

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['message', 'url', 'date', 'is_read']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ['id', 'auth_user_id', 'user_email', 'first_name', 'last_name']

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance