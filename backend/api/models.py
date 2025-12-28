import uuid
from django.db import models


class Log(models.Model):
    """Represents an Ansible log file uploaded by the frontend."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    raw_content = models.TextField(blank=True, help_text="Raw log file content")

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Log"
        verbose_name_plural = "Logs"

    def __str__(self):
        return f"{self.title} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"


class Host(models.Model):
    """Represents a server/host that Ansible plays are executed on."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    log = models.ForeignKey(Log, on_delete=models.CASCADE, related_name="hosts")
    hostname = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["hostname"]
        verbose_name = "Host"
        verbose_name_plural = "Hosts"
        unique_together = [["log", "hostname"]]

    def __str__(self):
        return f"{self.hostname} (Log: {self.log.title})"


class Play(models.Model):
    """Represents a single Ansible play execution on a host."""

    STATUS_CHOICES = [
        ("ok", "OK"),
        ("changed", "Changed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name="plays")
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, db_index=True)

    # Task summary fields
    tasks_ok = models.IntegerField(default=0)
    tasks_changed = models.IntegerField(default=0)
    tasks_failed = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Play"
        verbose_name_plural = "Plays"
        indexes = [
            models.Index(fields=["host", "-date"]),
            models.Index(fields=["status", "-date"]),
        ]

    def __str__(self):
        return f"{self.name} on {self.host.hostname} ({self.status})"

    @property
    def tasks(self):
        """Return task summary dict matching frontend TaskSummary interface."""
        return {
            "ok": self.tasks_ok,
            "changed": self.tasks_changed,
            "failed": self.tasks_failed,
        }
