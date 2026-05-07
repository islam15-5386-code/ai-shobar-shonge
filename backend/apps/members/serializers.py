from rest_framework import serializers

from apps.tenants.models import TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = TeamMember
        fields = ['id', 'user', 'username', 'email', 'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'username', 'email']
