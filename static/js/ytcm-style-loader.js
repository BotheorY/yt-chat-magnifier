/**
 * YT Chat Magnifier Style Loader
 * Dynamically loads stylesheets based on the selected mode
 */

// Function to load stylesheets based on the mode
function loadStylesheets(styleMode) {
    // Remove any previous stylesheets
    removeStylesheets();
    
    // Load appropriate stylesheets based on the mode
    if (styleMode === 'dark') {
        loadStylesheet('/static/css/yt-chat-magnifier-dark.css');
        loadStylesheet('/static/css/ytcm-message-overlay-dark.css');
        loadStylesheet('/static/css/yt-emoji-dark.css');
    } else if (styleMode === 'high-contrast') {
        loadStylesheet('/static/css/yt-chat-magnifier-high-contrast.css');
        loadStylesheet('/static/css/ytcm-message-overlay-high-contrast.css');
        loadStylesheet('/static/css/yt-emoji-high-contrast.css');
    } else {
        // Standard mode - use original stylesheets
        loadStylesheet('/static/css/yt-chat-magnifier.css');
        loadStylesheet('/static/css/ytcm-message-overlay.css');
        loadStylesheet('/static/css/yt-emoji.css');
    }
}

// Function to load a single stylesheet
function loadStylesheet(href) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    link.className = 'ytcm-dynamic-stylesheet';
    document.head.appendChild(link);
}

// Function to remove dynamic stylesheets
function removeStylesheets() {
    const stylesheets = document.querySelectorAll('.ytcm-dynamic-stylesheet');
    stylesheets.forEach(sheet => sheet.remove());
}

// Load stylesheets on startup based on the YTCM_LAYOUT_STYLE constant value
document.addEventListener('DOMContentLoaded', function() {
    // The value of YTCM_LAYOUT_STYLE is passed from the server via a JavaScript variable
    if (typeof ytcmLayoutStyle !== 'undefined') {
        loadStylesheets(ytcmLayoutStyle);
    } else {
        // Fallback to standard mode if the variable is not defined
        loadStylesheets('standard');
    }
});