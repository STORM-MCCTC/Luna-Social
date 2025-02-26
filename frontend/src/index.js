// WebSocket URL configuration
const WS_URL = "ws://127.0.0.1:8000/ws";

// Function to check if user is logged in
function checkUserSession() {
    fetch("/session", { credentials: "include" })
        .then(response => response.json())
        .then(data => {
            if (data.username) {
                document.getElementById("usernameDisplay").innerText = data.username;
            } else {
                window.location.href = "/frontend/login.html"; // Redirect if not logged in
            }
        })
        .catch(() => {
            window.location.href = "/frontend/login.html"; // Redirect on error
        });
}

document.addEventListener("DOMContentLoaded", checkUserSession);

// Function to establish the WebSocket connection
function connectWebSocket() {
    websocket = new WebSocket(WS_URL);

    websocket.onopen = function () {
        console.log("Connected to WebSocket");
    };

    websocket.onmessage = function (event) {
        const newPost = JSON.parse(event.data);
        displayPost(newPost);
    };

    websocket.onclose = function () {
        console.log("WebSocket connection closed");
        setTimeout(connectWebSocket, 1000); // Attempt to reconnect after 1 second
    };

    websocket.onerror = function (error) {
        console.error("WebSocket error: ", error);
    };
}

connectWebSocket();

// Function to add new posts
async function addPost() {
    const postText = document.getElementById("postText").value;
    const imageInput = document.getElementById("imageUpload");
    const username = localStorage.getItem("username");
    
    if (!username) {
        alert("You must be logged in to post!");
        window.location.href = "/frontend/login.html";
        return;
    }

    if (!postText.trim()) {
        alert("Post cannot be empty");
        return;
    }

    let imageUrl = null;

    if (imageInput.files.length > 0) {
        const formData = new FormData();
        formData.append("file", imageInput.files[0]);

        const response = await fetch("http://127.0.0.1:8000/upload/", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();
        imageUrl = result.image_url;
    }

    const newPost = {
        username: username,
        content: postText,
        image_url: imageUrl,
        timestamp: new Date().toISOString()
    };

    websocket.send(JSON.stringify(newPost));
    displayPost(newPost);

    document.getElementById("postText").value = "";
    imageInput.value = "";
}

// Function to display a post
function displayPost(post) {
    const postContainer = document.getElementById("postContainer");
    const newPost = document.createElement("div");
    newPost.classList.add("post_main");

    newPost.innerHTML = 
        `<span class="post_top">
            <img class="post_profile_image" src="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png">
            <p class="post_user">${post.username}</p>
            <p class="post_id">@UserID</p>
        </span>
        <span class="post_content">
            <p class="post_body_text">${post.content}</p>
            ${post.image_url ? `<img class="post_body_image" src="http://127.0.0.1:8000${post.image_url}">` : ""}
        </span>
        <span class="post_footer">
            <p class="post_footer_text">${new Date(post.timestamp).toLocaleTimeString()}</p>
        </span>`;

    postContainer.prepend(newPost);
}

// Logout function
function logout() {
    localStorage.removeItem("username");
    window.location.href = "/frontend/login.html";
}