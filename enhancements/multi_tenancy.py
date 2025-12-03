"""
Multi-Tenancy Support
Enable multiple organizations to use the system with data isolation
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Tenant:
    """Represents an organization using the system"""
    tenant_id: str
    organization_name: str
    subscription_tier: str  # free, professional, enterprise
    max_projects: int
    max_api_calls_per_day: int
    features_enabled: List[str]
    is_active: bool = True


class TenantManager:
    """Manages multi-tenant operations and data isolation"""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
    
    def create_tenant(
        self,
        tenant_id: str,
        organization_name: str,
        subscription_tier: str = "free"
    ) -> Tenant:
        """Create a new tenant"""
        
        # Define tier limits
        tier_config = {
            "free": {
                "max_projects": 10,
                "max_api_calls": 1000,
                "features": ["prm", "cop"]
            },
            "professional": {
                "max_projects": 100,
                "max_api_calls": 50000,
                "features": ["prm", "cop", "slm", "ab_testing"]
            },
            "enterprise": {
                "max_projects": -1,  # unlimited
                "max_api_calls": -1,
                "features": ["prm", "cop", "slm", "po", "ab_testing", "feature_store", "lineage"]
            }
        }
        
        config = tier_config.get(subscription_tier, tier_config["free"])
        
        tenant = Tenant(
            tenant_id=tenant_id,
            organization_name=organization_name,
            subscription_tier=subscription_tier,
            max_projects=config["max_projects"],
            max_api_calls_per_day=config["max_api_calls"],
            features_enabled=config["features"]
        )
        
        self.tenants[tenant_id] = tenant
        logger.info(f"Created tenant {tenant_id} with {subscription_tier} tier")
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Retrieve tenant information"""
        return self.tenants.get(tenant_id)
    
    def check_feature_access(self, tenant_id: str, feature: str) -> bool:
        """Check if tenant has access to a feature"""
        tenant = self.get_tenant(tenant_id)
        if not tenant or not tenant.is_active:
            return False
        return feature in tenant.features_enabled


# Database query wrapper for tenant isolation
class TenantAwareQuery:
    """Ensures all database queries are scoped to tenant"""
    
    @staticmethod
    def add_tenant_filter(query: str, tenant_id: str) -> str:
        """Add tenant filter to SQL query"""
        if "WHERE" in query.upper():
            return f"{query} AND tenant_id = '{tenant_id}'"
        else:
            return f"{query} WHERE tenant_id = '{tenant_id}'"
