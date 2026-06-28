javascript:(function() {
    // Function to extract GitHub repository links from YouTube video description
    function extractGitHubLinks() {
        // Array to store found GitHub links
        let githubLinks = [];
        
        // Get all links from the current page
        const allLinks = document.querySelectorAll('a');
        
        // Regular expression to match GitHub repository URLs
        const githubRegex = /https:\/\/github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_.-]+/g;
        
        // Loop through all links and check if they match the GitHub pattern
        allLinks.forEach(link => {
            const href = link.href;
            if (githubRegex.test(href)) {
                githubLinks.push(href);
            }
        });
        
        // Also search in video description elements if they exist
        const descriptionElements = document.querySelectorAll('#description, .yt-core-attributed-string, #content-text');
        descriptionElements.forEach(element => {
            const text = element.innerText || element.textContent;
            const matches = text.match(githubRegex);
            if (matches) {
                matches.forEach(match => {
                    if (!githubLinks.includes(match)) {
                        githubLinks.push(match);
                    }
                });
            }
        });
        
        // Remove duplicates
        githubLinks = [...new Set(githubLinks)];
        
        // Display the results
        if (githubLinks.length > 0) {
            console.log('Found GitHub repositories:');
            githubLinks.forEach((link, index) => {
                console.log(`${index + 1}. ${link}`);
            });
            
            // Create a simple popup with the links
            const results = githubLinks.map((link, index) => 
                `<a href="${link}" target="_blank">${link}</a><br>`
            ).join('');
            
            const popup = document.createElement('div');
            popup.innerHTML = `
                <div style="position: fixed; top: 20px; right: 20px; z-index: 9999; 
                    background: white; border: 1px solid #ccc; padding: 15px; 
                    max-width: 400px; max-height: 500px; overflow-y: auto; 
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                    <h3>Found GitHub Repositories:</h3>
                    ${results}
                    <button onclick="this.parentElement.remove()" 
                        style="margin-top: 10px; padding: 5px 10px;">Close</button>
                </div>
            `;
            document.body.appendChild(popup);
        } else {
            alert('No GitHub repositories found on this page.');
        }
    }
    
    // Execute the function
    extractGitHubLinks();
})();