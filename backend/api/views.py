from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Host, Log, Play
from .serializers import HostSerializer, LogCreateSerializer, LogSerializer
from .services.log_parser import LogParserService, determine_status


class LogViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    ViewSet for viewing and creating logs.

    create: Upload and parse a new Ansible log
    retrieve: Get a specific log with all hosts and plays
    hosts: Get all hosts for a specific log
    """

    queryset = Log.objects.all()
    serializer_class = LogSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return LogCreateSerializer
        return LogSerializer

    def get_queryset(self):
        return Log.objects.all().prefetch_related("hosts__plays")

    def create(self, request, *args, **kwargs):
        """
        Create a new log by uploading and parsing Ansible output.

        The log content is stored and parsed to extract hosts and plays.
        On success, returns the created log with all parsed data.
        On parsing failure, returns a 500 error with detailed information.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the log first to store raw content
        log = serializer.save()

        # Parse the log content
        parser_service = LogParserService()
        result = parser_service.parse(log.raw_content)

        if not result.success:
            # Delete the log on parsing failure
            log.delete()

            error_response = {
                "error": result.error or "Log parsing failed",
                "detail": result.detail or "Unknown parsing error",
                "raw_content_preview": log.raw_content[:500]
                if log.raw_content
                else None,
                "parser_type": result.parser_type,
            }

            if result.traceback_str:
                error_response["traceback"] = result.traceback_str

            return Response(
                error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Create Host and Play entities from parsed data
        for parsed_host in result.hosts:
            host = Host.objects.create(log=log, hostname=parsed_host.hostname)

            # Create a Play for each parsed play with line number and order
            for parsed_play in result.plays:
                Play.objects.create(
                    host=host,
                    name=parsed_play.name,
                    date=result.timestamp,
                    status=determine_status(parsed_host),
                    tasks_ok=parsed_host.ok,
                    tasks_changed=parsed_host.changed,
                    tasks_failed=parsed_host.failed,
                    line_number=parsed_play.line_number,
                    order=parsed_play.order,
                )

        # Refresh log to include newly created hosts and plays
        log.refresh_from_db()

        # Return the full log with nested hosts and plays
        output_serializer = LogSerializer(log)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

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
