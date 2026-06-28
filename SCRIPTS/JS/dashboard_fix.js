/**
 * AUGGDASH26 Dashboard System - JavaScript Fix
 * This script adds the missing functionality to the dashboard index page
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('AUGGDASH26 Dashboard System: Initializing dashboard functionality...');
    
    // Initialize dashboard system
    initializeDashboardSystem();
});

function initializeDashboardSystem() {
    // Add the missing JavaScript functions to the global scope
    window.openDashboard = openDashboard;
    window.openFolder = openFolder;
    window.searchDashboards = searchDashboards;
    window.toggleCategory = toggleCategory;
    
    // Initialize search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', searchDashboards);
        console.log('Search functionality initialized');
    } else {
        console.warn('Search input not found');
    }
    
    // Initialize category headers to be clickable
    initializeCategoryHeaders();
    
    // Show initial dashboard counts
    updateDashboardCounts();
    
    console.log('AUGGDASH26 Dashboard System: Initialization complete');
}

function openDashboard(filePath) {
    /**
     * Opens a specific dashboard in a new tab/window
     */
    if (!filePath) {
        console.error('No file path provided to openDashboard function');
        return;
    }
    
    try {
        // Ensure the file path is properly formatted
        let fullPath = filePath;
        if (!fullPath.startsWith('/') && !fullPath.startsWith('http')) {
            // If it doesn't start with / or http, assume it's a relative path
            fullPath = './' + fullPath;
        }
        
        console.log('Opening dashboard:', fullPath);
        window.open(fullPath, '_blank');
    } catch (error) {
        console.error('Error opening dashboard:', error);
    }
}

function openFolder(folderPath) {
    /**
     * Opens a folder view in the current window
     */
    if (!folderPath) {
        console.error('No folder path provided to openFolder function');
        return;
    }
    
    try {
        // Ensure the folder path is properly formatted
        let fullPath = folderPath;
        if (!fullPath.startsWith('/') && !fullPath.startsWith('http')) {
            // If it doesn't start with / or http, assume it's a relative path
            fullPath = './' + fullPath;
        }
        
        console.log('Opening folder:', fullPath);
        window.location.href = fullPath;
    } catch (error) {
        console.error('Error opening folder:', error);
    }
}

function searchDashboards() {
    /**
     * Filters dashboards based on the search input
     */
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) {
        console.error('Search input element not found');
        return;
    }
    
    const searchTerm = searchInput.value.toLowerCase().trim();
    
    // Get all dashboard cards
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    
    if (dashboardCards.length === 0) {
        console.warn('No dashboard cards found to search');
        return;
    }
    
    // Filter dashboards based on search term
    dashboardCards.forEach(card => {
        const titleElement = card.querySelector('h3');
        const filenameElement = card.querySelector('.filename');
        const metaElement = card.querySelector('.meta');
        
        const title = titleElement ? titleElement.textContent.toLowerCase() : '';
        const filename = filenameElement ? filenameElement.textContent.toLowerCase() : '';
        const meta = metaElement ? metaElement.textContent.toLowerCase() : '';
        
        // Check if search term matches any of the fields
        const matches = title.includes(searchTerm) || 
                       filename.includes(searchTerm) || 
                       meta.includes(searchTerm);
        
        // Show or hide the card based on whether it matches
        card.style.display = matches ? 'block' : 'none';
        
        // If a category has no visible dashboards, hide the entire category
        if (card.parentElement.classList.contains('dashboard-grid')) {
            const visibleCards = Array.from(card.parentElement.children)
                                    .filter(child => child.style.display !== 'none');
            
            // Show/hide the category based on if it has visible dashboards
            const categoryHeader = card.parentElement.previousElementSibling;
            if (categoryHeader && categoryHeader.classList.contains('category-header')) {
                const categoryHasVisibleDashboards = visibleCards.length > 0 || searchTerm === '';
                // Don't hide the category header, just ensure it's visible
            }
        }
    });
    
    console.log(`Search completed. Showing ${Array.from(dashboardCards).filter(card => card.style.display !== 'none').length} dashboards.`);
}

function toggleCategory(categoryId) {
    /**
     * Toggles the visibility of a category's dashboard grid
     */
    if (!categoryId) {
        console.error('No category ID provided to toggleCategory function');
        return;
    }
    
    const categoryGrid = document.getElementById(`category-${categoryId}`);
    if (!categoryGrid) {
        console.error(`Category grid with ID 'category-${categoryId}' not found`);
        return;
    }
    
    // Toggle the display of the category grid
    if (categoryGrid.style.display === 'none' || categoryGrid.style.display === '') {
        categoryGrid.style.display = 'grid';
        console.log(`Category '${categoryId}' expanded`);
    } else {
        categoryGrid.style.display = 'none';
        console.log(`Category '${categoryId}' collapsed`);
    }
}

