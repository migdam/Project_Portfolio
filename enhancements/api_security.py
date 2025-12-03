"""
API Authentication and Rate Limiting
JWT-based authentication and request rate limiting
"""
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
from typing import Dict, Optional
import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.rate = requests_per_minute
        self.tokens: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        window_start = now - 60
        
        # Remove old tokens
        self.tokens[client_id] = [
            t for t in self.tokens[client_id] if t > window_start
        ]
        
        # Check rate limit
        if len(self.tokens[client_id]) < self.rate:
            self.tokens[client_id].append(now)
            return True
        
        return False


rate_limiter = RateLimiter(requests_per_minute=100)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


def check_rate_limit(token_payload: Dict = Depends(verify_token)):
    """Check rate limit for authenticated user"""
    user_id = token_payload.get("sub")
    
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return token_payload


# API Key authentication (alternative to JWT)
class APIKeyAuth:
    """API Key based authentication"""
    
    def __init__(self, db_path: str = "config/api_keys.json"):
        self.api_keys: Dict[str, Dict] = {}
        # Load from database in production
    
    def verify_api_key(self, api_key: str) -> Optional[Dict]:
        """Verify API key and return user info"""
        return self.api_keys.get(api_key)
