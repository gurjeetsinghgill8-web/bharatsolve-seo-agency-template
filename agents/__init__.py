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
from .github_publisher import (
    generate_heart_blog, build_blog_html, publish_blog_to_github,
    publish_batch_blogs, auto_blog_task, check_repo_connection
)
from .review_agent import (
    fetch_latest_reviews, process_reviews, generate_ai_reply,
    auto_reply_to_reviews, generate_review_report, auto_review_task,
    generate_review_reply, process_auto_replies, is_gbp_configured
)
from .draft_review import (
    save_pending_draft, list_pending_drafts, get_pending_draft,
    approve_and_publish_draft, reject_pending_draft, pending_draft_count
)
from .competitor_agent import (
    get_competitors, add_competitor, compare_rankings,
    generate_gap_analysis, compare_reviews, competitor_scan_task
)
from .gbp_poster import (
    post_weekly_heart_tip, get_random_heart_tip,
    generate_ai_heart_tip, post_multiple_tips, gbp_weekly_tip_task
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
    # GitHub Publisher
    'generate_heart_blog', 'build_blog_html', 'publish_blog_to_github',
    'publish_batch_blogs', 'auto_blog_task', 'check_repo_connection',
    # Review Agent
    'fetch_latest_reviews', 'process_reviews', 'generate_ai_reply',
    'auto_reply_to_reviews', 'generate_review_report', 'auto_review_task',
    'generate_review_reply', 'process_auto_replies', 'is_gbp_configured',
    # Draft Review (Telegram approval flow)
    'save_pending_draft', 'list_pending_drafts', 'get_pending_draft',
    'approve_and_publish_draft', 'reject_pending_draft', 'pending_draft_count',
    # Competitor Agent
    'get_competitors', 'add_competitor', 'compare_rankings',
    'generate_gap_analysis', 'compare_reviews', 'competitor_scan_task',
    # GBP Poster
    'post_weekly_heart_tip', 'get_random_heart_tip',
    'generate_ai_heart_tip', 'post_multiple_tips', 'gbp_weekly_tip_task',
]