function initializeCategoryHeaders() {
    /**
     * Makes category headers clickable to expand/collapse their content
     */
    const categoryHeaders = document.querySelectorAll('.category-header');
    
    categoryHeaders.forEach(header => {
        // Check if click handler is already attached
        if (!header.dataset.initialized) {
            header.style.cursor = 'pointer';
            
            // Add click event to toggle category
            header.addEventListener('click', function() {
                // Get the category ID from the data attribute or from the header text
                let categoryId = this.getAttribute('data-category');
                
                if (!categoryId) {
                    // Try to extract category from the header text
                    const headerText = this.querySelector('h2');
                    if (headerText) {
                        // Get the text and extract category (usually the first word after emoji)
                        const text = headerText.textContent.trim();
                        const parts = text.split(' ');
                        if (parts.length > 1) {
                            categoryId = parts[1].toLowerCase(); // Take the category name after emoji
                        } else {
                            categoryId = text.toLowerCase();
                        }
                    }
                }
                
                if (categoryId) {
                    toggleCategory(categoryId);
                } else {
                    console.error('Could not determine category ID for header:', header);
                }
            });
            
            // Mark as initialized
            header.dataset.initialized = 'true';
        }
    });
    
    console.log(`Initialized ${categoryHeaders.length} category headers`);
}

function updateDashboardCounts() {
    /**
     * Updates the dashboard count displays in the category headers
     */
    const categories = document.querySelectorAll('.category');
    
    categories.forEach(category => {
        const header = category.querySelector('.category-header');
        const grid = category.querySelector('.dashboard-grid');
        
        if (header && grid) {
            const dashboardCount = grid.querySelectorAll('.dashboard-card').length;
            const countSpan = header.querySelector('.count');
            
            if (countSpan) {
                countSpan.textContent = `${dashboardCount} dashboards`;
            }
        }
    });
    
    // Update total dashboard count
    const allDashboards = document.querySelectorAll('.dashboard-card');
    const totalDashboardsElement = document.querySelector('.stat-card h3'); // This is a simplification
    
    if (allDashboards.length > 0) {
        console.log(`Total dashboards found: ${allDashboards.length}`);
    }
}

// Additional utility functions for enhanced functionality

function highlightSearchTerms() {
    /**
     * Highlights search terms in the dashboard cards
     */
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    const searchTerm = searchInput.value.trim();
    if (!searchTerm) return;
    
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    
    dashboardCards.forEach(card => {
        // Reset any previous highlights
        resetHighlights(card);
        
        if (card.style.display !== 'none') { // Only highlight visible cards
            highlightInElement(card, searchTerm);
        }
    });
}

function resetHighlights(element) {
    /**
     * Removes highlighting from an element
     */
    const highlighted = element.querySelectorAll('.highlight');
    highlighted.forEach(span => {
        const parent = span.parentNode;
        parent.replaceChild(document.createTextNode(span.textContent), span);
    });
}

function highlightInElement(element, searchTerm) {
    /**
     * Highlights a search term within an element
     */
    const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    const nodesToHighlight = [];
    let node;
    
    while (node = walker.nextNode()) {
        if (node.nodeValue.toLowerCase().includes(searchTerm.toLowerCase())) {
            nodesToHighlight.push(node);
        }
    }
    
    nodesToHighlight.forEach(textNode => {
        const parent = textNode.parentNode;
        const text = textNode.nodeValue;
        const lowerText = text.toLowerCase();
        const lowerSearch = searchTerm.toLowerCase();
        const index = lowerText.indexOf(lowerSearch);
        
        if (index !== -1) {
            const before = text.substring(0, index);
            const match = text.substring(index, index + searchTerm.length);
            const after = text.substring(index + searchTerm.length);
            
            const beforeNode = document.createTextNode(before);
            const highlightNode = document.createElement('span');
            highlightNode.className = 'highlight';
            highlightNode.style.backgroundColor = '#ffeb3b';
            highlightNode.style.fontWeight = 'bold';
            highlightNode.textContent = match;
            const afterNode = document.createTextNode(after);
            
            parent.replaceChild(beforeNode, textNode);
            parent.insertBefore(highlightNode, beforeNode.nextSibling);
            parent.insertBefore(afterNode, highlightNode.nextSibling);
        }
    });
}

// Add CSS for highlighting if it doesn't exist
function addHighlightStyles() {
    if (!document.querySelector('#dashboard-highlight-styles')) {
        const style = document.createElement('style');
        style.id = 'dashboard-highlight-styles';
        style.textContent = `
            .highlight {
                background-color: #ffeb3b !important;
                font-weight: bold !important;
                padding: 1px 2px !important;
                border-radius: 2px !important;
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize additional features
addHighlightStyles();

// Add debouncing to search for better performance
let searchTimeout;
function debouncedSearchDashboards() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        searchDashboards();
        highlightSearchTerms();
    }, 300); // Wait 300ms after user stops typing
}

// If search input exists, attach the debounced version
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.removeEventListener('keyup', searchDashboards);
        searchInput.addEventListener('keyup', debouncedSearchDashboards);
    }
});

console.log('AUGGDASH26 Dashboard System: JavaScript functionality loaded');