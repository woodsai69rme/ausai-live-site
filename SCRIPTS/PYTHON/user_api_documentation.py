"""
User Guides and API Documentation for AUGGDASH26 Dashboard System
This module provides comprehensive user guides and API documentation
for the AUGGDASH26 dashboard system.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class UserGuideSection:
    """Data class for user guide sections"""
    title: str
    content: str
    audience: str  # 'beginner', 'intermediate', 'advanced'
    estimated_time: str  # e.g., '5 min', '15 min'

@dataclass
class APIEndpoint:
    """Data class for API endpoints"""
    method: str
    path: str
    summary: str
    description: str
    parameters: List[Dict[str, Any]]
    responses: Dict[str, Dict[str, str]]
    example_request: str
    example_response: str

class UserGuideGenerator:
    """Class for generating user guides"""
    
    def __init__(self):
        self.guide_sections = self._create_guide_sections()
    
    def _create_guide_sections(self) -> List[UserGuideSection]:
        """Create all user guide sections"""
        return [
            UserGuideSection(
                title="Getting Started",
                content="""
# Getting Started with AUGGDASH26

## Creating Your First Dashboard

1. **Sign In**: Navigate to the AUGGDASH26 dashboard and sign in with your credentials
2. **Create Dashboard**: Click the "New Dashboard" button in the top navigation
3. **Choose Template**: Select a template that fits your needs or start from scratch
4. **Name Your Dashboard**: Give your dashboard a descriptive name
5. **Add Widgets**: Drag and drop widgets from the sidebar onto your dashboard
6. **Configure Widgets**: Click on each widget to configure its data source and appearance
7. **Save Dashboard**: Click the "Save" button to save your dashboard

## Dashboard Layout

AUGGDASH26 uses a responsive grid system that automatically adjusts to different screen sizes. You can:

- Drag widgets to rearrange them
- Resize widgets by dragging their corners
- Use the layout toolbar to align widgets
- Switch between different layout modes (grid, list, etc.)

## Data Sources

Connect your dashboard to various data sources:

- **CSV Files**: Upload CSV files directly
- **APIs**: Connect to REST APIs with authentication
- **Databases**: Connect to SQL databases
- **Cloud Services**: Connect to cloud storage services
""",
                audience="beginner",
                estimated_time="10 min"
            ),
            UserGuideSection(
                title="Dashboard Customization",
                content="""
# Dashboard Customization

## Widget Configuration

Each widget can be configured with different settings:

### Chart Widgets
- **Data Source**: Select the data source for the chart
- **Chart Type**: Choose from line, bar, pie, scatter, etc.
- **Time Range**: Set the time range for the data
- **Aggregation**: Choose how to aggregate the data (sum, average, count, etc.)
- **Styling**: Customize colors, fonts, and layout

### Table Widgets
- **Columns**: Select which columns to display
- **Sorting**: Set default sort order
- **Filtering**: Add filters to the table
- **Pagination**: Set number of rows per page
- **Export**: Enable export options

### Metric Widgets
- **Value**: Select the metric to display
- **Target**: Set target values for comparison
- **Trend**: Show trend indicators
- **Formatting**: Format numbers, dates, etc.

## Theme Customization

Customize the appearance of your dashboard:

1. **Color Scheme**: Choose from predefined color schemes or create your own
2. **Typography**: Select fonts and font sizes
3. **Spacing**: Adjust padding and margins
4. **Background**: Set background colors or images
5. **Branding**: Add your logo and brand colors

## Sharing and Permissions

Control who can access your dashboard:

- **Public**: Anyone with the link can view
- **Private**: Only you can view
- **Shared**: Specific users or groups can view/edit
- **Organization**: All organization members can view
""",
                audience="intermediate",
                estimated_time="15 min"
            ),
            UserGuideSection(
                title="Advanced Features",
                content="""
# Advanced Features

## Dashboard Variables

Use variables to make your dashboards more dynamic:

1. **Create Variable**: Go to Dashboard Settings > Variables
2. **Define Variable**: Set name, type, and default value
3. **Use Variable**: Reference in queries with ${variable_name}

Example: Create a date range variable to filter data across all panels

## Dashboard Templates

Create reusable dashboard templates:

1. **Save as Template**: From any dashboard, select "Save as Template"
2. **Template Variables**: Add variables to make templates flexible
3. **Apply Template**: Use templates when creating new dashboards

## Alerting

Set up alerts based on dashboard metrics:

