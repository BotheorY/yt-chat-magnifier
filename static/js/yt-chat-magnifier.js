let lastNMessages = 0;
let preventSingleClick = false;
let pollingInterval;

$(document).ready(function() {

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
                    updateMessageList(response.messages);
                } else if (response.error !== 'Not connected to YouTube') {
                    console.error('Error retrieving messages:', response.error);
                }
            },
            error: function() {
                $('#message-list').empty();
                console.error('Error communicating with server');
            }
        });
    }
    
    // Function to update message list
    function updateMessageList(messages) {
        const messageList = $('#message-list');
        
        // Clear the list
        messageList.empty();
        
        // Add messages
        messages.forEach(function(msg) {

            if (msg.live_title) {
                updateLiveTitle(msg.live_title);

console.log('Live title changed.', msg.live_title); // Debugging

            } else {
            
                if (msg.show && (!(msg.show == 'false')) && (!(msg.show == 'False'))) {
                    const listItem = $('<li class="list-group-item d-flex justify-content-between align-items-center"></li>');
                    // Set the message ID as a data attribute
                    listItem.attr('data-id', msg.id);
                    listItem.attr('data-ismale', msg.is_male);
                    listItem.attr('data-show', msg.show);
                    listItem.attr('data-text', msg.text);
                    listItem.attr('data-author', msg.author);
                    
                    // Create message text container
                    const messageText = $('<div></div>');
                    const parsedText = parseYouTubeEmojisToHTML(msg.text);
                    messageText.html(`[<strong>${msg.author}</strong>] - ${parsedText}`);
                    
                    // Create toggle button
                    const toggleBtn = $('<button class="btn btn-sm ms-2"></button>');
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
                                    
                    // Add elements to list item
                    listItem.append(messageText);
                    listItem.append(toggleBtn);

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
                            console.error('Error during copy: ', err);
                            listItem.append('<span class="copy-feedback copy-error"><i class="bi bi-exclamation-triangle"></i> Error during copy</span>');
                            setTimeout(function() {
                                listItem.removeClass('message-flash');
                            }, 1500);
                        });
                    });
                    messageList.append(listItem);
                }
            }
        });
        
        let nMessages = messageList.children().length;
            if (lastNMessages < nMessages) {
            // Automatically scroll to bottom
            const messageContainer = $('.message-list');
            messageContainer.scrollTop(messageContainer[0].scrollHeight);
        }
        lastNMessages = nMessages;
    }
    
    // Function to toggle message visibility
    function toggleMessageVisibility(messageId, showValue) {
        // If showValue is false, immediately remove the element from the list
        if (!showValue) {
            // Find and remove the element with the corresponding ID
            $(`#message-list li[data-id="${messageId}"]`).remove();
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
                    // Se showValue è true, aggiorna la lista per mostrare il messaggio
                    if (showValue) {
                        fetchMessages();
                    }
                } else {
                    console.error('Error toggling message visibility:', response.error);
                    // In caso di errore, aggiorna comunque la lista per ripristinare lo stato corretto
                    fetchMessages();
                }
            },
            error: function() {
                console.error('Error communicating with server');
                // In caso di errore, aggiorna la lista per ripristinare lo stato corretto
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
        const text = $('#overlay-content').text();
        navigator.clipboard.writeText(text).then(function() {
            // Temporary visual feedback
            const originalText = $('#overlay-copy').html();
            $('#overlay-copy').html('<i class="bi bi-check"></i> Copied!');
            setTimeout(function() {
                $('#overlay-copy').html(originalText);
            }, 2000);
        }).catch(function(err) {
            console.error('Error during copy: ', err);
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
                    
                    // Request the generation of the audio file
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
                                // Show an error message
                                $('#audio-container').html('<div class="audio-error">Error generating audio</div>');
                            }
                        },
                        error: function() {
                            $('#audio-container').html('<div class="audio-error">Error generating audio</div>');
                        }
                    });
                }
            },
            error: function() {
                console.error('Error checking audio file');
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
