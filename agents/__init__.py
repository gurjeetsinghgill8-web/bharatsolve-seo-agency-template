"""
BHARATSOLVE SEO AGENCY — Agents Package
"""
from .manager_agent import get_manager_response, analyze_user_intent
from .keyword_agent import research_keywords, suggest_keyword_clusters
from .content_agent import generate_content, generate_batch_content
from .rank_agent import check_rankings, get_ranking_insights
from .social_agent import create_social_post, generate_content_calendar
from .email_agent import (
    send_email, send_client_report_email, send_newsletter,
    send_weekly_digest, send_bulk_campaign
)
from .wordpress_agent import (
    publish_post, publish_content_piece, publish_batch_content,
    test_connection, get_site_categories
)

__all__ = [
    'get_manager_response', 'analyze_user_intent',
    'research_keywords', 'suggest_keyword_clusters',
    'generate_content', 'generate_batch_content',
    'check_rankings', 'get_ranking_insights',
    'create_social_post', 'generate_content_calendar',
    'send_email', 'send_client_report_email', 'send_newsletter',
    'send_weekly_digest', 'send_bulk_campaign',
    'publish_post', 'publish_content_piece', 'publish_batch_content',
    'test_connection', 'get_site_categories',
]
