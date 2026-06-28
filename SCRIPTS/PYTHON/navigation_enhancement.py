"""
Navigation and User Flow Enhancement for AUGGDASH26 Dashboard System
This module implements improved navigation and user flow to enhance
the overall user experience of the dashboard system.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class NavigationType(Enum):
    """Types of navigation elements"""
    TOP_MENU = "top_menu"
    SIDEBAR = "sidebar"
    BREADCRUMB = "breadcrumb"
    PAGINATION = "pagination"
    TABS = "tabs"
    STEPPER = "stepper"

class UserFlowType(Enum):
    """Types of user flows"""
    DASHBOARD_OVERVIEW = "dashboard_overview"
    DASHBOARD_CREATION = "dashboard_creation"
    DASHBOARD_EDITING = "dashboard_editing"
    DATA_ANALYSIS = "data_analysis"
    REPORT_GENERATION = "report_generation"
    USER_SETTINGS = "user_settings"

@dataclass
class NavigationItem:
    """Data class for navigation items"""
    id: str
    title: str
    url: str
    icon: Optional[str] = None
    children: Optional[List['NavigationItem']] = None
    active: bool = False
    badge: Optional[str] = None

@dataclass
class UserFlowStep:
    """Data class for user flow steps"""
    id: str
    title: str
    description: str
    url: str
    completed: bool = False
    optional: bool = False

class NavigationManager:
    """Main class for managing navigation"""
    
    def __init__(self):
        self.navigation_tree = self._build_navigation_tree()
        self.breadcrumb = []
        self.user_flows = self._build_user_flows()
    
    def _build_navigation_tree(self) -> List[NavigationItem]:
        """Build the main navigation tree"""
        return [
            NavigationItem(
                id="dashboard",
                title="Dashboard",
                url="/dashboard",
                icon="dashboard"
            ),
            NavigationItem(
                id="dashboards",
                title="My Dashboards",
                url="/dashboards",
                icon="grid_view",
                children=[
                    NavigationItem(
                        id="all_dashboards",
                        title="All Dashboards",
                        url="/dashboards/all",
                        badge="12,402"
                    ),
                    NavigationItem(
                        id="favorites",
                        title="Favorites",
                        url="/dashboards/favorites"
                    ),
                    NavigationItem(
                        id="recent",
                        title="Recent",
                        url="/dashboards/recent"
                    )
                ]
            ),
            NavigationItem(
                id="analytics",
                title="Analytics",
                url="/analytics",
                icon="analytics",
                children=[
                    NavigationItem(
                        id="overview",
                        title="Overview",
                        url="/analytics/overview"
                    ),
                    NavigationItem(
                        id="reports",
                        title="Reports",
                        url="/analytics/reports"
                    ),
                    NavigationItem(
                        id="insights",
                        title="Insights",
                        url="/analytics/insights"
                    )
                ]
            ),
            NavigationItem(
                id="data",
                title="Data Sources",
                url="/data",
                icon="database",
                children=[
                    NavigationItem(
                        id="connections",
                        title="Connections",
                        url="/data/connections"
                    ),
                    NavigationItem(
                        id="datasets",
                        title="Datasets",
                        url="/data/datasets"
                    ),
                    NavigationItem(
                        id="import",
                        title="Import Data",
                        url="/data/import"
                    )
                ]
            ),
            NavigationItem(
                id="settings",
                title="Settings",
                url="/settings",
                icon="settings",
                children=[
                    NavigationItem(
                        id="profile",
                        title="Profile",
                        url="/settings/profile"
                    ),
                    NavigationItem(
                        id="preferences",
                        title="Preferences",
                        url="/settings/preferences"
                    ),
                    NavigationItem(
                        id="security",
                        title="Security",
                        url="/settings/security"
                    )
                ]
            )
        ]
    
    def _build_user_flows(self) -> Dict[str, List[UserFlowStep]]:
        """Build user flows for different tasks"""
        return {
            UserFlowType.DASHBOARD_CREATION.value: [
                UserFlowStep(
                    id="step1",
                    title="Select Template",
                    description="Choose a dashboard template or start from scratch",
                    url="/dashboard/create/template"
                ),
                UserFlowStep(
                    id="step2",
                    title="Add Data Sources",
                    description="Connect your data sources to the dashboard",
                    url="/dashboard/create/data"
                ),
                UserFlowStep(
                    id="step3",
                    title="Design Layout",
                    description="Arrange widgets and customize the layout",
                    url="/dashboard/create/layout"
                ),
                UserFlowStep(
                    id="step4",
                    title="Configure Widgets",
                    description="Set up charts, tables, and other visualizations",
                    url="/dashboard/create/widgets"
                ),
                UserFlowStep(
                    id="step5",
                    title="Review & Publish",
                    description="Preview and publish your dashboard",
                    url="/dashboard/create/publish"
                )
            ],
            UserFlowType.DATA_ANALYSIS.value: [
                UserFlowStep(
                    id="step1",
                    title="Select Dataset",
                    description="Choose the dataset you want to analyze",
                    url="/analysis/select-dataset"
                ),
                UserFlowStep(
                    id="step2",
                    title="Define Metrics",
                    description="Select the metrics you want to analyze",
                    url="/analysis/metrics"
                ),
                UserFlowStep(
                    id="step3",
                    title="Apply Filters",
                    description="Filter your data to focus on relevant information",
                    url="/analysis/filters"
                ),
                UserFlowStep(
                    id="step4",
                    title="Visualize Data",
                    description="Create charts and visualizations",
                    url="/analysis/visualize"
                ),
                UserFlowStep(
                    id="step5",
                    title="Generate Insights",
                    description="Get insights and recommendations from your data",
                    url="/analysis/insights"
                )
            ]
        }
    
    def get_navigation_menu(self, nav_type: NavigationType) -> List[NavigationItem]:
        """Get navigation menu for specified type"""
        if nav_type == NavigationType.TOP_MENU:
            # Return top-level items only
            return [item for item in self.navigation_tree if not item.id == "dashboards"]
        elif nav_type == NavigationType.SIDEBAR:
            # Return full navigation tree
            return self.navigation_tree
        else:
            return []
    
    def update_breadcrumb(self, path: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Update breadcrumb navigation"""
        self.breadcrumb = path
        return self.breadcrumb
    
    def get_current_user_flow(self, flow_type: str) -> Optional[List[UserFlowStep]]:
        """Get the current user flow"""
        return self.user_flows.get(flow_type)
    
    def get_user_flow_progress(self, flow_type: str) -> Dict[str, any]:
        """Get progress for a specific user flow"""
        flow = self.user_flows.get(flow_type)
        if not flow:
            return {}
        
        total_steps = len(flow)
        completed_steps = len([step for step in flow if step.completed])
        progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
        
        return {
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'progress_percentage': progress_percentage,
            'current_step': flow[completed_steps] if completed_steps < total_steps else None
        }
    
    def mark_flow_step_complete(self, flow_type: str, step_id: str) -> bool:
        """Mark a step in a user flow as complete"""
        flow = self.user_flows.get(flow_type)
        if not flow:
            return False
        
        for step in flow:
            if step.id == step_id:
                step.completed = True
                return True
        
        return False

