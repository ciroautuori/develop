#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/autcir_gmail_com/markettina/apps/backend')

from app.domain.auth.services import get_password_hash

password = "password123"
hashed = get_password_hash(password)
print(f"Password: {password}")
print(f"Hash: {hashed}")
