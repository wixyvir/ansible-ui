from django.contrib import admin
from django.db.models import Count, Max, Q
from django.utils.html import format_html
from .models import Log, Host, Play


# Custom List Filters

class HasFailuresFilter(admin.SimpleListFilter):
    """Filter logs by whether they contain any failed plays."""
    title = 'has failures'
    parameter_name = 'has_failures'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Has Failures'),
            ('no', 'No Failures'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(hosts__plays__status='failed').distinct()
        if self.value() == 'no':
            return queryset.exclude(hosts__plays__status='failed').distinct()
        return queryset


class PlayStatusFilter(admin.SimpleListFilter):
    """Filter hosts by play status composition."""
    title = 'play status'
    parameter_name = 'play_status'

    def lookups(self, request, model_admin):
        return (
            ('failed', 'Has Failed Plays'),
            ('changed', 'Has Changed Plays'),
            ('ok', 'All OK'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'failed':
            return queryset.filter(plays__status='failed').distinct()
        if self.value() == 'changed':
            return queryset.filter(plays__status='changed').distinct()
        if self.value() == 'ok':
            return queryset.filter(plays__status='ok').exclude(
                Q(plays__status='changed') | Q(plays__status='failed')
            ).distinct()
        return queryset


class HasFailedTasksFilter(admin.SimpleListFilter):
    """Filter plays by whether they have failed tasks."""
    title = 'has failed tasks'
    parameter_name = 'has_failed_tasks'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Has Failed Tasks'),
            ('no', 'No Failed Tasks'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(tasks_failed__gt=0)
        if self.value() == 'no':
            return queryset.filter(tasks_failed=0)
        return queryset


class TaskCountRangeFilter(admin.SimpleListFilter):
    """Filter plays by total task count range."""
    title = 'task count'
    parameter_name = 'task_count'

    def lookups(self, request, model_admin):
        return (
            ('0-5', '0-5 tasks'),
            ('6-10', '6-10 tasks'),
            ('11-20', '11-20 tasks'),
            ('20+', '20+ tasks'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0-5':
            return queryset.filter(
                tasks_ok__lte=5,
                tasks_changed__lte=5,
                tasks_failed__lte=5
            )
        if self.value() == '6-10':
            return queryset.filter(
                tasks_ok__lte=10,
                tasks_changed__lte=10,
                tasks_failed__lte=10
            ).exclude(
                tasks_ok__lte=5,
                tasks_changed__lte=5,
                tasks_failed__lte=5
            )
        if self.value() == '11-20':
            return queryset.filter(
                tasks_ok__lte=20,
                tasks_changed__lte=20,
                tasks_failed__lte=20
            ).exclude(
                tasks_ok__lte=10,
                tasks_changed__lte=10,
                tasks_failed__lte=10
            )
        if self.value() == '20+':
            return queryset.filter(
                Q(tasks_ok__gt=20) | Q(tasks_changed__gt=20) | Q(tasks_failed__gt=20)
            )
        return queryset


# Inline Admin Classes

class HostInline(admin.TabularInline):
    """Inline admin for hosts within a log."""
    model = Host
    fields = ['hostname', 'play_count_display', 'created_at']
    readonly_fields = ['play_count_display', 'created_at']
    extra = 0
    can_delete = True

    def play_count_display(self, obj):
        """Display play count for inline host."""
        if obj.pk:
            count = obj.plays.count()
            return f"{count} play{'s' if count != 1 else ''}"
        return "-"
    play_count_display.short_description = "Plays"


class PlayInline(admin.TabularInline):
    """Inline admin for plays within a host."""
    model = Play
    fields = ['name', 'date', 'status', 'tasks_ok', 'tasks_changed', 'tasks_failed']
    extra = 0
    can_delete = True
    ordering = ['-date']


# Model Admin Classes

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    """Admin interface for Log model."""
    list_display = ['title', 'uploaded_at', 'host_count', 'total_plays', 'has_failures']
    list_filter = ['uploaded_at', HasFailuresFilter]
    search_fields = ['title', 'hosts__hostname']
    readonly_fields = ['uploaded_at', 'host_count', 'total_plays']
    date_hierarchy = 'uploaded_at'
    inlines = [HostInline]
    ordering = ['-uploaded_at']

    def get_queryset(self, request):
        """Optimize queryset with prefetch_related to avoid N+1 queries."""
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('hosts__plays')
        return qs

    def host_count(self, obj):
        """Display number of hosts in this log."""
        count = obj.hosts.count()
        return f"{count} host{'s' if count != 1 else ''}"
    host_count.short_description = "Hosts"

    def total_plays(self, obj):
        """Display total number of plays across all hosts."""
        total = sum(host.plays.count() for host in obj.hosts.all())
        return f"{total} play{'s' if total != 1 else ''}"
    total_plays.short_description = "Total Plays"

    def has_failures(self, obj):
        """Display visual indicator if any play failed."""
        has_failed = any(
            play.status == 'failed'
            for host in obj.hosts.all()
            for play in host.plays.all()
        )
        if has_failed:
            return format_html(
                '<span style="background: #7f1d1d; color: #ef4444; padding: 2px 8px; '
                'border-radius: 4px; font-weight: 600;">FAILED</span>'
            )
        return format_html(
            '<span style="background: #064e3b; color: #10b981; padding: 2px 8px; '
            'border-radius: 4px; font-weight: 600;">OK</span>'
        )
    has_failures.short_description = "Status"


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    """Admin interface for Host model."""
    list_display = ['hostname', 'log_title', 'play_count', 'status_summary', 'latest_play_date', 'created_at']
    list_filter = ['log', 'created_at', PlayStatusFilter]
    search_fields = ['hostname', 'log__title']
    readonly_fields = ['log', 'created_at', 'updated_at', 'play_count', 'status_summary']
    date_hierarchy = 'created_at'
    inlines = [PlayInline]
    ordering = ['hostname']

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        qs = super().get_queryset(request)
        qs = qs.select_related('log').prefetch_related('plays')
        return qs

    def log_title(self, obj):
        """Display log title with link."""
        return obj.log.title
    log_title.short_description = "Log"

    def play_count(self, obj):
        """Display number of plays on this host."""
        count = obj.plays.count()
        return f"{count} play{'s' if count != 1 else ''}"
    play_count.short_description = "Plays"

    def status_summary(self, obj):
        """Display visual summary of play statuses."""
        plays = obj.plays.all()
        ok_count = sum(1 for play in plays if play.status == 'ok')
        changed_count = sum(1 for play in plays if play.status == 'changed')
        failed_count = sum(1 for play in plays if play.status == 'failed')

        parts = []
        if ok_count > 0:
            parts.append(format_html(
                '<span style="background: #064e3b; color: #10b981; padding: 2px 6px; '
                'border-radius: 3px; margin-right: 4px; font-size: 11px;">{} OK</span>',
                ok_count
            ))
        if changed_count > 0:
            parts.append(format_html(
                '<span style="background: #713f12; color: #fbbf24; padding: 2px 6px; '
                'border-radius: 3px; margin-right: 4px; font-size: 11px;">{} CHG</span>',
                changed_count
            ))
        if failed_count > 0:
            parts.append(format_html(
                '<span style="background: #7f1d1d; color: #ef4444; padding: 2px 6px; '
                'border-radius: 3px; margin-right: 4px; font-size: 11px;">{} FAIL</span>',
                failed_count
            ))

        return format_html(''.join(str(part) for part in parts)) if parts else '-'
    status_summary.short_description = "Status Summary"

    def latest_play_date(self, obj):
        """Display most recent play execution date."""
        latest = obj.plays.order_by('-date').first()
        return latest.date if latest else '-'
    latest_play_date.short_description = "Latest Play"


@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    """Admin interface for Play model."""
    list_display = ['name', 'hostname', 'log_title', 'date', 'status_badge', 'task_summary', 'total_tasks']
    list_filter = ['status', 'date', 'host', 'host__log', HasFailedTasksFilter, TaskCountRangeFilter]
    search_fields = ['name', 'host__hostname', 'host__log__title']
    readonly_fields = ['host', 'created_at', 'updated_at', 'total_tasks']
    date_hierarchy = 'date'
    ordering = ['-date']
    fieldsets = [
        ('Play Information', {
            'fields': ['host', 'name', 'date', 'status']
        }),
        ('Task Summary', {
            'fields': ['tasks_ok', 'tasks_changed', 'tasks_failed', 'total_tasks']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        qs = qs.select_related('host__log')
        return qs

    def hostname(self, obj):
        """Display hostname."""
        return obj.host.hostname
    hostname.short_description = "Host"

    def log_title(self, obj):
        """Display log title."""
        return obj.host.log.title
    log_title.short_description = "Log"

    def status_badge(self, obj):
        """Display colored status badge."""
        colors = {
            'ok': {'bg': '#064e3b', 'fg': '#10b981', 'text': 'OK'},
            'changed': {'bg': '#713f12', 'fg': '#fbbf24', 'text': 'CHANGED'},
            'failed': {'bg': '#7f1d1d', 'fg': '#ef4444', 'text': 'FAILED'},
        }
        color = colors.get(obj.status, {'bg': '#333', 'fg': '#fff', 'text': obj.status.upper()})
        return format_html(
            '<span style="background: {}; color: {}; padding: 3px 10px; '
            'border-radius: 4px; font-weight: 600; font-size: 11px;">{}</span>',
            color['bg'], color['fg'], color['text']
        )
    status_badge.short_description = "Status"

    def task_summary(self, obj):
        """Display formatted task counts with colors."""
        parts = []
        if obj.tasks_ok > 0:
            parts.append(format_html(
                '<span style="color: #10b981; font-weight: 600;">OK: {}</span>',
                obj.tasks_ok
            ))
        if obj.tasks_changed > 0:
            parts.append(format_html(
                '<span style="color: #fbbf24; font-weight: 600;">CHG: {}</span>',
                obj.tasks_changed
            ))
        if obj.tasks_failed > 0:
            parts.append(format_html(
                '<span style="color: #ef4444; font-weight: 600;">FAIL: {}</span>',
                obj.tasks_failed
            ))

        return format_html(' | '.join(str(part) for part in parts)) if parts else '-'
    task_summary.short_description = "Task Summary"

    def total_tasks(self, obj):
        """Display total number of tasks."""
        return obj.tasks_ok + obj.tasks_changed + obj.tasks_failed
    total_tasks.short_description = "Total Tasks"


# Admin Site Customization
admin.site.site_header = "Ansible UI Administration"
admin.site.site_title = "Ansible UI Admin"
admin.site.index_title = "Manage Ansible Execution Logs"