1. **Create Alert Rule**: In dashboard settings, define conditions
2. **Set Threshold**: Define when the alert should trigger
3. **Configure Notifications**: Choose how to receive alerts
4. **Test Alert**: Verify the alert works as expected

## Dashboard Embedding

Embed dashboards in other applications:

1. **Get Embed Code**: In dashboard settings, click "Embed"
2. **Configure Options**: Set permissions and appearance
3. **Use in Application**: Paste the embed code into your application

## API Integration

Use the API to programmatically manage dashboards:

- Create dashboards from external data
- Update dashboard content automatically
- Retrieve dashboard metrics for external systems
""",
                audience="advanced",
                estimated_time="20 min"
            ),
            UserGuideSection(
                title="Troubleshooting",
                content="""
# Troubleshooting

## Common Issues

### Dashboard Not Loading
- Check your internet connection
- Clear your browser cache
- Try a different browser
- Contact support if the issue persists

### Data Not Updating
- Verify your data source is accessible
- Check authentication credentials
- Ensure your API keys are valid
- Review any error messages in the console

### Widgets Not Displaying Correctly
- Refresh the dashboard
- Check widget configuration
- Verify data format matches expectations
- Resize the widget to trigger re-rendering

### Performance Issues
- Reduce the amount of data being displayed
- Use more specific time ranges
- Limit the number of widgets on a single dashboard
- Check your internet connection speed

## Getting Help

### In-App Help
- Click the "?" icon in the top navigation for contextual help
- Use the search function to find specific topics
- Access the keyboard shortcuts guide with Ctrl+/

### Support Resources
- Visit our documentation portal
- Check the community forums
- Submit a support ticket
- Schedule a support call for complex issues

## Contact Support

If you need further assistance:

- **Email**: support@auggdash26.com
- **Phone**: 1-800-DASHBOARD
- **Live Chat**: Available in the app (Hours: 9 AM - 6 PM EST)
- **Support Portal**: https://support.auggdash26.com
""",
                audience="all",
                estimated_time="5 min"
            )
        ]
    
    def generate_user_guide(self) -> str:
        """Generate the complete user guide"""
        guide = f"""
# AUGGDASH26 Dashboard System - User Guide

**Document Version:** 1.0  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**System Version:** 2.1.0

## Table of Contents

"""
        
        for i, section in enumerate(self.guide_sections, 1):
            guide += f"{i}. [{section.title}](#{section.title.lower().replace(' ', '-')})\n"
        
        guide += "\n"
        
        for i, section in enumerate(self.guide_sections, 1):
            guide += f"""
## {section.title}

**Audience:** {section.audience.title()}  
**Estimated Time:** {section.estimated_time}

{section.content}

