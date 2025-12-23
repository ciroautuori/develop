"""
Lead Intelligence Infrastructure.

Production-ready clients for lead generation and enrichment:
- Apollo.io API for prospecting
- Clearbit (future)
- Hunter.io (future)
"""

from .apollo_client import ApolloClient, ApolloError

__all__ = [
    "ApolloClient",
    "ApolloError",
]
