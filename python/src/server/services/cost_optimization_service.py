"""
Cost Optimization Service for Archon

This service provides cost analysis and optimization recommendations for cloud resources
linked to projects. It integrates with cloud provider APIs (AWS, GCP, Azure) to fetch
usage and cost data, then provides actionable insights.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json
import threading

from src.server.services.credential_service import credential_service
from src.server.utils import get_supabase_client
from ..config.logfire_config import get_logger

logger = get_logger(__name__)


class CostOptimizationService:
    """Service for cloud cost analysis and optimization."""

    # Per-instance lock for thread-safe lazy initialization of the Supabase client
    _client_lock = threading.Lock()

    def __init__(self, supabase_client=None):
        """Initialize with optional supabase client."""
        self._supabase_client = supabase_client
        self._client_initialized = supabase_client is not None

    @property
    def supabase_client(self):
        """Lazy-load Supabase client on first access (thread-safe)."""
        if self._client_initialized:
            return self._supabase_client
        with self._client_lock:
            if self._client_initialized:
                return self._supabase_client
            try:
                self._supabase_client = get_supabase_client()
            except Exception as e:
                logger.warning(f"Supabase unavailable in CostOptimizationService: {e}")
                self._supabase_client = None
            self._client_initialized = True
            return self._supabase_client

    async def get_cloud_credentials(self, project_id: str) -> Dict[str, Any]:
        """
        Get cloud provider credentials for a project.
        Looks for credentials stored under the project or in global settings.
        """
        try:
            # First try to get project-specific credentials
            project_response = (
                self.supabase_client.table("archon_projects")
                .select("data")
                .eq("id", project_id)
                .execute()
            )

            project_data = {}
            if project_response.data and len(project_response.data) > 0:
                project_data = project_response.data[0].get("data", {})
                # Check if project has cloud credentials in its data
                if "cloud_credentials" in project_data:
                    return project_data["cloud_credentials"]

            # Fallback to global credentials
            aws_key = await credential_service.get_credential("AWS_ACCESS_KEY_ID")
            aws_secret = await credential_service.get_credential("AWS_SECRET_ACCESS_KEY")
            gcp_key = await credential_service.get_credential("GCP_SERVICE_ACCOUNT_KEY")
            azure_key = await credential_service.get_credential("AZURE_SUBSCRIPTION_ID")
            azure_secret = await credential_service.get_credential("AZURE_CLIENT_SECRET")

            credentials = {}
            if aws_key and aws_secret:
                credentials["aws"] = {
                    "access_key_id": aws_key,
                    "secret_access_key": aws_secret,
                }
            if gcp_key:
                credentials["gcp"] = {
                    "service_account_key": gcp_key,
                }
            if azure_key and azure_secret:
                credentials["azure"] = {
                    "subscription_id": azure_key,
                    "client_secret": azure_secret,
                }

            return credentials

        except Exception as e:
            logger.error(f"Error getting cloud credentials for project {project_id}: {e}")
            return {}

    async def analyze_aws_costs(self, credentials: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """
        Analyze AWS costs and usage.
        In a real implementation, this would use the AWS SDK (boto3) to fetch Cost Explorer data.
        For now, we return mock data to demonstrate the structure.
        """
        try:
            # TODO: Implement actual AWS Cost Explorer API calls
            # For now, return mock analysis
            return {
                "provider": "aws",
                "analysis_period_days": days,
                "total_cost": 1245.67,
                "total_cost_last_period": 980.42,
                "cost_change_percent": 27.1,
                "top_services": [
                    {"service": "EC2", "cost": 450.23, "percentage": 36.1},
                    {"service": "RDS", "cost": 320.10, "percentage": 25.7},
                    {"service": "S3", "cost": 180.50, "percentage": 14.5},
                    {"service": "Lambda", "cost": 95.80, "percentage": 7.7},
                    {"service": "CloudWatch", "cost": 75.30, "percentage": 6.0},
                ],
                "recommendations": [
                    {
                        "type": "rightsizing",
                        "resource": "EC2 Instance",
                        "resource_id": "i-0a1b2c3d4e5f6g7h8",
                        "current_instance_type": "m5.large",
                        "recommended_instance_type": "t3.large",
                        "estimated_monthly_savings": 45.00,
                        "confidence": "high",
                    },
                    {
                        "type": "idle_resource",
                        "resource": "RDS Instance",
                        "resource_id": "db-abcdef123456",
                        "issue": "No connections for 7+ days",
                        "estimated_monthly_savings": 120.00,
                        "confidence": "medium",
                    },
                    {
                        "type": "storage_optimization",
                        "resource": "S3 Bucket",
                        "resource_id": "archon-logs-backup",
                        "issue": "Objects in Standard storage for >90 days",
                        "recommended_action": "Transition to Glacier",
                        "estimated_monthly_savings": 65.00,
                        "confidence": "high",
                    },
                ],
                "analyzed_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error analyzing AWS costs: {e}")
            return {"error": str(e), "provider": "aws"}

    async def analyze_gcp_costs(self, credentials: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """
        Analyze GCP costs and usage.
        Mock implementation for now.
        """
        try:
            return {
                "provider": "gcp",
                "analysis_period_days": days,
                "total_cost": 890.33,
                "total_cost_last_period": 750.18,
                "cost_change_percent": 18.7,
                "top_services": [
                    {"service": "Compute Engine", "cost": 320.45, "percentage": 36.0},
                    {"service": "Cloud SQL", "cost": 210.80, "percentage": 23.7},
                    {"service": "Cloud Storage", "cost": 150.25, "percentage": 16.9},
                    {"service": "BigQuery", "cost": 95.60, "percentage": 10.7},
                    {"service": "Kubernetes Engine", "cost": 65.20, "percentage": 7.3},
                ],
                "recommendations": [
                    {
                        "type": "rightsizing",
                        "resource": "Compute Engine VM",
                        "resource_id": "projects/my-project/zones/us-central1-a/instances/vm-1",
                        "current_machine_type": "n1-standard-4",
                        "recommended_machine_type": "e2-standard-4",
                        "estimated_monthly_savings": 38.50,
                        "confidence": "high",
                    },
                    {
                        "type": "idle_resource",
                        "resource": "Cloud SQL Instance",
                        "resource_id": "my-project:us-central1:my-instance",
                        "issue": "Low CPU utilization (<10%) for 14 days",
                        "estimated_monthly_savings": 85.00,
                        "confidence": "medium",
                    },
                ],
                "analyzed_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error analyzing GCP costs: {e}")
            return {"error": str(e), "provider": "gcp"}

    async def analyze_azure_costs(self, credentials: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """
        Analyze Azure costs and usage.
        Mock implementation for now.
        """
        try:
            return {
                "provider": "azure",
                "analysis_period_days": days,
                "total_cost": 1050.92,
                "total_cost_last_period": 920.55,
                "cost_change_percent": 14.2,
                "top_services": [
                    {"service": "Virtual Machines", "cost": 380.60, "percentage": 36.2},
                    {"service": "SQL Database", "cost": 240.30, "percentage": 22.9},
                    {"service": "Blob Storage", "cost": 160.15, "percentage": 15.2},
                    {"service": "App Service", "cost": 110.80, "percentage": 10.5},
                    {"service": "Functions", "cost": 65.40, "percentage": 6.2},
                ],
                "recommendations": [
                    {
                        "type": "rightsizing",
                        "resource": "Virtual Machine",
                        "resource_id": "/subscriptions/xxx/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1",
                        "current_size": "Standard_D4s_v3",
                        "recommended_size": "Standard_B4ms",
                        "estimated_monthly_savings": 52.00,
                        "confidence": "high",
                    },
                    {
                        "type": "idle_resource",
                        "resource": "App Service Plan",
                        "resource_id": "/subscriptions/xxx/resourceGroups/rg/providers/Microsoft.Web/serverfarms/plan1",
                        "issue": "Low request count and memory usage",
                        "estimated_monthly_savings": 40.00,
                        "confidence": "medium",
                    },
                ],
                "analyzed_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error analyzing Azure costs: {e}")
            return {"error": str(e), "provider": "azure"}

    async def analyze_project_costs(self, project_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Perform cost analysis for all cloud providers linked to a project.
        """
        try:
            # Get project details
            project_response = (
                self.supabase_client.table("archon_projects")
                .select("title, github_repo")
                .eq("id", project_id)
                .execute()
            )

            if not project_response.data or len(project_response.data) == 0:
                return {"error": f"Project {project_id} not found"}

            project = project_response.data[0]
            logger.info(f"Starting cost analysis for project: {project['title']} ({project_id})")

            # Get cloud credentials
            credentials = await self.get_cloud_credentials(project_id)

            if not credentials:
                return {
                    "error": "No cloud credentials found for project",
                    "project_id": project_id,
                    "project_title": project["title"],
                }

            # Analyze each cloud provider
            results = {
                "project_id": project_id,
                "project_title": project["title"],
                "github_repo": project.get("github_repo"),
                "analysis_period_days": days,
                "analyzed_at": datetime.utcnow().isoformat(),
                "providers": {},
            }

            # AWS
            if "aws" in credentials:
                results["providers"]["aws"] = await self.analyze_aws_costs(
                    credentials["aws"], days
                )

            # GCP
            if "gcp" in credentials:
                results["providers"]["gcp"] = await self.analyze_gcp_costs(
                    credentials["gcp"], days
                )

            # Azure
            if "azure" in credentials:
                results["providers"]["azure"] = await self.analyze_azure_costs(
                    credentials["azure"], days
                )

            # Calculate summary
            total_cost = 0
            total_savings = 0
            recommendation_count = 0

            for provider, data in results["providers"].items():
                if "total_cost" in data:
                    total_cost += data["total_cost"]
                if "recommendations" in data:
                    for rec in data["recommendations"]:
                        if "estimated_monthly_savings" in rec:
                            total_savings += rec["estimated_monthly_savings"]
                        recommendation_count += 1

            results["summary"] = {
                "total_monthly_cost": total_cost,
                "total_potential_monthly_savings": total_savings,
                "recommendation_count": recommendation_count,
                "savings_percentage": (total_savings / total_cost * 100) if total_cost > 0 else 0,
            }

            # Store results in project data for historical tracking
            await self._store_cost_analysis(project_id, results)

            return results

        except Exception as e:
            logger.error(f"Error analyzing project costs for {project_id}: {e}")
            return {"error": str(e), "project_id": project_id}

    async def _store_cost_analysis(self, project_id: str, analysis_results: Dict[str, Any]):
        """
        Store cost analysis results in the project's data field.
        We'll maintain a history of analyses under project.data.cost_analyses.
        """
        try:
            # Get current project data
            project_response = (
                self.supabase_client.table("archon_projects")
                .select("data")
                .eq("id", project_id)
                .execute()
            )

            current_data = {}
            if project_response.data and len(project_response.data) > 0:
                current_data = project_response.data[0].get("data", {})

            # Initialize cost_analyses array if not present
            if "cost_analyses" not in current_data:
                current_data["cost_analyses"] = []

            # Add this analysis with a timestamp
            analysis_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "period_days": analysis_results.get("analysis_period_days", 30),
                "summary": analysis_results.get("summary", {}),
                # Store only summary to avoid huge data blobs
                # Full analysis could be stored in a separate table if needed
            }

            # Keep only the last 10 analyses to prevent unbounded growth
            current_data["cost_analyses"] = [
                analysis_entry
            ] + current_data["cost_analyses"][:9]

            # Update the project
            self.supabase_client.table("archon_projects").update(
                {"data": current_data, "updated_at": datetime.utcnow().isoformat()}
            ).eq("id", project_id).execute()

            logger.info(f"Stored cost analysis results for project {project_id}")

        except Exception as e:
            logger.error(f"Error storing cost analysis for project {project_id}: {e}")
            # Don't fail the whole operation if storage fails

    async def get_cost_analysis_history(self, project_id: str, limit: int = 5) -> Dict[str, Any]:
        """
        Retrieve historical cost analyses for a project.
        """
        try:
            project_response = (
                self.supabase_client.table("archon_projects")
                .select("data")
                .eq("id", project_id)
                .execute()
            )

            if not project_response.data or len(project_response.data) == 0:
                return {"error": f"Project {project_id} not found"}

            current_data = project_response.data[0].get("data", {})
            analyses = current_data.get("cost_analyses", [])

            # Return the most recent analyses
            return {
                "project_id": project_id,
                "analyses": analyses[:limit],
                "total_count": len(analyses),
            }

        except Exception as e:
            logger.error(f"Error getting cost analysis history for {project_id}: {e}")
            return {"error": str(e), "project_id": project_id}


# Global instance (lazy-initialized on first use, thread-safe singleton)
_cost_optimization_service: Optional[CostOptimizationService] = None
_cost_optimization_service_lock = threading.Lock()


def get_cost_optimization_service() -> CostOptimizationService:
    """Get the cost optimization service instance (thread-safe singleton)."""
    global _cost_optimization_service
    if _cost_optimization_service is not None:
        return _cost_optimization_service
    with _cost_optimization_service_lock:
        if _cost_optimization_service is None:
            _cost_optimization_service = CostOptimizationService()
        return _cost_optimization_service