class UserFlowManager:
    """Class for managing user flows and onboarding"""
    
    def __init__(self):
        self.active_flow = None
        self.flow_history = []
    
    def start_flow(self, flow_type: str, navigation_manager: NavigationManager) -> bool:
        """Start a new user flow"""
        flow = navigation_manager.get_current_user_flow(flow_type)
        if flow:
            self.active_flow = {
                'type': flow_type,
                'steps': flow,
                'current_step_index': 0,
                'started_at': __import__('datetime').datetime.now().isoformat()
            }
            return True
        return False
    
    def next_step(self) -> Optional[UserFlowStep]:
        """Move to the next step in the current flow"""
        if not self.active_flow:
            return None
        
        current_index = self.active_flow['current_step_index']
        steps = self.active_flow['steps']
        
        if current_index < len(steps) - 1:
            self.active_flow['current_step_index'] += 1
            return steps[self.active_flow['current_step_index']]
        
        return None
    
    def previous_step(self) -> Optional[UserFlowStep]:
        """Move to the previous step in the current flow"""
        if not self.active_flow:
            return None
        
        current_index = self.active_flow['current_step_index']
        
        if current_index > 0:
            self.active_flow['current_step_index'] -= 1
            return self.active_flow['steps'][self.active_flow['current_step_index']]
        
        return None
    
    def complete_step(self, step_id: str, navigation_manager: NavigationManager) -> bool:
        """Complete the current step and move to the next"""
        success = navigation_manager.mark_flow_step_complete(self.active_flow['type'], step_id)
        if success:
            next_step = self.next_step()
            return next_step is not None or self.active_flow['current_step_index'] >= len(self.active_flow['steps'])
        return False
    
    def get_flow_status(self) -> Dict[str, any]:
        """Get the status of the current flow"""
        if not self.active_flow:
            return {}
        
        current_step = self.active_flow['steps'][self.active_flow['current_step_index']]
        total_steps = len(self.active_flow['steps'])
        completed_steps = sum(1 for step in self.active_flow['steps'] if step.completed)
        progress = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
        
        return {
            'flow_type': self.active_flow['type'],
            'current_step': current_step,
            'current_step_number': self.active_flow['current_step_index'] + 1,
            'total_steps': total_steps,
            'progress_percentage': progress,
            'completed': self.active_flow['current_step_index'] >= total_steps - 1
        }

