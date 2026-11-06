import uuid
from django.core import signing
from .constants import TOKEN_SALT

def site_context(request):
    # Random per-render token enables retry without creating duplicate inquiries.
    return {"submission_token": signing.dumps(str(uuid.uuid4()), salt=TOKEN_SALT)}
