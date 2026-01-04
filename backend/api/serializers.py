from rest_framework import serializers
from .models import Log, Host, Play


class TaskSummarySerializer(serializers.Serializer):
    """Serializer for task summary matching the frontend TaskSummary interface."""

    ok = serializers.IntegerField()
    changed = serializers.IntegerField()
    failed = serializers.IntegerField()


class PlaySerializer(serializers.ModelSerializer):
    """Serializer for Play model matching the frontend Play interface."""

    tasks = TaskSummarySerializer(read_only=True)

    class Meta:
        model = Play
        fields = ["id", "name", "date", "status", "tasks", "line_number", "order"]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        """Convert datetime to ISO string format for frontend compatibility."""
        representation = super().to_representation(instance)
        # Ensure date is in ISO format (YYYY-MM-DDTHH:MM:SS)
        if representation.get("date"):
            representation["date"] = instance.date.isoformat()
        return representation


class HostSerializer(serializers.ModelSerializer):
    """Serializer for Host model matching the frontend Host interface."""

    plays = PlaySerializer(many=True, read_only=True)

    class Meta:
        model = Host
        fields = ["id", "hostname", "plays"]
        read_only_fields = ["id"]


class HostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing hosts without plays."""

    play_count = serializers.IntegerField(source="plays.count", read_only=True)

    class Meta:
        model = Host
        fields = ["id", "hostname", "play_count"]
        read_only_fields = ["id"]


class PlayCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating plays with nested task summary data."""

    tasks_ok = serializers.IntegerField(min_value=0, default=0)
    tasks_changed = serializers.IntegerField(min_value=0, default=0)
    tasks_failed = serializers.IntegerField(min_value=0, default=0)

    class Meta:
        model = Play
        fields = ["name", "date", "status", "tasks_ok", "tasks_changed", "tasks_failed"]

    def validate_status(self, value):
        """Ensure status is one of the valid choices."""
        valid_statuses = ["ok", "changed", "failed"]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_statuses)}"
            )
        return value


class LogSerializer(serializers.ModelSerializer):
    """Serializer for Log model with nested hosts."""

    hosts = HostSerializer(many=True, read_only=True)
    host_count = serializers.IntegerField(source="hosts.count", read_only=True)

    class Meta:
        model = Log
        fields = ["id", "title", "uploaded_at", "hosts", "host_count"]
        read_only_fields = ["id", "uploaded_at"]


class LogListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing logs without full host data."""

    host_count = serializers.IntegerField(source="hosts.count", read_only=True)

    class Meta:
        model = Log
        fields = ["id", "title", "uploaded_at", "host_count"]
        read_only_fields = ["id", "uploaded_at"]


class LogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/uploading logs."""

    class Meta:
        model = Log
        fields = ["title", "raw_content"]

    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()