"""
        
        return guide

class APIGuideGenerator:
    """Class for generating API documentation"""
    
    def __init__(self):
        self.endpoints = self._create_api_endpoints()
    
    def _create_api_endpoints(self) -> List[APIEndpoint]:
        """Create API endpoint definitions"""
        return [
            APIEndpoint(
                method="GET",
                path="/api/v1/dashboards",
                summary="List dashboards",
                description="Retrieve a list of dashboards with optional filtering and pagination.",
                parameters=[
                    {"name": "category", "type": "string", "required": False, "description": "Filter by category"},
                    {"name": "limit", "type": "integer", "required": False, "description": "Number of results to return (default: 50)"},
                    {"name": "offset", "type": "integer", "required": False, "description": "Number of results to skip (default: 0)"},
                    {"name": "sort", "type": "string", "required": False, "description": "Sort field (default: updated_at)"}
                ],
                responses={
                    "200": {"description": "Successful response", "content": "List of dashboards"},
                    "401": {"description": "Unauthorized", "content": "Invalid or missing authentication token"}
                },
                example_request="GET /api/v1/dashboards?category=ai-systems&limit=10",
                example_response="""
{
  "dashboards": [
    {
      "id": "dashboard-123",
      "name": "AI Performance Metrics",
      "category": "ai-systems",
      "description": "Performance metrics for AI systems",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z",
      "status": "active"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
"""
            ),
            APIEndpoint(
                method="POST",
                path="/api/v1/dashboards",
                summary="Create dashboard",
                description="Create a new dashboard with the provided configuration.",
                parameters=[],
                responses={
                    "201": {"description": "Dashboard created successfully"},
                    "400": {"description": "Invalid request body"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"}
                },
                example_request="""
POST /api/v1/dashboards
Content-Type: application/json

{
  "name": "New Dashboard",
  "category": "ai-systems",
  "description": "A new dashboard for AI metrics",
  "configuration": {
    "layout": {
      "rows": 2,
      "columns": 3
    },
    "widgets": [
      {
        "id": "widget-1",
        "type": "chart",
        "position": {"row": 0, "col": 0, "width": 2, "height": 1},
        "config": {
          "title": "Performance Chart",
          "dataSource": "api://performance-data",
          "chartType": "line"
        }
      }
    ]
  }
}
""",
                example_response="""
{
  "id": "dashboard-456",
  "name": "New Dashboard",
  "category": "ai-systems",
  "description": "A new dashboard for AI metrics",
  "configuration": {
    "layout": {
      "rows": 2,
      "columns": 3
    },
    "widgets": [
      {
        "id": "widget-1",
        "type": "chart",
        "position": {"row": 0, "col": 0, "width": 2, "height": 1},
        "config": {
          "title": "Performance Chart",
          "dataSource": "api://performance-data",
          "chartType": "line"
        }
      }
    ]
  },
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "status": "active"
}
"""
            ),
            APIEndpoint(
                method="GET",
                path="/api/v1/dashboards/{id}",
                summary="Get dashboard",
                description="Retrieve a specific dashboard by ID.",
                parameters=[
                    {"name": "id", "type": "string", "required": True, "description": "Dashboard ID"}
                ],
                responses={
                    "200": {"description": "Successful response", "content": "Dashboard details"},
                    "401": {"description": "Unauthorized"},
                    "404": {"description": "Dashboard not found"}
                },
                example_request="GET /api/v1/dashboards/dashboard-123",
                example_response="""
{
  "id": "dashboard-123",
  "name": "AI Performance Metrics",
  "category": "ai-systems",
  "description": "Performance metrics for AI systems",
  "configuration": {
    "layout": {
      "rows": 2,
      "columns": 3
    },
    "widgets": [
      {
        "id": "widget-1",
        "type": "chart",
        "position": {"row": 0, "col": 0, "width": 2, "height": 1},
        "config": {
          "title": "Performance Chart",
          "dataSource": "api://performance-data",
          "chartType": "line"
        }
      }
    ]
  },
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "status": "active"
}
"""
            ),
            APIEndpoint(
                method="PUT",
                path="/api/v1/dashboards/{id}",
                summary="Update dashboard",
                description="Update an existing dashboard with the provided configuration.",
                parameters=[
                    {"name": "id", "type": "string", "required": True, "description": "Dashboard ID"}
                ],
                responses={
                    "200": {"description": "Dashboard updated successfully"},
                    "400": {"description": "Invalid request body"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                    "404": {"description": "Dashboard not found"}
                },
                example_request="""
PUT /api/v1/dashboards/dashboard-123
Content-Type: application/json

{
  "name": "Updated AI Performance Metrics",
  "description": "Updated performance metrics for AI systems",
  "configuration": {
    "layout": {
      "rows": 3,
      "columns": 4
    },
    "widgets": [
      {
        "id": "widget-1",
        "type": "chart",
        "position": {"row": 0, "col": 0, "width": 2, "height": 1},
        "config": {
          "title": "Updated Performance Chart",
          "dataSource": "api://updated-performance-data",
          "chartType": "bar"
        }
      }
    ]
  }
}
""",
                example_response="""
{
  "id": "dashboard-123",
  "name": "Updated AI Performance Metrics",
  "category": "ai-systems",
  "description": "Updated performance metrics for AI systems",
  "configuration": {
    "layout": {
      "rows": 3,
      "columns": 4
    },
    "widgets": [
      {
        "id": "widget-1",
        "type": "chart",
        "position": {"row": 0, "col": 0, "width": 2, "height": 1},
        "config": {
          "title": "Updated Performance Chart",
          "dataSource": "api://updated-performance-data",
          "chartType": "bar"
        }
      }
    ]
  },
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z",
  "status": "active"
}
"""
            ),
            APIEndpoint(
                method="DELETE",
                path="/api/v1/dashboards/{id}",
                summary="Delete dashboard",
                description="Delete a specific dashboard by ID.",
                parameters=[
                    {"name": "id", "type": "string", "required": True, "description": "Dashboard ID"}
                ],
                responses={
                    "204": {"description": "Dashboard deleted successfully"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                    "404": {"description": "Dashboard not found"}
                },
                example_request="DELETE /api/v1/dashboards/dashboard-123",
                example_response=""
            ),
            APIEndpoint(
                method="GET",
                path="/api/v1/analytics/dashboards/{id}",
                summary="Get dashboard analytics",
                description="Retrieve analytics data for a specific dashboard.",
                parameters=[
                    {"name": "id", "type": "string", "required": True, "description": "Dashboard ID"},
                    {"name": "start_date", "type": "string", "required": False, "description": "Start date (ISO 8601 format)"},
                    {"name": "end_date", "type": "string", "required": False, "description": "End date (ISO 8601 format)"},
                    {"name": "granularity", "type": "string", "required": False, "description": "Time granularity (hour, day, week, month)"}
                ],
                responses={
                    "200": {"description": "Successful response", "content": "Analytics data"},
                    "401": {"description": "Unauthorized"},
                    "404": {"description": "Dashboard not found"}
                },
                example_request="GET /api/v1/analytics/dashboards/dashboard-123?start_date=2023-01-01T00:00:00Z&end_date=2023-01-31T23:59:59Z&granularity=day",
                example_response="""
{
  "dashboard_id": "dashboard-123",
  "period": {
    "start_date": "2023-01-01T00:00:00Z",
    "end_date": "2023-01-31T23:59:59Z"
  },
  "metrics": {
    "views": 1250,
    "unique_visitors": 420,
    "avg_session_duration": 125.5,
    "bounce_rate": 0.23,
    "page_views_per_session": 3.2
  },
  "time_series": [
    {
      "timestamp": "2023-01-01T00:00:00Z",
      "views": 150
    },
    {
      "timestamp": "2023-01-02T00:00:00Z",
      "views": 180
    }
  ]
}
"""
            )
        ]
    
    def generate_api_documentation(self) -> str:
        """Generate the complete API documentation"""
        api_doc = f"""
# AUGGDASH26 API Documentation

**Base URL:** `https://api.auggdash26.com`
**API Version:** v1
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Authentication

All API requests require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Content Types

- Request Content-Type: `application/json`
- Response Content-Type: `application/json`

## Rate Limiting

The API implements rate limiting:
- 1000 requests per hour per user
- 10,000 requests per hour per organization
- Exceeded requests return HTTP 429

## Error Handling

The API uses standard HTTP status codes:

- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error

Error responses follow this format:
```json
{{
  "error": {{
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": "Additional error details"
  }}
}}
```

## Endpoints

"""
        
        for endpoint in self.endpoints:
            api_doc += f"""
### {endpoint.method} {endpoint.path}

**Summary:** {endpoint.summary}

**Description:** {endpoint.description}

"""
            
            if endpoint.parameters:
                api_doc += "**Parameters:**\n\n"
                for param in endpoint.parameters:
                    required = " (required)" if param.get("required", False) else " (optional)"
                    api_doc += f"- `{param['name']}` ({param['type']}){required}: {param['description']}\n"
                api_doc += "\n"
            
            api_doc += "**Responses:**\n"
            for status_code, response in endpoint.responses.items():
                api_doc += f"- `{status_code}`: {response['description']}\n"
            api_doc += "\n"
            
            api_doc += f"""
**Example Request:**
```http
{endpoint.method} {endpoint.path}
```

```json
{endpoint.example_request}
```

**Example Response:**
```json
{endpoint.example_response}
```

"""
        
        api_doc += """
## SDKs and Libraries

Official SDKs are available for:

- JavaScript/Node.js
- Python
- Java
- Go
- .NET

## Webhooks

The API supports webhooks for real-time notifications:

- Dashboard created/updated/deleted
- User login/logout
- System alerts
- Data refresh events

Configure webhooks in your account settings.

## Changelog

### v1.0 (Current)
- Initial API release
- Dashboard management endpoints
- Analytics endpoints
- User management endpoints
"""
        
        return api_doc

class QuickStartGuide:
    """Class for generating quick start guides"""
    
    def generate_dashboard_quick_start(self) -> str:
        """Generate a quick start guide for creating dashboards"""
        return """
# Dashboard Quick Start Guide

## Create Your First Dashboard - 5 Minute Setup

### Step 1: Sign In (30 seconds)
1. Go to https://dashboard.auggdash26.com
2. Enter your credentials
3. Click "Sign In"

### Step 2: Create Dashboard (1 minute)
1. Click "New Dashboard" button
2. Enter dashboard name: "My First Dashboard"
3. Select category: "Personal"
4. Click "Create"

### Step 3: Add Your First Widget (2 minutes)
1. In the widget sidebar, click "Chart"
2. Drag the chart widget to the dashboard
3. Click on the widget to configure it
4. Set data source to "Sample Data"
5. Choose chart type: "Line Chart"
6. Set title: "My Metrics"

### Step 4: Customize Appearance (1 minute)
1. Click on the chart title to edit
2. Change the color scheme
3. Adjust the time range to "Last 7 days"

### Step 5: Save and Share (30 seconds)
1. Click "Save Dashboard" in the top toolbar
2. Click "Share" to get a shareable link
3. Copy the link and send to colleagues

## Next Steps

- [Add more widgets](#adding-widgets)
- [Connect to real data sources](#data-sources)
- [Set up alerts](#alerts)
- [Customize themes](#themes)

## Common Shortcuts

- `Ctrl + S`: Save dashboard
- `Ctrl + D`: Duplicate widget
- `Ctrl + Z`: Undo
- `?`: Show all shortcuts
"""
    
    def generate_api_quick_start(self) -> str:
        """Generate a quick start guide for API usage"""
        return """
# API Quick Start Guide

## Getting Started with the API - 10 Minute Setup

### Step 1: Get Your API Key (2 minutes)
1. Log into your AUGGDASH26 account
2. Go to Settings > API Keys
3. Click "Generate New Key"
4. Copy your API key (save it securely)

### Step 2: Test API Access (3 minutes)
Make your first API call using curl:

```bash
curl -X GET \\
  https://api.auggdash26.com/v1/dashboards \\
  -H 'Authorization: Bearer YOUR_API_KEY' \\
  -H 'Content-Type: application/json'
```

### Step 3: Create Your First Dashboard (4 minutes)
Use the API to create a dashboard:

```bash
curl -X POST \\
  https://api.auggdash26.com/v1/dashboards \\
  -H 'Authorization: Bearer YOUR_API_KEY' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "name": "API Created Dashboard",
    "category": "development",
    "description": "Dashboard created via API"
  }'
```

### Step 4: Retrieve Dashboard Data (1 minute)
Get the dashboard you just created:

```bash
curl -X GET \\
  https://api.auggdash26.com/v1/dashboards/DASHBOARD_ID \\
  -H 'Authorization: Bearer YOUR_API_KEY' \\
  -H 'Content-Type: application/json'
```

## Common API Patterns

### List Dashboards
```bash
GET /api/v1/dashboards?limit=10&category=ai-systems
```

### Update Dashboard
```bash
PUT /api/v1/dashboards/{id}
{
  "name": "Updated Dashboard Name",
  "description": "Updated description"
}
```

### Get Analytics
```bash
GET /api/v1/analytics/dashboards/{id}?start_date=2023-01-01&end_date=2023-01-31
```

## SDK Installation

### Python
```bash
pip install auggdash26-sdk
```

### JavaScript
```bash
npm install @auggdash26/sdk
```

## Error Troubleshooting

### 401 Unauthorized
- Verify your API key is correct
- Check that your API key hasn't expired
- Ensure you're using Bearer token format

### 400 Bad Request
- Validate your JSON format
- Check required fields are present
- Verify data types match API specification

### 429 Rate Limited
- Check your request rate
- Implement exponential backoff
- Consider batching requests
"""

# Example usage
if __name__ == "__main__":
    # Initialize user guide generator
    user_guide_gen = UserGuideGenerator()
    user_guide = user_guide_gen.generate_user_guide()
    print("User guide generated")
    
    # Initialize API guide generator
    api_guide_gen = APIGuideGenerator()
    api_doc = api_guide_gen.generate_api_documentation()
    print("API documentation generated")
    
    # Initialize quick start guide
    quick_start = QuickStartGuide()
    dashboard_quick_start = quick_start.generate_dashboard_quick_start()
    api_quick_start = quick_start.generate_api_quick_start()
    print("Quick start guides generated")
    
    # Combine all documentation
    full_documentation = f"""
# AUGGDASH26 Dashboard System - Complete User Documentation

{user_guide}

# API Documentation

{api_doc}

# Quick Start Guides

## Dashboard Quick Start

{dashboard_quick_start}

## API Quick Start

{api_quick_start}
"""
    
    # Save to file
    with open("user_api_documentation.md", "w", encoding="utf-8") as f:
        f.write(full_documentation)
    
    print("\nUser guides and API documentation created successfully")
    print("Documentation saved to 'user_api_documentation.md'")