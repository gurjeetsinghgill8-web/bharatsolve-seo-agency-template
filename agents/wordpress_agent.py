"""
BHARATSOLVE SEO AGENCY — WordPress Content Publisher Agent
Auto-publish SEO content to WordPress sites via XML-RPC.
Supports: blog posts, pages, custom post types, categories, tags, featured images.
"""
import json
import os
import time
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    from wordpress_xmlrpc import Client as WPClient, WordPressPost
    from wordpress_xmlrpc.methods.posts import GetPosts, NewPost, EditPost, DeletePost
    from wordpress_xmlrpc.methods.taxonomies import GetTerms
    from wordpress_xmlrpc.methods.media import UploadFile
    WP_AVAILABLE = True
except ImportError:
    WPClient = None
    WordPressPost = None
    GetPosts = NewPost = EditPost = DeletePost = None
    GetTerms = None
    UploadFile = None
    WP_AVAILABLE = False

from utils.llm_client import call_llm
from db.operations import (
    get_content, log_agent_action, get_wp_sites, save_wp_site,
    update_content_publish_status
)

logger = logging.getLogger(__name__)

# ── Default WordPress XML-RPC endpoint ──
DEFAULT_XMLRPC_PATH = "/xmlrpc.php"


def get_wp_client(site_config: dict) -> Optional[Any]:
    """
    Create a WordPress XML-RPC client from site config.
    
    Args:
        site_config: Dict with 'url', 'username', 'password_encrypted' (encrypted application password)
    
    Returns:
        WordPress Client instance or None if failed
    """
    if not WP_AVAILABLE:
        logger.error("python-wordpress-xmlrpc not installed. Run: pip install python-wordpress-xmlrpc")
        return None
    
    try:
        url = site_config.get('url', '').rstrip('/')
        xmlrpc_url = site_config.get('xmlrpc_url', url + DEFAULT_XMLRPC_PATH)
        username = site_config.get('username', '')
        password_enc = site_config.get('password_encrypted', site_config.get('password', ''))
        
        if not all([url, username, password_enc]):
            logger.error("WordPress site config incomplete: need url, username, password")
            return None
        
        # Decrypt password
        try:
            from secure_vault import decrypt_data
            password = decrypt_data(password_enc)
        except:
            import base64
            try:
                password = base64.b64decode(password_enc).decode()
            except:
                password = password_enc
        
        if not password:
            logger.error("Could not decrypt WordPress password")
            return None
        
        client = WPClient(xmlrpc_url, username, password)
        # Test connection by fetching a post
        test = client.call(GetPosts({'number': 1}))
        logger.info(f"✅ Connected to WordPress: {url}")
        return client
    
    except Exception as e:
        logger.error(f"❌ WordPress connection failed: {e}")
        return None


def publish_post(
    site_id: int,
    title: str,
    content: str,
    excerpt: str = "",
    post_type: str = "post",
    status: str = "publish",
    categories: List[str] = None,
    tags: List[str] = None,
    meta_title: str = "",
    meta_description: str = "",
    featured_image_url: str = "",
    slug: str = ""
) -> Dict[str, Any]:
    """
    Publish content to a WordPress site.
    
    Args:
        site_id: Database ID of the WordPress site
        title: Post title
        content: Post body (HTML)
        excerpt: Post excerpt
        post_type: 'post', 'page', or custom post type slug
        status: 'publish', 'draft', 'pending'
        categories: List of category names
        tags: List of tag names
        meta_title: SEO meta title (Yoast/RankMath)
        meta_description: SEO meta description
        featured_image_url: URL for featured image
        slug: Custom URL slug
    
    Returns:
        Dict with publish result including post_id and url
    """
    sites = get_wp_sites()
    site_config = next((s for s in sites if s['id'] == site_id), None)
    
    if not site_config:
        return {"success": False, "error": f"WordPress site ID {site_id} not found"}
    
    client = get_wp_client(site_config)
    if not client:
        return {
            "success": False,
            "error": "Could not connect to WordPress. Check your credentials and XML-RPC URL."
        }
    
    try:
        post = WordPressPost()
        post.title = title
        post.content = content
        post.post_status = status
        post.post_type = post_type
        
        if excerpt:
            post.excerpt = excerpt
        
        if slug:
            post.slug = slug
        
        # Categories & Tags
        if categories:
            post.terms_names = post.terms_names or {}
            post.terms_names['category'] = categories
        if tags:
            post.terms_names = post.terms_names or {}
            post.terms_names['post_tag'] = tags
        
        # Yoast / RankMath SEO meta (via custom fields)
        if meta_title:
            post.custom_fields = post.custom_fields or []
            post.custom_fields.append({'key': '_yoast_wpseo_title', 'value': meta_title})
        if meta_description:
            post.custom_fields = post.custom_fields or []
            post.custom_fields.append({'key': '_yoast_wpseo_metadesc', 'value': meta_description})
        
        # Upload featured image if URL provided
        if featured_image_url:
            try:
                import requests
                img_data = requests.get(featured_image_url, timeout=30).content
                img_name = featured_image_url.split('/')[-1].split('?')[0] or 'featured.jpg'
                
                data = {
                    'name': img_name,
                    'type': img_name.split('.')[-1] if '.' in img_name else 'jpeg',
                    'bits': img_data,
                    'overwrite': True
                }
                img_result = client.call(UploadFile(data))
                post.thumbnail = img_result['id']
            except Exception as img_err:
                logger.warning(f"⚠️ Featured image upload failed: {img_err}")
        
        # Publish
        post_id = client.call(NewPost(post))
        
        # Get the permalink
        published_posts = client.call(GetPosts({'post_type': post_type, 'number': 1, 'post__in': [post_id]}))
        permalink = ""
        if published_posts:
            permalink = published_posts[0].link
        
        result = {
            "success": True,
            "post_id": post_id,
            "url": permalink,
            "status": status,
            "site_url": site_config.get('url', '')
        }
        
        log_agent_action(
            'wordpress_agent', 
            f"Published '{title[:50]}...' to {site_config.get('url', '')} (ID: {post_id})",
            'ok'
        )
        
        return result
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ WordPress publish failed: {error_msg}")
        
        log_agent_action(
            'wordpress_agent',
            f"Failed to publish '{title[:50]}...'",
            'error',
            error_message=error_msg
        )
        
        return {"success": False, "error": error_msg}


