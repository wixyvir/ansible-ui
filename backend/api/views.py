from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins, viewsets

from .models import Host, Log
from .serializers import HostSerializer, LogSerializer


class LogViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for viewing logs.

    retrieve: Get a specific log with all hosts and plays
    hosts: Get all hosts for a specific log
    """

    queryset = Log.objects.all()
    serializer_class = LogSerializer

    def get_queryset(self):
        return Log.objects.all().prefetch_related("hosts__plays")

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
