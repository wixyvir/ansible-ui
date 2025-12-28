"""
Django management command to populate the database with realistic mock Ansible execution data.

Usage:
    python manage.py populate_mock_data                    # Default: 5 logs, 25 hosts, 250 plays
    python manage.py populate_mock_data --clear            # Clear existing data first
    python manage.py populate_mock_data --logs 10          # Custom quantities
"""

import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Log, Host, Play


# Data pools for generating realistic mock data
ENVIRONMENTS = ['prod', 'staging', 'dev']
SERVICES = ['web', 'db', 'cache', 'lb', 'app', 'worker', 'api', 'queue']
LOCATIONS = ['us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1', 'ap-south-1']

LOG_TITLES = [
    "Production Web Server Deployment",
    "Database Maintenance and Backup",
    "Security Patches and Updates",
    "Application Configuration Update",
    "Load Balancer Health Check",
    "Cache Server Optimization",
    "Monitoring Agent Installation",
    "SSL Certificate Renewal",
    "Docker Container Updates",
    "Kubernetes Cluster Maintenance",
    "System Package Upgrades",
    "Application Log Rotation Setup",
    "Firewall Rules Configuration",
    "Database Replication Setup",
    "Web Server Performance Tuning",
    "API Gateway Configuration",
    "Message Queue Deployment",
    "Backup System Verification",
    "Network Security Audit",
    "Container Registry Migration",
]

PLAY_NAMES = {
    'system_setup': [
        "Install required system packages",
        "Configure system timezone and locale",
        "Setup system users and groups",
        "Configure firewall rules",
        "Update system kernel parameters",
        "Configure system hostname",
        "Setup NTP time synchronization",
        "Configure system logging",
    ],
    'package_management': [
        "Install Python dependencies",
        "Install Node.js and npm",
        "Install database client libraries",
        "Update package cache",
        "Remove obsolete packages",
        "Install build tools",
        "Install runtime libraries",
        "Configure package repositories",
    ],
    'service_configuration': [
        "Configure Nginx web server",
        "Setup PostgreSQL database",
        "Configure Redis cache server",
        "Setup Apache web server",
        "Configure MySQL database",
        "Setup Memcached service",
        "Configure HAProxy load balancer",
        "Setup RabbitMQ message broker",
    ],
    'application_deployment': [
        "Deploy application code",
        "Run database migrations",
        "Compile static assets",
        "Update application configuration",
        "Restart application services",
        "Deploy API services",
        "Update environment variables",
        "Build application containers",
    ],
    'security': [
        "Configure SSH security settings",
        "Setup SSL/TLS certificates",
        "Configure security groups",
        "Setup fail2ban",
        "Configure SELinux policies",
        "Update security patches",
        "Configure encryption keys",
        "Setup authentication services",
    ],
    'monitoring': [
        "Install monitoring agents",
        "Configure log rotation",
        "Setup system health checks",
        "Configure metrics collection",
        "Setup alerting rules",
        "Deploy logging infrastructure",
        "Configure APM agents",
        "Setup uptime monitoring",
    ],
    'file_management': [
        "Deploy configuration templates",
        "Update environment variables",
        "Backup configuration files",
        "Sync files from repository",
        "Clean up temporary files",
        "Deploy application assets",
        "Update configuration files",
        "Archive old log files",
    ],
}