class SearchManager:
    """Class for managing search functionality"""
    
    def __init__(self):
        self.search_history = []
        self.recent_searches = []
    
    def search(self, query: str, search_type: str = "all") -> List[Dict[str, any]]:
        """Perform a search across the system"""
        # In a real implementation, this would search the database
        # For now, we'll return mock results
        results = []
        
        if search_type == "dashboards" or search_type == "all":
            results.extend([
                {
                    'type': 'dashboard',
                    'title': f'Dashboard containing "{query}"',
                    'url': f'/dashboard/{query.lower().replace(" ", "-")}',
                    'description': f'A dashboard related to {query}'
                }
            ])
        
        if search_type == "analytics" or search_type == "all":
            results.extend([
                {
                    'type': 'analytics',
                    'title': f'Analytics report for "{query}"',
                    'url': f'/analytics/report/{query.lower().replace(" ", "-")}',
                    'description': f'An analytics report related to {query}'
                }
            ])
        
        # Add to search history
        self.search_history.append({
            'query': query,
            'type': search_type,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'results_count': len(results)
        })
        
        # Update recent searches (keep last 5)
        self.recent_searches = [query] + [s for s in self.recent_searches if s != query][:4]
        
        return results
    
    def get_recent_searches(self, limit: int = 5) -> List[str]:
        """Get recent searches"""
        return self.recent_searches[:limit]

class ContextualHelpManager:
    """Class for managing contextual help"""
    
    def __init__(self):
        self.help_content = self._build_help_content()
    
    def _build_help_content(self) -> Dict[str, str]:
        """Build contextual help content"""
        return {
            '/dashboard': "Welcome to your dashboard overview. Here you can see all your dashboards and their status.",
            '/dashboards/create': "Create a new dashboard by selecting a template or starting from scratch.",
            '/analytics/overview': "View analytics for your dashboards including usage metrics and performance.",
            '/settings/profile': "Update your profile information and preferences.",
            '/data/connections': "Manage your data source connections here."
        }
    
    def get_help_content(self, page_url: str) -> str:
        """Get help content for a specific page"""
        return self.help_content.get(page_url, "No help content available for this page.")

