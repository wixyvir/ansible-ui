from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Host, Log
from .serializers import HostSerializer, LogSerializer, LogListSerializer


class LogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing logs.

    list: Get all logs (lightweight, without full host data)
    retrieve: Get a specific log with all hosts and plays
    hosts: Get all hosts for a specific log
    """

    queryset = Log.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return LogListSerializer
        return LogSerializer

    def get_queryset(self):
        queryset = Log.objects.all()
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("hosts__plays")
        return queryset

    @action(detail=True, methods=["get"])
    def hosts(self, request, pk=None):
        """
        List all hosts for a specific log.

        Returns:
            List of hosts with their plays for the specified log.
        """
        log = self.get_object()
        hosts = Host.objects.filter(log=log).prefetch_related("plays")
        serializer = HostSerializer(hosts, many=True)
        return Response(serializer.data)
