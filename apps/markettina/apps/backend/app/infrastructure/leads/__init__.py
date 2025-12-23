"""
Lead Intelligence Infrastructure.

Production-ready clients for lead generation and enrichment:
- Apollo.io for B2B lead intelligence

Features:
- People and company search
- Lead enrichment
- Contact data
"""

from app.infrastructure.leads.apollo_client import ApolloClient

__all__ = [
    "ApolloClient",
]
