$(document).ready(function() {
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
                // Uso HTML per mettere in grassetto il nome dell'autore
                messageText.html(`[<strong>${msg.author}</strong>] - ${msg.text}`);
                // Nota: cambiato .text() in .html() per supportare i tag HTML
                
                // Create toggle button
                const toggleBtn = $('<button class="btn btn-sm ms-2"></button>');
                toggleBtn.addClass(msg.show ? 'btn-outline-danger' : 'btn-outline-success');
                toggleBtn.html(msg.show ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>');
                toggleBtn.attr('title', msg.show ? 'Hide message' : 'Show message');
                toggleBtn.click(function(e) {
                    e.preventDefault();
                    toggleMessageVisibility(msg.id, !msg.show);
                });
                                    
                // Add elements to list item
                listItem.append(messageText);
                listItem.append(toggleBtn);

                messageList.append(listItem);

            }

        });
        
        // Automatically scroll to bottom
        const messageContainer = $('.message-list');
        messageContainer.scrollTop(messageContainer[0].scrollHeight);
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