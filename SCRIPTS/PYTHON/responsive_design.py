"""
Responsive Design Implementation for AUGGDASH26 Dashboard System
This module implements responsive design principles to ensure the dashboard
works well on all screen sizes and devices.
"""

from typing import Dict, List, Tuple
import json

class ResponsiveDesignManager:
    """Main class for managing responsive design implementation"""
    
    def __init__(self):
        self.breakpoints = {
            'mobile_small': 320,      # Small mobile devices
            'mobile': 480,            # Mobile devices
            'tablet_portrait': 768,   # Tablet portrait
            'tablet_landscape': 1024, # Tablet landscape
            'desktop_small': 1200,    # Small desktop
            'desktop': 1440,          # Desktop
            'desktop_large': 1920     # Large desktop
        }
        
        self.grid_system = {
            'columns': 12,
            'gutter': '15px',
            'max_width': '1200px'
        }
    
    def generate_responsive_css(self) -> str:
        """Generate responsive CSS for the dashboard system"""
        css = """
/* Responsive Design for AUGGDASH26 Dashboard System */
:root {
    --primary-color: #4a90e2;
    --secondary-color: #50e3c2;
    --background-color: #f5f7fa;
    --text-color: #333;
    --border-color: #dcdfe6;
    --shadow: 0 2px 8px rgba(0,0,0,0.1);
    --border-radius: 4px;
    --transition: all 0.3s ease;
}

/* Base styles */
* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    margin: 0;
    padding: 0;
    background-color: var(--background-color);
    color: var(--text-color);
    line-height: 1.6;
}

.container {
    width: 100%;
    max-width: var(--max-width);
    margin: 0 auto;
    padding: 0 15px;
}

/* Grid System */
.grid {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -var(--gutter);
}

.grid > [class*="col-"] {
    padding: 0 var(--gutter);
    margin-bottom: 15px;
}

/* Column sizes */
.col-1 { flex: 0 0 8.333333%; max-width: 8.333333%; }
.col-2 { flex: 0 0 16.666667%; max-width: 16.666667%; }
.col-3 { flex: 0 0 25%; max-width: 25%; }
.col-4 { flex: 0 0 33.333333%; max-width: 33.333333%; }
.col-5 { flex: 0 0 41.666667%; max-width: 41.666667%; }
.col-6 { flex: 0 0 50%; max-width: 50%; }
.col-7 { flex: 0 0 58.333333%; max-width: 58.333333%; }
.col-8 { flex: 0 0 66.666667%; max-width: 66.666667%; }
.col-9 { flex: 0 0 75%; max-width: 75%; }
.col-10 { flex: 0 0 83.333333%; max-width: 83.333333%; }
.col-11 { flex: 0 0 91.666667%; max-width: 91.666667%; }
.col-12 { flex: 0 0 100%; max-width: 100%; }

/* Dashboard layout */
.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 0;
    border-bottom: 1px solid var(--border-color);
}

.dashboard-content {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
    margin-top: 20px;
}

.dashboard-sidebar {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    padding: 20px;
    height: fit-content;
}

.dashboard-main {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    padding: 20px;
}

/* Card styles */
.card {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    padding: 20px;
    margin-bottom: 20px;
    transition: var(--transition);
}

.card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border-color);
}

.card-title {
    margin: 0;
    font-size: 1.2em;
    font-weight: 600;
}

/* Table styles */
.responsive-table {
    width: 100%;
    border-collapse: collapse;
    overflow-x: auto;
    display: block;
}

.responsive-table table {
    width: 100%;
    min-width: 600px;
}

.responsive-table th,
.responsive-table td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

.responsive-table th {
    background-color: #f8f9fa;
    font-weight: 600;
}

/* Button styles */
.btn {
    display: inline-block;
    padding: 8px 16px;
    background-color: var(--primary-color);
    color: white;
    text-decoration: none;
    border-radius: var(--border-radius);
    border: none;
    cursor: pointer;
    transition: var(--transition);
    font-size: 14px;
}

.btn:hover {
    opacity: 0.9;
}

.btn-secondary {
    background-color: #6c757d;
}

.btn-success {
    background-color: #28a745;
}

.btn-danger {
    background-color: #dc3545;
}

/* Navigation */
.nav {
    display: flex;
    list-style: none;
    padding: 0;
    margin: 0;
}

.nav-item {
    margin-right: 20px;
}

.nav-link {
    text-decoration: none;
    color: var(--text-color);
    padding: 10px 15px;
    border-radius: var(--border-radius);
    transition: var(--transition);
}

.nav-link:hover,
.nav-link.active {
    background-color: var(--primary-color);
    color: white;
}

/* Mobile menu */
.mobile-menu-toggle {
    display: none;
    background: none;
    border: none;
    font-size: 1.5em;
    cursor: pointer;
}

/* Utility classes */
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-left { text-align: left; }
.mb-1 { margin-bottom: 5px; }
.mb-2 { margin-bottom: 10px; }
.mb-3 { margin-bottom: 15px; }
.mb-4 { margin-bottom: 20px; }
.mt-1 { margin-top: 5px; }
.mt-2 { margin-top: 10px; }
.mt-3 { margin-top: 15px; }
.mt-4 { margin-top: 20px; }
.p-1 { padding: 5px; }
.p-2 { padding: 10px; }
.p-3 { padding: 15px; }
.p-4 { padding: 20px; }

/* Hide on mobile */
.hidden-mobile {
    display: block;
}

/* Show on mobile */
.mobile-only {
    display: none;
}

/* Responsive adjustments for different screen sizes */
"""
        
        # Add media queries for different breakpoints
        for bp_name, bp_value in self.breakpoints.items():
            css += f"""
/* {bp_name.replace('_', ' ').title()} and above */
@media (min-width: {bp_value}px) {{
    .container {{
        max-width: {min(bp_value - 40, 1200)}px;
    }}
    
    .dashboard-content {{
        grid-template-columns: 300px 1fr;
    }}
    
    .hidden-{bp_name.replace('_', '-')} {{
        display: none;
    }}
    
    .show-{bp_name.replace('_', '-')} {{
        display: block;
    }}
}}
"""
        
        # Mobile-specific styles
        css += """
/* Mobile styles */
@media (max-width: 767px) {
    .dashboard-header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .dashboard-header > * {
        margin-bottom: 10px;
        width: 100%;
    }
    
    .dashboard-content {
        grid-template-columns: 1fr;
    }
    
    .nav {
        flex-direction: column;
    }
    
    .nav-item {
        margin-right: 0;
        margin-bottom: 5px;
    }
    
    .mobile-menu-toggle {
        display: block;
        position: absolute;
        top: 20px;
        right: 20px;
    }
    
    .hidden-mobile {
        display: none;
    }
    
    .mobile-only {
        display: block;
    }
    
    .grid {
        flex-direction: column;
    }
    
    .grid > [class*="col-"] {
        flex: 0 0 100%;
        max-width: 100%;
    }
    
    .card-header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .card-header > * {
        margin-bottom: 10px;
    }
    
    .responsive-table {
        overflow-x: auto;
    }
    
    .responsive-table table {
        min-width: 100%;
    }
    
    .responsive-table th,
    .responsive-table td {
        padding: 8px;
        font-size: 0.9em;
    }
}

/* Tablet styles */
@media (min-width: 768px) and (max-width: 1023px) {
    .dashboard-content {
        grid-template-columns: 250px 1fr;
    }
    
    .card {
        padding: 15px;
    }
    
    .card-title {
        font-size: 1.1em;
    }
}

/* Large screen optimizations */
@media (min-width: 1440px) {
    .dashboard-content {
        grid-template-columns: 350px 1fr;
    }
    
    .container {
        max-width: 1400px;
    }
}

/* High DPI displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    body {
        font-weight: 450;
    }
}

/* Reduced motion for users who prefer less animation */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    :root {
        --border-color: #000;
        --shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .card {
        border: 1px solid var(--border-color);
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --background-color: #1a1a1a;
        --text-color: #e0e0e0;
        --border-color: #444;
    }
    
    body {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    .card,
    .dashboard-sidebar,
    .dashboard-main {
        background: #2d2d2d;
        color: var(--text-color);
    }
    
    .responsive-table th {
        background-color: #3a3a3a;
    }
}
"""
        
        return css
    
    def generate_responsive_html_template(self) -> str:
        """Generate a responsive HTML template for dashboards"""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AUGGDASH26 Dashboard</title>
    <style>
    """ + self.generate_responsive_css() + """
    </style>