class Command(BaseCommand):
    help = "Populate database with realistic mock Ansible execution data"

    def add_arguments(self, parser):
        """Define command-line arguments."""
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing data before populating'
        )
        parser.add_argument(
            '--logs',
            type=int,
            default=5,
            help='Number of logs to create (default: 5)'
        )
        parser.add_argument(
            '--hosts-per-log',
            type=int,
            default=5,
            help='Number of hosts per log (default: 5)'
        )
        parser.add_argument(
            '--plays-per-host',
            type=int,
            default=10,
            help='Number of plays per host (default: 10)'
        )

    def handle(self, *args, **options):
        """Main command handler."""
        # Parse options
        clear_data = options['clear']
        num_logs = options['logs']
        hosts_per_log = options['hosts_per_log']
        plays_per_host = options['plays_per_host']

        # Clear existing data if requested
        if clear_data:
            self.clear_existing_data()

        # Generate mock data
        self.stdout.write(self.style.HTTP_INFO("\nCreating mock Ansible execution data...\n"))
        stats = self.populate_mock_data(num_logs, hosts_per_log, plays_per_host)

        # Display summary
        self.display_summary(stats)

    def clear_existing_data(self):
        """Delete all existing logs, hosts, and plays."""
        log_count = Log.objects.count()
        host_count = Host.objects.count()
        play_count = Play.objects.count()

        if log_count == 0 and host_count == 0 and play_count == 0:
            self.stdout.write(self.style.WARNING("No existing data to clear.\n"))
            return

        self.stdout.write(self.style.WARNING("\nClearing existing data..."))
        Log.objects.all().delete()  # Cascade deletes hosts and plays
        self.stdout.write(
            self.style.SUCCESS(
                f"  Deleted {log_count} logs, {host_count} hosts, {play_count} plays\n"
            )
        )

    def generate_hostname(self, used_names):
        """Generate a unique realistic hostname within the current log."""
        max_attempts = 100
        for _ in range(max_attempts):
            environment = random.choice(ENVIRONMENTS)
            service = random.choice(SERVICES)
            location = random.choice(LOCATIONS)
            number = random.randint(1, 99)
            hostname = f"{environment}-{service}-{location}-{number:02d}"

            if hostname not in used_names:
                return hostname

        # Fallback: append random suffix to ensure uniqueness
        base = f"{random.choice(ENVIRONMENTS)}-{random.choice(SERVICES)}"
        return f"{base}-{random.randint(1000, 9999)}"

    def generate_log_title(self, used_titles):
        """Select a random log title, avoiding duplicates if possible."""
        available_titles = [t for t in LOG_TITLES if t not in used_titles]
        if available_titles:
            return random.choice(available_titles)
        # If all titles used, pick any title
        return random.choice(LOG_TITLES)

    def generate_play_name(self, used_names=None):
        """Select a random play name from categorized pools."""
        # Flatten all play names from all categories
        all_plays = []
        for category_plays in PLAY_NAMES.values():
            all_plays.extend(category_plays)

        # Try to avoid recently used names for variety
        if used_names and len(used_names) < len(all_plays) * 0.7:
            available_plays = [p for p in all_plays if p not in used_names]
            if available_plays:
                return random.choice(available_plays)

        return random.choice(all_plays)

    def generate_task_counts(self, status):
        """Generate realistic task counts based on play status."""
        if status == 'failed':
            # Failed plays: some successful tasks, few changed, at least 1 failed
            tasks_ok = random.randint(0, 8)
            tasks_changed = random.randint(0, 3)
            tasks_failed = random.randint(1, 5)
        elif status == 'changed':
            # Changed plays: mix of ok and changed tasks, no failures
            tasks_ok = random.randint(3, 12)
            tasks_changed = random.randint(1, 8)
            tasks_failed = 0
        else:  # status == 'ok'
            # OK plays: all tasks ok, no changes or failures
            tasks_ok = random.randint(5, 18)
            tasks_changed = 0
            tasks_failed = 0

        return tasks_ok, tasks_changed, tasks_failed

    def get_weighted_status(self):
        """Return a play status with realistic distribution."""
        # 60% OK, 30% Changed, 10% Failed
        statuses = ['ok', 'changed', 'failed']
        weights = [0.6, 0.3, 0.1]
        return random.choices(statuses, weights=weights)[0]

    def generate_play_date(self, base_time, offset_minutes):
        """Generate a timestamp for a play based on offset from base time."""
        # Add offset in minutes with some randomness (30s to 5min between plays)
        offset_seconds = offset_minutes * 60 + random.randint(30, 300)
        return base_time + timedelta(seconds=offset_seconds)

    def create_log(self, title, base_date):
        """Create and return a Log instance."""
        return Log.objects.create(
            title=title,
            uploaded_at=base_date,
            raw_content=f"Mock Ansible log for: {title}"
        )

    def create_host(self, log, hostname):
        """Create and return a Host instance."""
        return Host.objects.create(
            log=log,
            hostname=hostname
        )

    def create_play(self, host, name, date, status, tasks):
        """Create and return a Play instance."""
        tasks_ok, tasks_changed, tasks_failed = tasks
        return Play.objects.create(
            host=host,
            name=name,
            date=date,
            status=status,
            tasks_ok=tasks_ok,
            tasks_changed=tasks_changed,
            tasks_failed=tasks_failed
        )

    def populate_mock_data(self, num_logs, hosts_per_log, plays_per_host):
        """Generate and populate mock data."""
        stats = {
            'logs': 0,
            'hosts': 0,
            'plays': 0,
            'ok_plays': 0,
            'changed_plays': 0,
            'failed_plays': 0,
        }

        used_log_titles = set()
        now = timezone.now()

        # Generate logs
        for log_idx in range(num_logs):
            # Generate log with timestamp spread across last 30 days
            days_ago = random.randint(0, 30)
            log_date = now - timedelta(days=days_ago)
            log_title = self.generate_log_title(used_log_titles)
            used_log_titles.add(log_title)

            log = self.create_log(log_title, log_date)
            stats['logs'] += 1

            # Display log creation
            date_str = log_date.strftime('%Y-%m-%d %H:%M:%S')
            self.stdout.write(
                self.style.HTTP_INFO(f"\n[LOG {log_idx + 1}/{num_logs}] ")
                + self.style.SUCCESS(f"{log_title} ")
                + self.style.WARNING(f"({date_str})")
            )

            # Generate hosts for this log
            used_hostnames = set()
            for host_idx in range(hosts_per_log):
                hostname = self.generate_hostname(used_hostnames)
                used_hostnames.add(hostname)

                host = self.create_host(log, hostname)
                stats['hosts'] += 1

                # Track play status counts for this host
                host_ok = 0
                host_changed = 0
                host_failed = 0

                # Generate plays for this host
                used_play_names = set()
                base_play_time = log_date

                for play_idx in range(plays_per_host):
                    play_name = self.generate_play_name(used_play_names)
                    used_play_names.add(play_name)

                    status = self.get_weighted_status()
                    tasks = self.generate_task_counts(status)
                    play_date = self.generate_play_date(base_play_time, play_idx * 2)

                    self.create_play(host, play_name, play_date, status, tasks)
                    stats['plays'] += 1

                    # Track status counts
                    if status == 'ok':
                        stats['ok_plays'] += 1
                        host_ok += 1
                    elif status == 'changed':
                        stats['changed_plays'] += 1
                        host_changed += 1
                    else:  # failed
                        stats['failed_plays'] += 1
                        host_failed += 1

                # Display host completion with play summary
                self.stdout.write(
                    f"  [HOST {host_idx + 1}/{hosts_per_log}] "
                    + self.style.HTTP_INFO(f"{hostname}")
                )
                self.stdout.write(
                    f"    Created {plays_per_host} plays: "
                    + self.style.SUCCESS(f"{host_ok} OK")
                    + ", "
                    + self.style.WARNING(f"{host_changed} Changed")
                    + ", "
                    + self.style.ERROR(f"{host_failed} Failed")
                )

        return stats

    def display_summary(self, stats):
        """Display summary statistics of created data."""
        total_plays = stats['plays']
        ok_pct = (stats['ok_plays'] / total_plays * 100) if total_plays > 0 else 0
        changed_pct = (stats['changed_plays'] / total_plays * 100) if total_plays > 0 else 0
        failed_pct = (stats['failed_plays'] / total_plays * 100) if total_plays > 0 else 0

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.HTTP_INFO("Summary:"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"  Created {self.style.SUCCESS(str(stats['logs']))} logs")
        self.stdout.write(f"  Created {self.style.SUCCESS(str(stats['hosts']))} hosts")
        self.stdout.write(f"  Created {self.style.SUCCESS(str(stats['plays']))} plays")
        self.stdout.write(
            f"    - {self.style.SUCCESS(str(stats['ok_plays']))} OK plays "
            f"({ok_pct:.1f}%)"
        )
        self.stdout.write(
            f"    - {self.style.WARNING(str(stats['changed_plays']))} Changed plays "
            f"({changed_pct:.1f}%)"
        )
        self.stdout.write(
            f"    - {self.style.ERROR(str(stats['failed_plays']))} Failed plays "
            f"({failed_pct:.1f}%)"
        )
        self.stdout.write("=" * 50)
        self.stdout.write(
            self.style.SUCCESS("\n✓ Mock data population completed successfully!\n")
        )
