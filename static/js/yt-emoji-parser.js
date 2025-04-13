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
    ':eyes:': '👀',
    ':face-with-hand-over-mouth:': '🤭',
    ':face-with-monocle:': '🧐',
    ':face-with-raised-eyebrow:': '🤨',
    ':face-with-steam-from-nose:': '😤',
    ':face-with-tears:': '😢',
    ':face-screaming-in-fear:': '😱',
    ':face-vomiting:': '🤮',
    ':face-with-medical-mask:': '😷',
    ':money-mouth-face:': '🤑',
    ':nerd-face:': '🤓',
    ':smiling-face-with-sunglasses:': '😎',
    ':zany-face:': '🤪',
    ':shushing-face:': '🤫',
    ':sleeping-face:': '😴',
    ':face-with-tongue:': '😛',
    ':winking-face:': '😉',
    ':angry-face:': '😠',
    ':face-with-symbols-over-mouth:': '🤬',
    ':exploding-head:': '🤯',
    ':star-struck:': '🤩',
    ':face-holding-back-tears:': '🥹',
    ':saluting-face:': '🫡',
    ':melting-face:': '🫠',
    ':face-with-peeking-eye:': '🫣',
    ':face-with-diagonal-mouth:': '🫤',
    ':dotted-line-face:': '🫥',
    ':smiling-face-with-tear:': '🥲',
    ':clown-face:': '🤡',
    ':lying-face:': '🤥',
    ':sneezing-face:': '🤧',
    ':raised-hands:': '🙌',
    ':folded-hands:': '🙏',
    ':handshake:': '🤝',
    ':ok-hand:': '👌',
    ':victory-hand:': '✌️',
    ':crossed-fingers:': '🤞',
    ':love-you-gesture:': '🤟',
    ':call-me-hand:': '🤙',
    ':backhand-index-pointing-up:': '👆',
    ':middle-finger:': '🖕',
    ':clapping-hands:': '👏',
    ':raising-hands:': '🙌',
    ':crown:': '👑',
    ':trophy:': '🏆',
    ':first-place-medal:': '🥇',
    ':gem-stone:': '💎',
    ':money-bag:': '💰',
    ':gift:': '🎁',
    ':confetti-ball:': '🎊',
    ':sparkles:': '✨',
    ':dizzy:': '💫',
    ':collision:': '💥',
    ':sweat-droplets:': '💦',
    ':dash:': '💨',
    ':check-mark:': '✅',
    ':cross-mark:': '❌',
    ':warning:': '⚠️',
    ':red-heart:': '❤️',
    ':orange-heart:': '🧡',
    ':yellow-heart:': '💛',
    ':green-heart:': '💚',
    ':blue-heart:': '💙',
    ':purple-heart:': '💜',
    ':black-heart:': '🖤',
    ':broken-heart:': '💔',
    ':growing-heart:': '💗',
    ':beating-heart:': '💓',
    ':revolving-hearts:': '💞',
    ':two-hearts:': '💕',
    ':heart-decoration:': '💟',
    ':zzz:': '💤',
    ':musical-notes:': '🎵',
    ':speech-balloon:': '💬',
    ':thought-balloon:': '💭',
    ':light-bulb:': '💡'
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