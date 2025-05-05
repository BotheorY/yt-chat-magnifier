let lastNMessages = 0;
let lastNMessagesFull = 0;
let preventSingleClick = false;
let pollingInterval;
let apiQuotaErrMsg = false;
let questionsOnly = 1; // Default value is 1 (on)

// Function to set a cookie
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + value + expires + "; path=/";
}

// Function to get a cookie
function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

$(document).ready(function() {
    // Initialize questions button state from cookie
    const savedQuestionsOnly = getCookie('questionsOnly');
    if (savedQuestionsOnly !== null) {
        questionsOnly = parseInt(savedQuestionsOnly);
    }
    
    // Update button appearance based on saved state
    updateQuestionsButtonState();
    
    // Questions button click handler
    $('#questions-btn').click(function() {
        // Toggle state
        questionsOnly = questionsOnly === 0 ? 1 : 0;
        
        // Update button appearance
        updateQuestionsButtonState();
        
        // Save state to cookie
        setCookie('questionsOnly', questionsOnly, 30); // Save for 30 days
    });
    
    // Function to update button appearance
    function updateQuestionsButtonState() {
        const questionsBtn = $('#questions-btn');
        questionsBtn.attr('data-questions-only', questionsOnly);
        
        if (questionsOnly !== 0) {
            questionsBtn.addClass('questions-btn-on').removeClass('questions-btn-off');
            $('#message-list').show();
            $('#message-list-full').hide();
        } else {
            questionsBtn.addClass('questions-btn-off').removeClass('questions-btn-on');
            $('#message-list-full').show();
            $('#message-list').hide();
        }
    }

    $('#scroll-bottom-btn').click(function() {
        
        // Automatically scroll to bottom
        const messageContainer = $('.message-list');
        messageContainer.scrollTop(messageContainer[0].scrollHeight);

    });

    $('#scroll-top-btn').click(function() {
        
        // Automatically scroll to top
        const messageContainer = $('.message-list');
        messageContainer.scrollTop(0);

    });

    $('#scroll-up-btn').click(function() {
        
        // Automatically scroll up
        const messageContainer = $('.message-list');
        messageContainer.scrollTop(messageContainer.scrollTop() - 50);

    });

    $('#scroll-down-btn').click(function() {
        
        // Automatically scroll down
        const messageContainer = $('.message-list');
        messageContainer.scrollTop(messageContainer.scrollTop() + 50);

    });

    // Connection management
    $('#connect-btn').click(function() {
        $.ajax({
            url: '/ytcm_connect',
            type: 'POST',
            success: function(response) {
                if (response.success) {
                    if (response.auth_url) {
                        location.href = response.auth_url;
                    } else {
                        // Update the interface
                        $('#connection-controls').html('<button id="disconnect-btn" class="btn btn-lg disconnect-btn text-white">DISCONNECT FROM YOUTUBE</button>');
                        $('#messages-container').removeClass('d-none');
                        
                        // Start messages polling
                        // Connection management
                        // Update interface
                        // Start message polling
                        // Stop message polling
                        
                        startMessagePolling();
                    }
                } else {
                    alert('Error during connection: ' + response.error);
                }
            },
            error: function() {
                alert('Error connecting to server');
            }
        });
    });
    
    // Disconnection management (using event delegation for dynamic elements)
    $(document).on('click', '#disconnect-btn', function() {
        $.ajax({
            url: '/ytcm_disconnect',
            type: 'POST',
            success: function(response) {
                if (response.success) {
                    // Update the interface
                    $('#connection-controls').html('<button id="connect-btn" class="btn btn-lg connect-btn text-white">CONNECT TO YOUTUBE</button>');
                    $('#messages-container').addClass('d-none');
                    $('#message-list').empty();
                    
                    // Stop message polling
                    stopMessagePolling();
                    
                    // Reload the page
                    location.reload();
                } else {
                    alert('Error during disconnection: ' + response.error);
                }
            },
            error: function() {
                alert('Error disconnecting from server');
            }
        });
    });
    
    // Function to update live title text
    function updateLiveTitle(text) {
        $('#live-title').text('(' + text + ')');
    }
    
    // Function to start message polling
    function startMessagePolling() {
        // Clear any previous intervals
        if (pollingInterval) {
            clearInterval(pollingInterval);
        }
        
        // Start a new interval
        pollingInterval = setInterval(fetchMessages, pollingIntervalMs); // Interval from server configuration
        
        // Execute the first request immediately
        fetchMessages();
    }
    
    // Function to stop message polling
    function stopMessagePolling() {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    }
    
    // Function to fetch messages
    function fetchMessages() {
        $.ajax({
            url: '/ytcm_get_messages',
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    apiQuotaErrMsg = false;
                    updateMessageList(response.messages);
                } else if (response.error !== 'Not connected to YouTube') {
                    console.log('Error retrieving messages:', response.error);
                    if ((!apiQuotaErrMsg) && response.error.toLowerCase().includes('query')) {
                        apiQuotaErrMsg = true;
                        alert(response.error);
                    }
                }
            },
            error: function() {
//                $('#message-list').empty();
                console.log('Error communicating with server');
            }
        });
    }
    
    // Function to update message list
    function updateMessageList(messages) {

        const messageList = $('#message-list');
        const messageListFull = $('#message-list-full');
        let messageListCleared = false;
        
        // Add messages
        messages.forEach(function(msg) {

            if (msg.live_title) {
                updateLiveTitle(msg.live_title);
                if (msg.clean_msg_list) {
                    messageList.empty();
                    messageListFull.empty();
                    messageListCleared = true;
                }
            } else {            
                if (!messageListCleared) {
                    messageList.empty();
                    messageListFull.empty();
                    messageListCleared = true;
                }
                if (msg.show && (!(msg.show == 'false')) && (!(msg.show == 'False'))) {
                    const listItem = $('<li class="list-group-item d-flex justify-content-between align-items-center"></li>');
                    const listItemFull = $('<li class="list-group-item d-flex justify-content-between align-items-center"></li>');
                    // Set the message ID as a data attribute
                    listItem.attr('data-id', msg.id);
                    listItem.attr('data-ismale', msg.is_male);
                    listItem.attr('data-show', msg.show);
                    listItem.attr('data-text', msg.text);
                    listItem.attr('data-author', msg.author);
                    listItem.attr('data-isquestion', msg.is_question);
                    listItemFull.attr('data-id', msg.id);
                    listItemFull.attr('data-ismale', msg.is_male);
                    listItemFull.attr('data-show', msg.show);
                    listItemFull.attr('data-text', msg.text);
                    listItemFull.attr('data-author', msg.author);
                    listItemFull.attr('data-isquestion', msg.is_question);
                    
                    // Create message text container
                    const messageText = $('<div></div>');
                    const messageTextFull = $('<div></div>');
                    let msgText = msg.text;
                    if (forceMsgUppercase) {
                        msgText = msgText.toUpperCase();
                    }
                    const parsedText = parseYouTubeEmojisToHTML(msgText);
                    let msgAuthor = msg.author;
                    if (forceMsgUppercase) {
                        msgAuthor = msgAuthor.toUpperCase();
                    }
                    messageText.html(`<span style="font-family: Verdana, Open Sans, Inter, sans-serif, monospace, system-ui;"><strong>[${msgAuthor}] - ${parsedText}</strong></span>`);
                    messageTextFull.html(`<span style="font-family: Verdana, Open Sans, Inter, sans-serif, monospace, system-ui;"><strong>[${msgAuthor}] - ${parsedText}</strong></span>`);
                    
                    // Create toggle button
                    const toggleBtn = $('<button class="btn btn-sm ms-2"></button>');
                    const toggleBtnFull = $('<button class="btn btn-sm ms-2"></button>');
                    toggleBtn.addClass(msg.show ? 'btn-outline-danger' : 'btn-outline-success');
                    toggleBtn.html(msg.show ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>');
                    toggleBtn.attr('title', msg.show ? 'Hide message' : 'Show message');
                    // Make sure the click event doesn't propagate to the parent element in any case
                    toggleBtn.on('click mousedown mouseup', function(e) {
                        e.preventDefault();
                        e.stopPropagation(); // Prevent triggering the list item click
                        if (e.type === 'click') {
                            toggleMessageVisibility(msg.id, !msg.show);
                        }
                        return false; // Additional security to stop propagation
                    });

                    toggleBtnFull.addClass(msg.show ? 'btn-outline-danger' : 'btn-outline-success');
                    toggleBtnFull.html(msg.show ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>');
                    toggleBtnFull.attr('title', msg.show ? 'Hide message' : 'Show message');
                    // Make sure the click event doesn't propagate to the parent element in any case
                    toggleBtnFull.on('click mousedown mouseup', function(e) {
                        e.preventDefault();
                        e.stopPropagation(); // Prevent triggering the list item click
                        if (e.type === 'click') {
                            toggleMessageVisibility(msg.id, !msg.show);
                        }
                        return false; // Additional security to stop propagation
                    });
                    

                    // Add elements to list item
                    listItem.append(messageText);
                    listItem.append(toggleBtn);
                    listItemFull.append(messageTextFull);
                    listItemFull.append(toggleBtnFull);

                    // Variable to track click timing
                    let clickTimer = null;
                    
                    // Add click event to show overlay (single click)
                    listItem.click(function() {                   
                        // Use a timer to differentiate between single and double click
                        const $this = $(this);
                        clickTimer = setTimeout(function() {
                            clickTimer = null;
                            showMessageOverlay(msg.author, msg.text, $this);
                        }, 300); // 300ms delay to wait for potential double click
                    });
                    listItemFull.click(function() {                   
                        // Use a timer to differentiate between single and double click
                        const $this = $(this);
                        clickTimer = setTimeout(function() {
                            clickTimer = null;
                            showMessageOverlay(msg.author, msg.text, $this);
                        }, 300); // 300ms delay to wait for potential double click
                    });
                    
                    // Add double click event to flash message and copy to clipboard
                    listItem.dblclick(function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // Set flag to prevent single click
                        preventSingleClick = true;
                        
                        // Clear the single click timer if it exists
                        if (clickTimer) {
                            clearTimeout(clickTimer);
                            clickTimer = null;
                        }
                        
                        // Reset the prevention flag after a short delay
                        /* setTimeout(function() {
                            preventSingleClick = false;
                        }, 500); */
                        
                        // Add flash animation class
                        listItem.addClass('message-flash');
                        
                        // Copy text to clipboard
                        const textToCopy = `[${msg.author}] - ${msg.text}`;
                        navigator.clipboard.writeText(textToCopy).then(function() {
                            // Show temporary visual feedback
                            const feedback = $('<span class="copy-feedback copy-success"><i class="bi bi-check"><i> Copied!</span>');
                            listItem.append(feedback);
                            
                            // Remove flash class and feedback after animation completes
                            setTimeout(function() {
                                listItem.removeClass('message-flash');
                                feedback.remove();
                            }, 1500);
                        }).catch(function(err) {
                            console.log('Error during copy: ', err);
                            listItem.append('<span class="copy-feedback copy-error"><i class="bi bi-exclamation-triangle"></i> Error during copy</span>');
                            setTimeout(function() {
                                listItem.removeClass('message-flash');
                            }, 1500);
                        });
                    });

                    listItemFull.dblclick(function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // Set flag to prevent single click
                        preventSingleClick = true;
                        
                        // Clear the single click timer if it exists
                        if (clickTimer) {
                            clearTimeout(clickTimer);
                            clickTimer = null;
                        }
                        
                        // Reset the prevention flag after a short delay
                        /* setTimeout(function() {
                            preventSingleClick = false;
                        }, 500); */
                        
                        // Add flash animation class
                        listItemFull.addClass('message-flash');
                        
                        // Copy text to clipboard
                        const textToCopy = `[${msg.author}] - ${msg.text}`;
                        navigator.clipboard.writeText(textToCopy).then(function() {
                            // Show temporary visual feedback
                            const feedback = $('<span class="copy-feedback copy-success"><i class="bi bi-check"><i> Copied!</span>');
                            listItemFull.append(feedback);
                            
                            // Remove flash class and feedback after animation completes
                            setTimeout(function() {
                                listItemFull.removeClass('message-flash');
                                feedback.remove();
                            }, 1500);
                        }).catch(function(err) {
                            console.log('Error during copy: ', err);
                            listItemFull.append('<span class="copy-feedback copy-error"><i class="bi bi-exclamation-triangle"></i> Error during copy</span>');
                            setTimeout(function() {
                                listItemFull.removeClass('message-flash');
                            }, 1500);
                        });
                    });

                    if (msg.is_question && (!(msg.is_question == 'false')) && (!(msg.is_question == 'False'))) {
                        messageList.append(listItem);
                    }
                    messageListFull.append(listItemFull);
                }
            }
        });
        
        updateQuestionsButtonState();

        if (questionsOnly !== 0) {
            let nMessages = messageList.children().length;
            if (lastNMessages < nMessages) {
                // Automatically scroll to bottom
                const messageContainer = $('.message-list');
                messageContainer.scrollTop(messageContainer[0].scrollHeight);
            }
            lastNMessages = nMessages;
        } else {
            let nMessages = messageListFull.children().length;
            if (lastNMessagesFull < nMessages) {
                // Automatically scroll to bottom
                const messageContainer = $('.message-list');
                messageContainer.scrollTop(messageContainer[0].scrollHeight);
            }
            lastNMessagesFull = nMessages;
        }
    }
    
    // Function to toggle message visibility
    function toggleMessageVisibility(messageId, showValue) {
        // If showValue is false, immediately remove the element from the list
        if (!showValue) {
            // Find and remove the element with the corresponding ID
            $(`#message-list li[data-id="${messageId}"]`).remove();
            $(`#message-list-full li[data-id="${messageId}"]`).remove();
        }
        
        // Send the request to the server anyway to update the status
        $.ajax({
            url: '/ytcm_toggle_message_visibility',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                id: messageId,
                show: showValue
            }),
            success: function(response) {
                if (response.success) {
                    // If showValue is true, update the list to show the message
                    if (showValue) {
                        fetchMessages();
                    }
                } else {
                    console.log('Error toggling message visibility:', response.error);
                    // In case of error, update the list anyway to restore the correct state
                    fetchMessages();
                }
            },
            error: function() {
                console.log('Error communicating with server');
                // In case of error, update the list anyway to restore the correct state
                fetchMessages();
            }
        });
    }
    
    // If already connected, start polling
    if (isConnected) {
        startMessagePolling();
    }