def publish_content_piece(
    content_id: int,
    site_id: int,
    status: str = "publish",
    add_meta: bool = True
) -> Dict[str, Any]:
    """
    Publish an existing content piece from the database to WordPress.
    
    Args:
        content_id: ID from content_pieces table
        site_id: WordPress site ID
        status: 'publish' or 'draft'
        add_meta: Auto-generate meta title/desc if missing
    
    Returns:
        Dict with publish result
    """
    from db.operations import get_single_content
    
    content_data = get_single_content(content_id)
    if not content_data:
        return {"success": False, "error": f"Content piece {content_id} not found"}
    
    title = content_data.get('meta_title') or content_data.get('title', 'Untitled')
    body = content_data.get('content', '')
    target_kw = content_data.get('target_keyword', '')
    meta_desc = content_data.get('meta_description', '')
    
    # Auto-generate meta if missing and requested
    if add_meta and (not meta_desc or not title.startswith("<")):
        try:
            prompt = f"""Given this SEO content about "{target_kw}", generate:
1. A compelling meta title (max 60 chars)
2. A meta description (max 160 chars)

Title: {content_data.get('title', '')}
Content preview: {body[:300]}

Return as JSON: {{"title": "...", "description": "..."}}"""
            
            meta_result = call_llm(prompt, provider="groq", model="llama-3.1-8b-instant")
            if meta_result:
                try:
                    parsed = json.loads(meta_result)
                    title = parsed.get('title', title)
                    meta_desc = parsed.get('description', meta_desc)
                except:
                    pass
        except:
            pass
    
    # Build excerpt from first 150 chars
    excerpt = body[:200].strip().rstrip('.,;:') + "..." if len(body) > 200 else body
    
    categories = [target_kw] if target_kw else []
    
    result = publish_post(
        site_id=site_id,
        title=title[:60] if len(title) > 60 else title,
        content=body,
        excerpt=excerpt,
        status=status,
        categories=categories,
        meta_title=title,
        meta_description=meta_desc[:160] if meta_desc else ""
    )
    
    # Update the content piece status in DB
    if result.get('success'):
        update_content_publish_status(
            content_id=content_id,
            status=f"published_{status}",
            url=result.get('url', '')
        )
    
    return result


def publish_batch_content(
    content_ids: List[int],
    site_id: int,
    status: str = "publish"
) -> List[Dict[str, Any]]:
    """
    Publish multiple content pieces to WordPress.
    
    Args:
        content_ids: List of content piece IDs
        site_id: WordPress site ID
        status: 'publish' or 'draft'
    
    Returns:
        List of results for each piece
    """
    results = []
    for cid in content_ids:
        result = publish_content_piece(cid, site_id, status)
        results.append(result)
        time.sleep(1)  # Rate limiting
    
    return results


def get_site_categories(site_id: int) -> List[Dict[str, Any]]:
    """Get available categories from a WordPress site."""
    sites = get_wp_sites()
    site_config = next((s for s in sites if s['id'] == site_id), None)
    if not site_config:
        return []
    
    client = get_wp_client(site_config)
    if not client:
        return []
    
    try:
        terms = client.call(GetTerms('category'))
        return [{"id": t.id, "name": t.name, "slug": t.slug} for t in terms]
    except Exception as e:
        logger.error(f"Failed to fetch categories: {e}")
        return []


def test_connection(site_id: int) -> Dict[str, Any]:
    """
    Test WordPress connection and return site info.
    
    Args:
        site_id: WordPress site ID
    
    Returns:
        Dict with connection status and site info
    """
    sites = get_wp_sites()
    site_config = next((s for s in sites if s['id'] == site_id), None)
    
    if not site_config:
        return {"success": False, "error": "Site not found"}
    
    start = time.time()
    client = get_wp_client(site_config)
    elapsed = int((time.time() - start) * 1000)
    
    if not client:
        return {
            "success": False,
            "error": "Connection failed",
            "site_url": site_config.get('url', ''),
            "response_time_ms": elapsed
        }
    
    try:
        # Get site info via posts query
        posts = client.call(GetPosts({'number': 3}))
        categories = client.call(GetTerms('category'))
        
        return {
            "success": True,
            "site_url": site_config.get('url', ''),
            "xmlrpc_url": site_config.get('xmlrpc_url', site_config.get('url', '') + DEFAULT_XMLRPC_PATH),
            "recent_posts": len(posts),
            "total_categories": len(categories),
            "response_time_ms": elapsed,
            "wp_version": "connected"
        }
    except Exception as e:
        return {
            "success": True,
            "site_url": site_config.get('url', ''),
            "response_time_ms": elapsed,
            "note": "Connected but limited info"
        }