class NavigationEnhancement:
    """Class for implementing navigation enhancements"""
    
    def __init__(self):
        self.enhancements = []
    
    def add_breadcrumb_navigation(self) -> str:
        """Add breadcrumb navigation to pages"""
        breadcrumb_html = """
        <nav aria-label="breadcrumb" class="breadcrumb-nav">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/dashboard">Home</a></li>
                <li class="breadcrumb-item"><a href="/dashboards">Dashboards</a></li>
                <li class="breadcrumb-item active" aria-current="page">Dashboard Name</li>
            </ol>
        </nav>
        <style>
        .breadcrumb-nav {
            padding: 1rem 0;
            margin-bottom: 1rem;
        }
        .breadcrumb {
            display: flex;
            flex-wrap: wrap;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
            list-style: none;
            background-color: #e9ecef;
            border-radius: 0.25rem;
        }
        .breadcrumb-item + .breadcrumb-item::before {
            display: inline-block;
            padding-right: 0.5rem;
            padding-left: 0.5rem;
            color: #6c757d;
            content: "/";
        }
        .breadcrumb-item a {
            color: #007bff;
            text-decoration: none;
        }
        .breadcrumb-item a:hover {
            text-decoration: underline;
        }
        </style>
        """
        self.enhancements.append("Breadcrumb navigation added")
        return breadcrumb_html
    
    def add_quick_access_toolbar(self) -> str:
        """Add quick access toolbar"""
        toolbar_html = """
        <div class="quick-access-toolbar" role="toolbar" aria-label="Quick access">
            <button class="btn btn-secondary" title="Create Dashboard" aria-label="Create new dashboard">
                <i class="icon">+</i> New Dashboard
            </button>
            <button class="btn btn-secondary" title="Search" aria-label="Search">
                <i class="icon">🔍</i> Search
            </button>
            <button class="btn btn-secondary" title="Help" aria-label="Help">
                <i class="icon">?</i> Help
            </button>
        </div>
        <style>
        .quick-access-toolbar {
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 1000;
        }
        .quick-access-toolbar .btn {
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
        }
        .quick-access-toolbar .btn span {
            display: none;
        }
        @media (min-width: 768px) {
            .quick-access-toolbar .btn span {
                display: inline;
            }
            .quick-access-toolbar .btn {
                border-radius: 4px;
                width: auto;
                height: auto;
                padding: 8px 16px;
            }
        }
        </style>
        """
        self.enhancements.append("Quick access toolbar added")
        return toolbar_html
    
    def add_page_progress_indicator(self) -> str:
        """Add page progress indicator"""
        progress_html = """
        <div class="page-progress" style="position: fixed; top: 0; left: 0; width: 0%; height: 3px; background: #4a90e2; z-index: 10000; transition: width 0.3s;"></div>
        <script>
        // Simple scroll-based progress indicator
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset;
            const docHeight = document.body.offsetHeight - window.innerHeight;
            const scrollPercent = scrollTop / docHeight * 100;
            document.querySelector('.page-progress').style.width = scrollPercent + '%';
        });
        </script>
        """
        self.enhancements.append("Page progress indicator added")
        return progress_html

# Example usage
if __name__ == "__main__":
    # Initialize navigation manager
    nav_manager = NavigationManager()
    
    # Get top navigation menu
    top_menu = nav_manager.get_navigation_menu(NavigationType.TOP_MENU)
    print(f"Top navigation menu has {len(top_menu)} items")
    
    # Get sidebar navigation
    sidebar_menu = nav_manager.get_navigation_menu(NavigationType.SIDEBAR)
    print(f"Sidebar navigation has {len(sidebar_menu)} items")
    
    # Update breadcrumb
    breadcrumb = nav_manager.update_breadcrumb([
        ("Dashboard", "/dashboard"),
        ("My Dashboards", "/dashboards"),
        ("Dashboard Name", "/dashboard/123")
    ])
    print(f"Breadcrumb updated with {len(breadcrumb)} items")
    
    # Get user flow for dashboard creation
    creation_flow = nav_manager.get_current_user_flow(UserFlowType.DASHBOARD_CREATION.value)
    print(f"Dashboard creation flow has {len(creation_flow)} steps")
    
    # Get user flow progress
    progress = nav_manager.get_user_flow_progress(UserFlowType.DASHBOARD_CREATION.value)
    print(f"Dashboard creation flow progress: {progress['progress_percentage']:.1f}%")
    
    # Initialize user flow manager
    flow_manager = UserFlowManager()
    flow_started = flow_manager.start_flow(UserFlowType.DASHBOARD_CREATION.value, nav_manager)
    print(f"Dashboard creation flow started: {flow_started}")
    
    # Get flow status
    flow_status = flow_manager.get_flow_status()
    print(f"Flow status: {flow_status['current_step_number']}/{flow_status['total_steps']} steps")
    
    # Initialize search manager
    search_manager = SearchManager()
    search_results = search_manager.search("sales", "dashboards")
    print(f"Search returned {len(search_results)} results")
    
    # Get recent searches
    recent_searches = search_manager.get_recent_searches()
    print(f"Recent searches: {recent_searches}")
    
    # Initialize contextual help
    help_manager = ContextualHelpManager()
    help_content = help_manager.get_help_content("/dashboard")
    print(f"Help content for dashboard page: {help_content[:50]}...")
    
    # Apply navigation enhancements
    enhancement = NavigationEnhancement()
    
    # Add breadcrumb navigation
    breadcrumb_html = enhancement.add_breadcrumb_navigation()
    print("Breadcrumb navigation added")
    
    # Add quick access toolbar
    toolbar_html = enhancement.add_quick_access_toolbar()
    print("Quick access toolbar added")
    
    # Add page progress indicator
    progress_html = enhancement.add_page_progress_indicator()
    print("Page progress indicator added")
    
    print("\nNavigation and user flow enhancements implemented successfully")