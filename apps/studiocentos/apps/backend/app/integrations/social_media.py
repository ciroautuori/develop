"""
Social Media Integration - Twitter, LinkedIn, Facebook, Instagram
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
import tweepy
from app.core.config import settings


class SocialMediaIntegration:
    """Unified social media platform integration"""

    def __init__(self):
        # Meta/Facebook
        self.meta_app_id = settings.META_APP_ID
        self.meta_app_secret = settings.META_APP_SECRET
        self.meta_access_token = settings.META_ACCESS_TOKEN
        self.facebook_page_id = settings.FACEBOOK_PAGE_ID

        # Threads
        self.threads_app_id = settings.THREADS_APP_ID
        self.threads_app_secret = settings.THREADS_APP_SECRET
        self.threads_access_token = settings.THREADS_ACCESS_TOKEN
        self.threads_user_id = settings.THREADS_USER_ID

        # Twitter/X
        self.twitter_api_key = settings.TWITTER_API_KEY
        self.twitter_api_secret = settings.TWITTER_API_SECRET
        self.twitter_access_token = settings.TWITTER_ACCESS_TOKEN
        self.twitter_access_secret = settings.TWITTER_ACCESS_SECRET
        self.twitter_bearer_token = settings.TWITTER_BEARER_TOKEN

        # LinkedIn
        self.linkedin_access_token = settings.LINKEDIN_ACCESS_TOKEN

        # Instagram
        self.instagram_account_id = settings.INSTAGRAM_ACCOUNT_ID
        self.instagram_access_token = settings.INSTAGRAM_ACCESS_TOKEN


    async def get_account_stats(self, platform: str) -> Dict[str, Any]:
        """Get account level statistics (followers, etc.)"""
        if platform == 'twitter':
            return await self._get_twitter_account_stats()
        elif platform == 'linkedin':
            return await self._get_linkedin_account_stats()
        elif platform == 'facebook':
            return await self._get_facebook_account_stats()
        elif platform == 'instagram':
            return await self._get_instagram_account_stats()
        else:
            return {}

    async def _get_twitter_account_stats(self) -> Dict[str, Any]:
        """Get Twitter account stats"""
        if not self.twitter_bearer_token:
            return {}
        try:
            client = tweepy.Client(bearer_token=self.twitter_bearer_token)
            # Get user metrics for the authenticated user or configured user
            # Since we use bearer token only here, we might need username or id.
            # Assuming we can get 'me' if using OAuth1/OAuth2 user context, but with App-only bearer it's harder.
            # If we have access tokens (OAuth1), we can use Client with consumer keys.

            if self.twitter_access_token:
                 client = tweepy.Client(
                    bearer_token=self.twitter_bearer_token,
                    consumer_key=self.twitter_api_key,
                    consumer_secret=self.twitter_api_secret,
                    access_token=self.twitter_access_token,
                    access_token_secret=self.twitter_access_secret
                )
                 me = client.get_me(user_fields=['public_metrics'])
                 if me.data:
                     metrics = me.data.public_metrics
                     return {
                         'followers': metrics.get('followers_count', 0),
                         'following': metrics.get('following_count', 0),
                         'tweets': metrics.get('tweet_count', 0),
                     }
            return {}
        except Exception as e:
            print(f"Twitter stats error: {e}")
            return {}

    async def _get_facebook_account_stats(self) -> Dict[str, Any]:
        """Get Facebook Page stats"""
        if not self.meta_access_token or not self.facebook_page_id:
            return {}
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://graph.facebook.com/v18.0/{self.facebook_page_id}"
                params = {
                    'fields': 'followers_count,fan_count',
                    'access_token': self.meta_access_token,
                }
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'followers': data.get('followers_count', 0),
                            'likes': data.get('fan_count', 0),
                        }
            return {}
        except Exception as e:
            print(f"Facebook stats error: {e}")
            return {}

    async def _get_instagram_account_stats(self) -> Dict[str, Any]:
        """Get Instagram Business stats"""
        if not self.meta_access_token or not self.instagram_account_id:
            return {}
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}"
                params = {
                    'fields': 'followers_count,media_count',
                    'access_token': self.meta_access_token,
                }
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'followers': data.get('followers_count', 0),
                            'posts': data.get('media_count', 0),
                        }
            return {}
        except Exception as e:
            print(f"Instagram stats error: {e}")
            return {}

    async def _get_linkedin_account_stats(self) -> Dict[str, Any]:
        """Get LinkedIn Page stats"""
        # Requires organization URN and access token
        return {'followers': 0}

    async def publish_post(
        self,
        platform: str,
        content: str,
        media_urls: Optional[List[str]] = None,
        scheduled_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Publish post to specified platform"""

        if platform == 'twitter':
            return await self.publish_twitter(content, media_urls)
        elif platform == 'linkedin':
            return await self.publish_linkedin(content, media_urls)
        elif platform == 'facebook':
            return await self.publish_facebook(content, media_urls)
        elif platform == 'threads':
            return await self.publish_threads(content, media_urls)
        elif platform == 'instagram':
            return await self.publish_instagram(content, media_urls)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def publish_twitter(
        self,
        content: str,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Publish to Twitter/X"""

        if not self.twitter_bearer_token:
            return {'status': 'error', 'message': 'Twitter credentials not configured'}

        try:
            client = tweepy.Client(
                bearer_token=self.twitter_bearer_token,
                consumer_key=self.twitter_api_key,
                consumer_secret=self.twitter_api_secret,
                access_token=self.twitter_access_token,
                access_token_secret=self.twitter_access_secret,
            )

            # Upload media if provided
            media_ids = []
            if media_urls:
                auth = tweepy.OAuth1UserHandler(
                    self.twitter_api_key,
                    self.twitter_api_secret,
                    self.twitter_access_token,
                    self.twitter_access_secret,
                )
                api = tweepy.API(auth)

                for url in media_urls[:4]:  # Twitter allows max 4 images
                    # Download and upload media
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as response:
                            if response.status == 200:
                                media_data = await response.read()
                                media = api.media_upload(filename='temp', file=media_data)
                                media_ids.append(media.media_id)

            # Create tweet
            response = client.create_tweet(
                text=content,
                media_ids=media_ids if media_ids else None,
            )

            return {
                'status': 'success',
                'platform': 'twitter',
                'post_id': str(response.data['id']),
                'url': f"https://twitter.com/i/web/status/{response.data['id']}",
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def publish_linkedin(
        self,
        content: str,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Publish to LinkedIn"""

        if not self.linkedin_access_token:
            return {'status': 'error', 'message': 'LinkedIn credentials not configured'}

        try:
            async with aiohttp.ClientSession() as session:
                # Get user profile
                headers = {'Authorization': f'Bearer {self.linkedin_access_token}'}
                async with session.get(
                    'https://api.linkedin.com/v2/me',
                    headers=headers
                ) as response:
                    if response.status != 200:
                        return {'status': 'error', 'message': 'Failed to get LinkedIn profile'}
                    profile = await response.json()
                    person_urn = f"urn:li:person:{profile['id']}"

                # Create post
                post_data = {
                    'author': person_urn,
                    'lifecycleState': 'PUBLISHED',
                    'specificContent': {
                        'com.linkedin.ugc.ShareContent': {
                            'shareCommentary': {'text': content},
                            'shareMediaCategory': 'NONE',
                        }
                    },
                    'visibility': {'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'},
                }

                async with session.post(
                    'https://api.linkedin.com/v2/ugcPosts',
                    headers={**headers, 'Content-Type': 'application/json'},
                    json=post_data
                ) as response:
                    if response.status == 201:
                        data = await response.json()
                        post_id = data['id']
                        return {
                            'status': 'success',
                            'platform': 'linkedin',
                            'post_id': post_id,
                            'url': f"https://www.linkedin.com/feed/update/{post_id}",
                        }
                    return {'status': 'error', 'message': await response.text()}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def publish_facebook(
        self,
        content: str,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Publish to Facebook Page with optional photo"""

        if not self.meta_access_token or not self.facebook_page_id:
            return {'status': 'error', 'message': 'Facebook credentials not configured'}

        try:
            # First get Page Access Token from User Token
            page_token = await self._get_facebook_page_token()
            if not page_token:
                return {'status': 'error', 'message': 'Failed to get page access token'}

            async with aiohttp.ClientSession() as session:
                # If we have media, publish as photo post
                if media_urls and len(media_urls) > 0:
                    url = f"https://graph.facebook.com/v18.0/{self.facebook_page_id}/photos"
                    params = {
                        'message': content,
                        'url': media_urls[0],  # Facebook accepts image URL directly
                        'access_token': page_token,
                    }
                else:
                    # Text-only post
                    url = f"https://graph.facebook.com/v18.0/{self.facebook_page_id}/feed"
                    params = {
                        'message': content,
                        'access_token': page_token,
                    }

                async with session.post(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        post_id = data.get('id') or data.get('post_id')
                        return {
                            'status': 'success',
                            'platform': 'facebook',
                            'post_id': post_id,
                            'url': f"https://facebook.com/{post_id}",
                        }
                    error_text = await response.text()
                    return {'status': 'error', 'message': error_text}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def _get_facebook_page_token(self) -> Optional[str]:
        """Get Page Access Token from User Access Token"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://graph.facebook.com/v18.0/me/accounts"
                params = {'access_token': self.meta_access_token}

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        pages = data.get('data', [])

                        # Find the specific page
                        for page in pages:
                            if page.get('id') == self.facebook_page_id:
                                return page.get('access_token')

                        # If not found by ID, return first page token
                        if pages:
                            print(f"Warning: Page ID {self.facebook_page_id} not found, using first available page")
                            return pages[0].get('access_token')

                        print(f"Error: No Facebook pages found for this account")
                        return None
                    else:
                        # Log detailed error information
                        error_text = await response.text()
                        try:
                            error_json = await response.json()
                            error_msg = error_json.get('error', {}).get('message', error_text)
                            print(f"Failed to get Facebook page token: {error_msg} (status: {response.status})")
                        except:
                            print(f"Failed to get Facebook page token: {error_text} (status: {response.status})")
                        return None
        except Exception as e:
            print(f"Exception in _get_facebook_page_token: {str(e)}")
            return None

    async def publish_threads(
        self,
        content: str,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Publish to Threads

        Doc: https://developers.facebook.com/docs/threads/posts
        """

        if not self.threads_access_token or not self.threads_user_id:
            return {'status': 'error', 'message': 'Threads credentials not configured'}

        try:
            async with aiohttp.ClientSession() as session:
                # Step 1: Create media container
                create_url = f"https://graph.threads.net/v1.0/{self.threads_user_id}/threads"

                # Prepare payload
                payload = {
                    'text': content,
                    'access_token': self.threads_access_token,
                }

                # Add media if provided
                if media_urls and len(media_urls) > 0:
                    payload['media_type'] = 'IMAGE'
                    payload['image_url'] = media_urls[0]  # Threads supports 1 image per post
                else:
                    payload['media_type'] = 'TEXT'

                # Create container
                async with session.post(create_url, params=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {'status': 'error', 'message': f'Failed to create Threads container: {error_text}'}
                    data = await response.json()
                    container_id = data.get('id')

                # Step 2: Publish container
                publish_url = f"https://graph.threads.net/v1.0/{self.threads_user_id}/threads_publish"
                publish_payload = {
                    'creation_id': container_id,
                    'access_token': self.threads_access_token,
                }

                async with session.post(publish_url, params=publish_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        post_id = data.get('id')
                        return {
                            'status': 'success',
                            'platform': 'threads',
                            'post_id': post_id,
                            'url': f"https://www.threads.net/@{self.threads_user_id}/post/{post_id}",
                        }
                    error_text = await response.text()
                    return {'status': 'error', 'message': f'Failed to publish to Threads: {error_text}'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def publish_instagram(
        self,
        content: str,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Publish to Instagram (requires media)"""

        if not self.instagram_access_token or not self.instagram_account_id:
            return {
                'status': 'error',
                'message': 'Instagram credentials not configured. Please set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID in settings.'
            }

        if not media_urls:
            return {
                'status': 'error',
                'message': 'Instagram requires at least one image. Please provide an image URL.'
            }

        try:
            async with aiohttp.ClientSession() as session:
                # Validate image URL format
                image_url = media_urls[0]
                if not image_url.startswith(('http://', 'https://')):
                    return {
                        'status': 'error',
                        'message': f'Invalid image URL format: {image_url}. URL must start with http:// or https://'
                    }

                # Create media container
                url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/media"
                params = {
                    'image_url': image_url,
                    'caption': content,
                    'access_token': self.instagram_access_token,
                }

                async with session.post(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        try:
                            error_json = await response.json()
                            error_msg = error_json.get('error', {}).get('message', error_text)
                            error_code = error_json.get('error', {}).get('code', 'unknown')
                            return {
                                'status': 'error',
                                'message': f'Failed to create Instagram media container: {error_msg} (code: {error_code})'
                            }
                        except:
                            return {'status': 'error', 'message': f'Instagram API error: {error_text}'}

                    data = await response.json()
                    container_id = data.get('id')

                    if not container_id:
                        return {
                            'status': 'error',
                            'message': 'Failed to get container ID from Instagram API response'
                        }

                # Publish media
                publish_url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/media_publish"
                publish_params = {
                    'creation_id': container_id,
                    'access_token': self.instagram_access_token,
                }

                async with session.post(publish_url, params=publish_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        post_id = data.get('id')
                        return {
                            'status': 'success',
                            'platform': 'instagram',
                            'post_id': post_id,
                            'url': f"https://instagram.com/p/{post_id}",
                        }

                    error_text = await response.text()
                    try:
                        error_json = await response.json()
                        error_msg = error_json.get('error', {}).get('message', error_text)
                        return {
                            'status': 'error',
                            'message': f'Failed to publish Instagram media: {error_msg}'
                        }
                    except:
                        return {'status': 'error', 'message': f'Instagram publish error: {error_text}'}

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Instagram integration exception: {str(e)}'
            }


    async def get_engagement_metrics(
        self,
        platform: str,
        post_id: str
    ) -> Dict[str, Any]:
        """Get engagement metrics for a post"""

        if platform == 'twitter':
            return await self._get_twitter_metrics(post_id)
        elif platform == 'linkedin':
            return await self._get_linkedin_metrics(post_id)
        elif platform == 'facebook':
            return await self._get_facebook_metrics(post_id)
        elif platform == 'instagram':
            return await self._get_instagram_metrics(post_id)
        else:
            return {}

    async def _get_twitter_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """Get Twitter engagement metrics"""
        if not self.twitter_bearer_token:
            return {}

        try:
            client = tweepy.Client(bearer_token=self.twitter_bearer_token)
            tweet = client.get_tweet(
                tweet_id,
                tweet_fields=['public_metrics', 'created_at']
            )

            if tweet.data:
                metrics = tweet.data.public_metrics
                return {
                    'likes': metrics.get('like_count', 0),
                    'retweets': metrics.get('retweet_count', 0),
                    'replies': metrics.get('reply_count', 0),
                    'impressions': metrics.get('impression_count', 0),
                }
            return {}
        except Exception as e:
            print(f"Twitter metrics error: {e}")
            return {}

    async def _get_facebook_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get Facebook engagement metrics"""
        if not self.facebook_access_token:
            return {}

        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://graph.facebook.com/v18.0/{post_id}"
                params = {
                    'fields': 'likes.summary(true),comments.summary(true),shares',
                    'access_token': self.facebook_access_token,
                }

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'likes': data.get('likes', {}).get('summary', {}).get('total_count', 0),
                            'comments': data.get('comments', {}).get('summary', {}).get('total_count', 0),
                            'shares': data.get('shares', {}).get('count', 0),
                        }
            return {}
        except Exception as e:
            print(f"Facebook metrics error: {e}")
            return {}

    async def _get_linkedin_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get LinkedIn engagement metrics"""
        # LinkedIn API v2 requires specific permissions
        return {'likes': 0, 'comments': 0, 'shares': 0}

    async def _get_instagram_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get Instagram engagement metrics"""
        if not self.instagram_access_token:
            return {}

        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://graph.facebook.com/v18.0/{post_id}"
                params = {
                    'fields': 'like_count,comments_count',
                    'access_token': self.instagram_access_token,
                }

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'likes': data.get('like_count', 0),
                            'comments': data.get('comments_count', 0),
                        }
            return {}
        except Exception as e:
            print(f"Instagram metrics error: {e}")
            return {}


# Singleton instance
social_media = SocialMediaIntegration()
