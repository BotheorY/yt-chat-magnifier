/**
 * YouTube Emoji Parser
 * 
 * Questo script gestisce il parsing e la visualizzazione delle emoticon di YouTube
 * nelle chat durante le live streaming.
 */

const ytEmojiMap = {
    ':hand-pink-waving:': '👋',
    ':face-blue-smiling:': '😊',
    ':face-red-droopy-eyes:': '😴',
    ':thumbs-up:': '👍',
    ':thumbs-down:': '👎',
    ':heart:': '❤️',
    ':fire:': '🔥',
    ':clapping-hands:': '👏',
    ':face-with-tears-of-joy:': '😂',
    ':face-blowing-a-kiss:': '😘',
    ':thinking-face:': '🤔',
    ':face-with-rolling-eyes:': '🙄',
    ':face-with-open-mouth:': '😮',
    ':smiling-face-with-heart-eyes:': '😍',
    ':face-with-symbols-on-mouth:': '🤬',
    ':party-popper:': '🎉',
    ':rocket:': '🚀',
    ':hundred-points:': '💯',
    ':eyes:': '👀'
};

/**
 * Converte i codici delle emoticon di YouTube in emoji Unicode
 * @param {string} text - Il testo del messaggio da processare
 * @returns {string} - Il testo con le emoticon sostituite
 */
function parseYouTubeEmojis(text) {
    if (!text) return text;
    
    let parsedText = text;
    
    // Cerca tutti i codici di emoticon nel formato :nome-emoticon:
    const emojiRegex = /:([-a-z]+):/g;
    
    // Sostituisce i codici trovati con le relative emoji
    parsedText = parsedText.replace(emojiRegex, (match) => {
        return ytEmojiMap[match] || match;
    });
    
    return parsedText;
}

/**
 * Versione avanzata che sostituisce i codici delle emoticon con elementi HTML
 * per una visualizzazione più ricca e personalizzabile
 * @param {string} text - Il testo del messaggio da processare
 * @returns {string} - Il testo HTML con le emoticon sostituite
 */
function parseYouTubeEmojisToHTML(text) {
    if (!text) return text;
    
    let parsedText = text;
    
    // Cerca tutti i codici di emoticon nel formato :nome-emoticon:
    const emojiRegex = /:([-a-z]+):/g;
    
    // Sostituisce i codici trovati con elementi HTML
    parsedText = parsedText.replace(emojiRegex, (match) => {
        if (ytEmojiMap[match]) {
            return `<span class="yt-emoji" title="${match}">${ytEmojiMap[match]}</span>`;
        }
        return match;
    });
    
    return parsedText;
}