</head>
<body>
    <div class="container">
        <header class="dashboard-header">
            <h1 class="dashboard-title">AUGGDASH26 Dashboard</h1>
            <button class="mobile-menu-toggle">☰</button>
            <nav class="nav hidden-mobile">
                <li class="nav-item"><a href="#" class="nav-link active">Dashboard</a></li>
                <li class="nav-item"><a href="#" class="nav-link">Analytics</a></li>
                <li class="nav-item"><a href="#" class="nav-link">Reports</a></li>
                <li class="nav-item"><a href="#" class="nav-link">Settings</a></li>
            </nav>
            <div class="header-actions">
                <button class="btn btn-secondary">Export</button>
                <button class="btn">Refresh</button>
            </div>
        </header>
        
        <div class="dashboard-content">
            <aside class="dashboard-sidebar">
                <h3>Filters</h3>
                <div class="filter-group">
                    <label for="date-range">Date Range</label>
                    <select id="date-range" class="form-control">
                        <option>Last 7 days</option>
                        <option selected>Last 30 days</option>
                        <option>Last 90 days</option>
                    </select>
                </div>
                
                <div class="filter-group mt-3">
                    <label for="category">Category</label>
                    <select id="category" class="form-control">
                        <option>All Categories</option>
                        <option>AI Systems</option>
                        <option>Archon</option>
                        <option>Crypto</option>
                        <option>Development</option>
                    </select>
                </div>
                
                <div class="filter-group mt-3">
                    <label for="status">Status</label>
                    <select id="status" class="form-control">
                        <option>All Statuses</option>
                        <option>Active</option>
                        <option>Inactive</option>
                        <option>Warning</option>
                    </select>
                </div>
            </aside>
            
            <main class="dashboard-main">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Dashboard Overview</h2>
                        <div class="card-actions">
                            <button class="btn btn-secondary">View Details</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="grid">
                            <div class="col-6 col-md-3">
                                <div class="metric-card">
                                    <h3>12,402</h3>
                                    <p>Total Dashboards</p>
                                </div>
                            </div>
                            <div class="col-6 col-md-3">
                                <div class="metric-card">
                                    <h3>99.25%</h3>
                                    <p>Uptime</p>
                                </div>
                            </div>
                            <div class="col-6 col-md-3">
                                <div class="metric-card">
                                    <h3>1,240</h3>
                                    <p>New This Month</p>
                                </div>
                            </div>
                            <div class="col-6 col-md-3">
                                <div class="metric-card">
                                    <h3>24.5s</h3>
                                    <p>Avg. Load Time</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Recent Dashboards</h2>
                        <div class="card-actions">
                            <button class="btn">View All</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="responsive-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Category</th>
                                        <th>Status</th>
                                        <th>Last Updated</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>AI Performance Metrics</td>
                                        <td>AI Systems</td>
                                        <td><span class="status active">Active</span></td>
                                        <td>2023-06-15</td>
                                        <td>
                                            <button class="btn btn-secondary">View</button>
                                            <button class="btn btn-danger">Delete</button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Crypto Market Analysis</td>
                                        <td>Crypto</td>
                                        <td><span class="status warning">Warning</span></td>
                                        <td>2023-06-14</td>
                                        <td>
                                            <button class="btn btn-secondary">View</button>
                                            <button class="btn btn-danger">Delete</button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Development Pipeline</td>
                                        <td>Development</td>
                                        <td><span class="status active">Active</span></td>
                                        <td>2023-06-13</td>
                                        <td>
                                            <button class="btn btn-secondary">View</button>
                                            <button class="btn btn-danger">Delete</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>
    
    <script>
        // Mobile menu toggle
        document.querySelector('.mobile-menu-toggle').addEventListener('click', function() {
            const nav = document.querySelector('.nav');
            nav.classList.toggle('show-mobile');
        });
        
        // Responsive table handling
        document.querySelectorAll('.responsive-table').forEach(table => {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-wrapper';
            wrapper.style.overflowX = 'auto';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        });
    </script>
