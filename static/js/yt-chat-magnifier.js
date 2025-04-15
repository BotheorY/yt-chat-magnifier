let lastNMessages = 0;
let preventSingleClick = false;

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
                    // Update the interface
                    $('#connection-controls').html('<button id="disconnect-btn" class="btn btn-lg disconnect-btn text-white">DISCONNECT FROM YOUTUBE</button>');
                    $('#messages-container').removeClass('d-none');
                    
                    // Start messages polling
                    // Connection management
                    // Update interface
                    // Start message polling
                    // Stop message polling
                    
                    startMessagePolling();
                } else {
                    alert('Error during connection: ' + response.error);
                }
            },
            error: function() {
                alert('Error connecting to server');
            }
        });
    });
    
    // Gestione disconnessione (usando event delegation per elementi dinamici)
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
    
    // Variable for polling interval
    let pollingInterval;
    
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
            
            if (msg.show) {
                const listItem = $('<li class="list-group-item d-flex justify-content-between align-items-center"></li>');
                // Set the message ID as a data attribute
                listItem.attr('data-id', msg.id);
                listItem.attr('data-ismale', msg.is_male);
                listItem.attr('data-show', msg.show);
                listItem.attr('data-text', msg.text);
                listItem.attr('data-author', msg.author);
                
                // Create message text container
                const messageText = $('<div></div>');
                // Uso HTML per mettere in grassetto il nome dell'autore e parsare le emoticon
                const parsedText = parseYouTubeEmojisToHTML(msg.text);
                messageText.html(`[<strong>${msg.author}</strong>] - ${parsedText}`);
                // Nota: cambiato .text() in .html() per supportare i tag HTML e le emoticon
                
                // Create toggle button
                const toggleBtn = $('<button class="btn btn-sm ms-2"></button>');
                toggleBtn.addClass(msg.show ? 'btn-outline-danger' : 'btn-outline-success');
                toggleBtn.html(msg.show ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>');
                toggleBtn.attr('title', msg.show ? 'Hide message' : 'Show message');
                toggleBtn.click(function(e) {
                    e.preventDefault();
                    e.stopPropagation(); // Prevent triggering the list item click
                    toggleMessageVisibility(msg.id, !msg.show);
                });
                                
                // Add elements to list item
                listItem.append(messageText);
                listItem.append(toggleBtn);

                // Variable to track click timing
                let clickTimer = null;
                
                // Add click event to show overlay (single click)
                listItem.click(function() {                   
                    // Use a timer to differentiate between single and double click
                    clickTimer = setTimeout(function() {
                        clickTimer = null;
                        showMessageOverlay(msg.author, msg.text);
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
                        const feedback = $('<span class="copy-feedback copy-success"><i class="bi bi-check"></i> Copiato negli appunti!</span>');
                        listItem.append(feedback);
                        
                        // Remove flash class and feedback after animation completes
                        setTimeout(function() {
                            listItem.removeClass('message-flash');
                            feedback.remove();
                        }, 1500);
                    }).catch(function(err) {
                        console.error('Errore durante la copia: ', err);
                        listItem.append('<span class="copy-feedback copy-error"><i class="bi bi-exclamation-triangle"></i> Errore durante la copia</span>');
                        setTimeout(function() {
                            listItem.removeClass('message-flash');
                        }, 1500);
                    });
                });

                messageList.append(listItem);
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
                    // Refresh messages to update UI
                    fetchMessages();
                } else {
                    console.error('Error toggling message visibility:', response.error);
                }
            },
            error: function() {
                console.error('Error communicating with server');
            }
        });
    }
    
    // If already connected, start polling
    if (isConnected) {
        startMessagePolling();
    }
});


// Gestione dell'overlay dei messaggi
$(document).ready(function() {
    // Funzione per mostrare l'overlay con il messaggio
    window.showMessageOverlay = function(author, text) {
        // Don't show overlay if double click was detected
        if (preventSingleClick) {
            preventSingleClick = false;
            return;
        }
        $('#overlay-author').text(author);
        $('#overlay-content').html(parseYouTubeEmojisToHTML(text));
        $('#message-overlay').css('display', 'flex');
    };
    
    // Chiudi l'overlay quando si clicca sul pulsante di chiusura
    $('#overlay-close').click(function() {
        $('#message-overlay').css('display', 'none');
    });
    
    // Copia il testo del messaggio negli appunti
    $('#overlay-copy').click(function() {
/*        const text = `[${$('#overlay-author').text()}] - ${$('#overlay-content').text()}`;    */
        const text = $('#overlay-content').text();
        navigator.clipboard.writeText(text).then(function() {
            // Feedback visivo temporaneo
            const originalText = $('#overlay-copy').html();
            $('#overlay-copy').html('<i class="bi bi-check"></i> Copiato!');
            setTimeout(function() {
                $('#overlay-copy').html(originalText);
            }, 2000);
        }).catch(function(err) {
            console.error('Errore durante la copia: ', err);
        });
    });
});

