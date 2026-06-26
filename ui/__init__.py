"""
BHARATSOLVE SEO AGENCY — UI Package
"""
from .auth import login_page, check_auth, logout
from .dashboard import show_dashboard
from .clients import show_clients_page
from .keywords import show_keywords_page
from .content import show_content_page
from .rankings import show_rankings_page
from .social import show_social_page
from .email import show_email_page
from .reports import show_reports_page
from .settings import show_settings_page
from .publisher import show_publisher_page
from .google_business import show_google_business_page
from .scheduler import show_scheduler_page
from .backup import show_backup_page

__all__ = [
    'login_page', 'check_auth', 'logout',
    'show_dashboard', 'show_clients_page',
    'show_keywords_page', 'show_content_page',
    'show_rankings_page', 'show_social_page',
    'show_email_page', 'show_reports_page',
    'show_settings_page',
    'show_publisher_page',
    'show_google_business_page',
    'show_scheduler_page',
    'show_backup_page',
]
