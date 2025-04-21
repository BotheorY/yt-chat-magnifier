/**
 * YT Chat Magnifier Style Loader
 * Carica dinamicamente i fogli di stile in base alla modalità selezionata
 */

// Funzione per caricare i fogli di stile in base alla modalità
function loadStylesheets(styleMode) {
    // Rimuovi eventuali fogli di stile precedenti
    removeStylesheets();
    
    // Carica i fogli di stile appropriati in base alla modalità
    if (styleMode === 'dark') {
        loadStylesheet('/static/css/yt-chat-magnifier-dark.css');
        loadStylesheet('/static/css/ytcm-message-overlay-dark.css');
        loadStylesheet('/static/css/yt-emoji-dark.css');
    } else if (styleMode === 'high-contrast') {
        loadStylesheet('/static/css/yt-chat-magnifier-high-contrast.css');
        loadStylesheet('/static/css/ytcm-message-overlay-high-contrast.css');
        loadStylesheet('/static/css/yt-emoji-high-contrast.css');
    } else {
        // Modalità standard - usa i fogli di stile originali
        loadStylesheet('/static/css/yt-chat-magnifier.css');
        loadStylesheet('/static/css/ytcm-message-overlay.css');
        loadStylesheet('/static/css/yt-emoji.css');
    }
}

// Funzione per caricare un singolo foglio di stile
function loadStylesheet(href) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    link.className = 'ytcm-dynamic-stylesheet';
    document.head.appendChild(link);
}

// Funzione per rimuovere i fogli di stile dinamici
function removeStylesheets() {
    const stylesheets = document.querySelectorAll('.ytcm-dynamic-stylesheet');
    stylesheets.forEach(sheet => sheet.remove());
}

// Carica i fogli di stile all'avvio in base al valore della costante YTCM_LAYOUT_STYLE
document.addEventListener('DOMContentLoaded', function() {
    // Il valore di YTCM_LAYOUT_STYLE viene passato dal server tramite una variabile JavaScript
    if (typeof ytcmLayoutStyle !== 'undefined') {
        loadStylesheets(ytcmLayoutStyle);
    } else {
        // Fallback alla modalità standard se la variabile non è definita
        loadStylesheets('standard');
    }
});