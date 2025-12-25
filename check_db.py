
import os
import sys

# Add backend to path
sys.path.append("/home/autcir_gmail_com/develop/apps/studiocentos/apps/backend")

from app.infrastructure.database.session import SessionLocal
from app.domain.toolai.models import ToolAIPost

db = SessionLocal()
try:
    posts = db.query(ToolAIPost).all()
    print(f"Total posts: {len(posts)}")
    for post in posts:
        print(f"ID: {post.id} | Slug: {post.slug} | Status: {post.status}")
finally:
    db.close()
