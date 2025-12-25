"""
SEO Tools Integration - SEMrush, Ahrefs, Google APIs
"""

import os
from typing import List, Dict, Any, Optional
import aiohttp
from datetime import datetime


class SEOToolsIntegration:
    """Unified SEO tools integration"""
    
    def __init__(self):
        self.semrush_api_key = os.getenv('SEMRUSH_API_KEY')
        self.ahrefs_api_key = os.getenv('AHREFS_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        
    async def get_keyword_suggestions(
        self, 
        seed_keyword: str, 
        limit: int = 20
    ) -> List[str]:
        """Get keyword suggestions from multiple sources"""
        
        # Try SEMrush first (if available)
        if self.semrush_api_key:
            try:
                return await self._semrush_keyword_suggestions(seed_keyword, limit)
            except Exception as e:
                print(f"SEMrush error: {e}")
        
        # Fallback to Google Suggest API (free)
        return await self._google_suggest(seed_keyword, limit)
    
    async def _semrush_keyword_suggestions(
        self, 
        seed: str, 
        limit: int
    ) -> List[str]:
        """Get keywords from SEMrush API"""
        async with aiohttp.ClientSession() as session:
            url = "https://api.semrush.com/"
            params = {
                'type': 'phrase_related',
                'key': self.semrush_api_key,
                'phrase': seed,
                'export_columns': 'Ph',
                'database': 'us',
                'display_limit': limit,
            }
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    text = await response.text()
                    lines = text.strip().split('\n')[1:]  # Skip header
                    return [line.split(';')[0] for line in lines if line]
                return []
    
    async def _google_suggest(self, seed: str, limit: int) -> List[str]:
        """Get keywords from Google Suggest (free)"""
        async with aiohttp.ClientSession() as session:
            url = f"https://suggestqueries.google.com/complete/search"
            params = {
                'client': 'firefox',
                'q': seed,
            }
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data[1][:limit] if len(data) > 1 else []
                return []
    
    async def get_keyword_metrics(self, keyword: str) -> Dict[str, Any]:
        """Get keyword metrics (volume, difficulty, CPC)"""
        
        if self.semrush_api_key:
            try:
                return await self._semrush_keyword_metrics(keyword)
            except Exception as e:
                print(f"SEMrush error: {e}")
        
        # Fallback to estimates
        return {
            'keyword': keyword,
            'search_volume': await self._estimate_volume(keyword),
            'difficulty': 'medium',
            'cpc': 0.0,
            'competition': 0.5,
            'trend': 'stable',
        }
    
    async def _semrush_keyword_metrics(self, keyword: str) -> Dict[str, Any]:
        """Get metrics from SEMrush"""
        async with aiohttp.ClientSession() as session:
            url = "https://api.semrush.com/"
            params = {
                'type': 'phrase_this',
                'key': self.semrush_api_key,
                'phrase': keyword,
                'export_columns': 'Ph,Nq,Cp,Co,Nr',
                'database': 'us',
            }
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    text = await response.text()
                    lines = text.strip().split('\n')
                    if len(lines) > 1:
                        data = lines[1].split(';')
                        return {
                            'keyword': data[0],
                            'search_volume': int(data[1]) if data[1] else 0,
                            'cpc': float(data[2]) if data[2] else 0.0,
                            'competition': float(data[3]) if data[3] else 0.5,
                            'results': int(data[4]) if data[4] else 0,
                        }
                return {}
    
    async def _estimate_volume(self, keyword: str) -> int:
        """Estimate search volume based on keyword length and complexity"""
        # Simple heuristic: shorter = higher volume
        word_count = len(keyword.split())
        if word_count == 1:
            return 10000
        elif word_count == 2:
            return 5000
        elif word_count == 3:
            return 2000
        else:
            return 500
    
    async def get_domain_authority(self, domain: str) -> Dict[str, Any]:
        """Get domain authority metrics"""
        
        if self.ahrefs_api_key:
            try:
                return await self._ahrefs_domain_metrics(domain)
            except Exception as e:
                print(f"Ahrefs error: {e}")
        
        # Fallback estimates
        return {
            'domain': domain,
            'domain_rating': 50,
            'url_rating': 40,
            'backlinks': 1000,
            'referring_domains': 200,
            'organic_traffic': 10000,
        }
    
    async def _ahrefs_domain_metrics(self, domain: str) -> Dict[str, Any]:
        """Get metrics from Ahrefs API"""
        async with aiohttp.ClientSession() as session:
            url = f"https://api.ahrefs.com/v3/site-explorer/domain-rating"
            headers = {'Authorization': f'Bearer {self.ahrefs_api_key}'}
            params = {'target': domain}
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return {}
    
    async def check_page_speed(self, url: str) -> Dict[str, Any]:
        """Check page speed using Google PageSpeed Insights"""
        
        if not self.google_api_key:
            return {'score': 0, 'issues': []}
        
        async with aiohttp.ClientSession() as session:
            api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {
                'url': url,
                'key': self.google_api_key,
                'category': 'performance',
            }
            
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    lighthouse = data.get('lighthouseResult', {})
                    categories = lighthouse.get('categories', {})
                    performance = categories.get('performance', {})
                    
                    return {
                        'score': int(performance.get('score', 0) * 100),
                        'metrics': lighthouse.get('audits', {}),
                        'opportunities': self._extract_opportunities(lighthouse),
                    }
                return {'score': 0, 'issues': []}
    
    def _extract_opportunities(self, lighthouse: Dict) -> List[Dict[str, Any]]:
        """Extract optimization opportunities"""
        opportunities = []
        audits = lighthouse.get('audits', {})
        
        for audit_id, audit in audits.items():
            if audit.get('score', 1) < 0.9 and audit.get('details'):
                opportunities.append({
                    'title': audit.get('title'),
                    'description': audit.get('description'),
                    'savings': audit.get('details', {}).get('overallSavingsMs', 0),
                })
        
        return sorted(opportunities, key=lambda x: x['savings'], reverse=True)


# Singleton instance
seo_tools = SEOToolsIntegration()
