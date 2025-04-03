# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from django.conf import settings

# Configure logging
import logging
logger = logging.getLogger(__name__)

__all__ = ('celery_app',)
