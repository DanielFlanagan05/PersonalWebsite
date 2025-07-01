var socket;

$(document).ready(function(){
    socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');
    socket.on('connect', function() {
        socket.emit('joined', {});
    });
    
    // Socket functionality for joining the room
    socket.on('status', function(data) {  
        console.log("status output")
        let tag  = document.createElement("p");
        let text = document.createTextNode(data.msg);
        let element = document.getElementById("chat");
        tag.appendChild(text);
        tag.style.cssText = data.style;
        element.appendChild(tag);
        $('#chat').scrollTop($('#chat')[0].scrollHeight);

    });        

    // Socket functionality for sending a message
    socket.on('message', function(data) {
        console.log("message output")
        let tag  = document.createElement("p");
        let text = document.createTextNode(data.msg);
        let element = document.getElementById("chat");
        tag.appendChild(text);
        tag.style.cssText = data.style;
        element.appendChild(tag);
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    // Socket functionality for leaving the room
    socket.on('leave', function(data) {
        debugger;
        let tag  = document.createElement("p");
        let text = document.createTextNode(data.msg);
        let element = document.getElementById("chat");
        tag.appendChild(text);
        tag.style.cssText = data.style;
        element.appendChild(tag);
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    // Send message if enter is pressed
    $('.chat-input').keypress(function(event){
        if(event.keyCode == 13){
            socket.emit('message', { 'message': $(this).val()});
            $(this).val(''); // clear input
        }
    });

    // Send message if button is clicked
    $("#sendButton").click(function(event) {
        var message = $('.chat-input').val(); // get the value from the chat-input field
        socket.emit('message', { 'message': message});
        $('.chat-input').val(''); 
    });

    // Leave the room if the leave button is clicked
    $("#leaveButton").click(function(event) {
        leaveRoom();  
    });
    
});

// Leave the room
function leaveRoom() {
    debugger;
    socket.emit('leave', {}, function(){
        socket.disconnect();
        window.location.href = "/home";
    });
}

