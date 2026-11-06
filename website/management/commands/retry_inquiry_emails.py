from django.core.management.base import BaseCommand
from website.models import Inquiry
from website.services import notify_inquiry

class Command(BaseCommand):
    help = "Retry pending/failed notification emails (does not resend successful ones)."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)
        parser.add_argument("--include-disabled", action="store_true", help="Also notify about inquiries received before SMTP was enabled.")

    def handle(self, *args, **options):
        statuses = [Inquiry.EmailStatus.PENDING, Inquiry.EmailStatus.FAILED]
        if options["include_disabled"]:
            statuses.append(Inquiry.EmailStatus.DISABLED)
        ids = list(Inquiry.objects.filter(email_status__in=statuses).order_by("created_at").values_list("id", flat=True)[:max(0, options["limit"])])
        sent = sum(int(notify_inquiry(pk)) for pk in ids)
        self.stdout.write(f"Checked: {len(ids)}; passed to SMTP: {sent}.")
