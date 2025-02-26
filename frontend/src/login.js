// Switch between login and signup forms
function toggleSignup() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    if (loginForm.style.display === 'none') {
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
    } else {
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
    }
}

// Login function
function login() {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;

    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user, password: pass }),
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            localStorage.setItem("username", user);
            window.location.href = "/frontend/index.html";
        } else {
            alert("Invalid credentials");
        }
    })
    .catch(error => console.error("Error:", error));
}

// Signup function
function signup() {
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;

    fetch('http://localhost:8000/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Signup successful! You can now login.');
            toggleSignup();
        } else {
            alert('Signup failed: ' + data.detail);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again later.');
    });
}