</body>
</html>"""
        
        return html
    
    def get_responsive_utilities(self) -> Dict[str, str]:
        """Get responsive utility classes and functions"""
        return {
            'breakpoints': json.dumps(self.breakpoints),
            'grid_system': json.dumps(self.grid_system),
            'css_framework': self.generate_responsive_css(),
            'html_template': self.generate_responsive_html_template()
        }

class ResponsiveImageManager:
    """Manage responsive images for the dashboard"""
    
    def generate_picture_element(self, image_sources: List[Tuple[str, str]], alt_text: str) -> str:
        """Generate a responsive picture element with multiple sources"""
        picture_html = '<picture>\n'
        
        # Add sources in descending order (largest first)
        for src, media_query in reversed(image_sources):
            picture_html += f'  <source srcset="{src}" media="{media_query}">\n'
        
        # Add default image
        default_src = image_sources[0][0]  # Use the first (smallest) image as default
        picture_html += f'  <img src="{default_src}" alt="{alt_text}" style="width:100%;height:auto;">\n'
        picture_html += '</picture>'
        
        return picture_html
    
    def generate_image_sizes(self, base_name: str, formats: List[str] = None) -> List[Tuple[str, str]]:
        """Generate different sizes of an image for responsive loading"""
        if formats is None:
            formats = ['webp', 'jpg']
        
        sizes = []
        
        # Define breakpoints and corresponding image sizes
        breakpoints = [
            (1920, '(min-width: 1200px)'),
            (1440, '(min-width: 1024px)'),
            (1024, '(min-width: 768px)'),
            (768, '(min-width: 480px)'),
            (480, 'default')
        ]
        
        for width, media_query in breakpoints:
            for fmt in formats:
                filename = f"{base_name}_{width}w.{fmt}"
                if media_query == 'default':
                    sizes.append((filename, '(max-width: 479px)'))
                else:
                    sizes.append((filename, media_query))
        
        return sizes

# Example usage
if __name__ == "__main__":
    # Initialize responsive design manager
    responsive_manager = ResponsiveDesignManager()
    
    # Generate responsive CSS
    css = responsive_manager.generate_responsive_css()
    print("Responsive CSS generated successfully")
    
    # Generate responsive HTML template
    html_template = responsive_manager.generate_responsive_html_template()
    print("Responsive HTML template generated successfully")
    
    # Get responsive utilities
    utilities = responsive_manager.get_responsive_utilities()
    print("Responsive utilities prepared")
    
    # Example of responsive image management
    image_manager = ResponsiveImageManager()
    
    # Generate responsive image sources
    image_sources = image_manager.generate_image_sizes("dashboard_chart")
    picture_element = image_manager.generate_picture_element(
        image_sources[:3],  # Use first 3 sizes for example
        "Dashboard performance chart"
    )
    print("Responsive image element generated")
    
    # Save CSS to file
    with open("responsive_dashboard.css", "w") as f:
        f.write(css)
    
    # Save HTML template to file
    with open("responsive_dashboard_template.html", "w") as f:
        f.write(html_template)
    
    print("\nResponsive design implementation completed")
    print(f"CSS file created: responsive_dashboard.css")
    print(f"HTML template created: responsive_dashboard_template.html")
    print(f"Breakpoints defined: {list(responsive_manager.breakpoints.keys())}")