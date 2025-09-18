// medicore/static/js/chat.js

document.addEventListener('DOMContentLoaded', () => {
    // Connect to the WebSocket server
    var socket = io();

    // Get elements from the page
    const chatContainer = document.getElementById('chat-container');
    const requestId = chatContainer.dataset.requestId; // Get request ID from data attribute
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const messagesContainer = document.getElementById('chat-messages');
    const statusDisplay = document.getElementById('request-status');

    // Function to scroll the chat box to the bottom
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Scroll to bottom on page load
    scrollToBottom();

    // 1. Join the specific chat room
    socket.on('connect', () => {
        socket.emit('join', { room: requestId });
    });

    // 2. Listen for incoming messages
    socket.on('receive_message', function(data) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('mb-2');
        
        messageDiv.innerHTML = `
            <strong>${data.username}:</strong>
            <p class="mb-0">${data.msg}</p>
            <small class="text-muted">${data.timestamp}</small>
        `;
        
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    });

    // 3. Send a message when the send button is clicked
    sendButton.addEventListener('click', () => {
        const message = messageInput.value;
        if (message.trim() !== '') {
            socket.emit('send_message', { 'msg': message, 'request_id': requestId });
            messageInput.value = '';
        }
    });

    // Also send message when 'Enter' is pressed
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });

    // --- THIS IS THE PART THAT MAKES THE BUTTONS CLICKABLE ---
    // Send status change event when a pharmacist clicks a button
    document.querySelectorAll('.status-change-btn').forEach(button => {
        button.addEventListener('click', () => {
            const newStatus = button.dataset.status;
            socket.emit('change_status', { 'request_id': requestId, 'status': newStatus });
        });
    });

    // Listen for status updates from the server
    socket.on('status_updated', function(data) {
        if (statusDisplay) {
            statusDisplay.textContent = data.status;
        }
    });
});