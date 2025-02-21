// WebSocket URL configuration
const WS_URL = "ws://127.0.0.1:8000/ws";

// Function to establish the WebSocket connection
function connectWebSocket() {
    websocket = new WebSocket(WS_URL);

    websocket.onopen = function() {
        console.log("Connected to WebSocket");
    };

    websocket.onmessage = function(event) {
        const newPost = JSON.parse(event.data);
        displayPost(newPost);
    };

    websocket.onclose = function() {
        console.log("WebSocket connection closed");
        setTimeout(connectWebSocket, 1000);  // Attempt to reconnect after 1 second
    };

    websocket.onerror = function(error) {
        console.error("WebSocket error: ", error);
    };
}

// Call connectWebSocket to open the WebSocket connection
connectWebSocket();

// Function to add new posts
function addPost() {
    const postText = document.getElementById("postText").value;
    const imageInput = document.getElementById("imageUpload");
    const postContainer = document.getElementById("postContainer");
            
    if (!postText.trim()) {
        alert("Post cannot be empty");
        return;
    }
            
    const newPost = {
        username: "Username",
        content: postText,
        image_url: imageInput.files && imageInput.files[0] ? URL.createObjectURL(imageInput.files[0]) : null,
        timestamp: new Date().toISOString()
    };

    // Send post data to the backend via WebSocket
    websocket.send(JSON.stringify(newPost));
    displayPost(newPost);

    document.getElementById("postText").value = "";
    imageInput.value = "";
}

// Display post in the frontend
function displayPost(post) {
    const postContainer = document.getElementById("postContainer");
    const newPost = document.createElement("div");
    newPost.classList.add("post_main");
            
    newPost.innerHTML = `
        <span class="post_top">
            <img class="post_profile_image" src="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png">
            <p class="post_user">${post.username}</p>
            <p class="post_id">@UserID</p>
            </span>
            <span class="post_content">
                <p class="post_body_text">${post.content}</p>
                ${post.image_url ? `<img class="post_body_image" src="${post.image_url}">` : ""}
            </span>
            <span class="post_footer">
                <p class="post_footer_text">${new Date(post.timestamp).toLocaleTimeString()}</p>
            </span>`;

    postContainer.prepend(newPost);
}