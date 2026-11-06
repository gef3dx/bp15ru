from django.core.management.base import BaseCommand
from django.utils import timezone
from website.models import SubmissionRateBucket

class Command(BaseCommand):
    help = "Delete expired rate-limit buckets. Does not delete inquiries."

    def handle(self, *args, **options):
        deleted, _ = SubmissionRateBucket.objects.filter(expires_at__lt=timezone.now()).delete()
        self.stdout.write(f"Expired buckets deleted: {deleted}.")