// ================================================
// ********** Message overlay management **********
// ================================================

    // Function to show the overlay with the message
    window.showMessageOverlay = function(author, text, element) {
        // Don't show overlay if double click was detected
        if (preventSingleClick) {
            preventSingleClick = false;
            return;
        }
        
        if (forceMsgUppercase) {
            author = author.toUpperCase();
            text = text.toUpperCase();
        }
        
        // Get the message ID from the clicked element
        const messageId = element.attr('data-id');
        const isMale = element.attr('data-ismale') === 'true';
        
        $('#overlay-author').text(author);
        $('#overlay-content').html(parseYouTubeEmojisToHTML(text));
        
        // Add the audio player or loading image
        checkAndAddAudioPlayer(messageId, text, isMale);
        
        $('#message-overlay').css('display', 'flex');
    };
    
    // Close the overlay when clicking the close button
    $('#overlay-close').click(function() {
        // Stop audio playback if it's playing
        const audioElement = $('#audio-container audio')[0];
        if (audioElement && !audioElement.paused) {
            audioElement.pause();
            audioElement.currentTime = 0;
        }
        
        $('#message-overlay').css('display', 'none');
    });
    
    // Copy the message text to the clipboard
    $('#overlay-copy').click(function() {
        const text = '[' + $('#overlay-author').text() + '] - ' + $('#overlay-content').text();
        navigator.clipboard.writeText(text).then(function() {
            // Temporary visual feedback
            const originalText = $('#overlay-copy').html();
            $('#overlay-copy').html('<i class="bi bi-check"></i> Copied!');
            setTimeout(function() {
                $('#overlay-copy').html(originalText);
            }, 2000);
        }).catch(function(err) {
            console.log('Error during copy: ', err);
        });
    });
    
    // Function to check and add the audio player
    function checkAndAddAudioPlayer(messageId, text, isMale) {
        if (!messageId) return;
        
        // Check if TTS is enabled
        if (typeof ytcm_tts_enabled !== 'undefined' && !ytcm_tts_enabled) {
            return;
        }

        // Remove any existing audio players
        $('#audio-container').remove();
        
        // Check if an audio file already exists for this message
        $.ajax({
            url: '/ytcm_check_audio_file',
            type: 'GET',
            data: { id: messageId },
            success: function(response) {
                if (response.exists) {
                    // The audio file exists, add the player
                    addAudioPlayer(messageId);
                } else {
                    // The audio file does not exist, show the loading image
                    $('.message-overlay-footer').prepend('<div id="audio-container"><img src="/static/images/loading-bar.gif" alt="Loading..." style="height: 40px;"></div>');
                    
                    // Request the generation of the audio file with retry mechanism
                    let retryCount = 0;
                    const maxRetries = 3;
                    
                    function generateAudio() {
                        $.ajax({
                            url: '/ytcm_generate_audio',
                            type: 'POST',
                            contentType: 'application/json',
                            data: JSON.stringify({
                                id: messageId,
                                text: text,
                                is_male: isMale
                            }),
                            success: function(genResponse) {
                                if (genResponse.success) {
                                    // Replace the loading image with the audio player
                                    addAudioPlayer(messageId);
                                } else {
                                    // Retry if we haven't reached max retries
                                    if (retryCount < maxRetries) {
                                        retryCount++;
                                        $('#audio-container').html(`<div class="audio-loading">Attempt ${retryCount}/${maxRetries}...</div>`);
                                        setTimeout(generateAudio, 1000); // Wait 1 second before retrying
                                    } else {
                                        // Show an error message after all retries failed
                                        $('#audio-container').html('<div class="audio-error">Error generating audio</div>');
                                    }
                                }
                            },
                            error: function() {
                                // Retry if we haven't reached max retries
                                if (retryCount < maxRetries) {
                                    retryCount++;
                                    $('#audio-container').html(`<div class="audio-loading">Attempt ${retryCount}/${maxRetries}...</div>`);
                                    setTimeout(generateAudio, 1000); // Wait 1 second before retrying
                                } else {
                                    // Show an error message after all retries failed
                                    $('#audio-container').html('<div class="audio-error">Error generating audio</div>');
                                }
                            }
                        });
                    }
                    
                    // Start the generation process
                    generateAudio();
                }
            },
            error: function() {
                console.log('Error checking audio file');
            }
        });
    }
    
    // Function to add the audio player
    function addAudioPlayer(messageId) {
        // Check if TTS is enabled
        if (typeof ytcm_tts_enabled !== 'undefined' && !ytcm_tts_enabled) {
            // Remove any existing audio players
            $('#audio-container').remove();
            return;
        }
        
        // Remove any existing audio players before adding a new one
        $('#audio-container').remove();
        
        const audioHtml = `
            <div id="audio-container">
                <audio controls>
                    <source src="${YTCM_TTS_AUDIO_FILES_DIR}${messageId}.mp3" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            </div>
        `;
        
        // Add the player at the beginning of the footer
        $('.message-overlay-footer').prepend(audioHtml);
    }

});
