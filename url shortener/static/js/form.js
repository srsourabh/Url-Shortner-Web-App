// // Variables
var signupButton = document.getElementById('new-button'),
    loginButton = document.getElementById('login-button'),
    userForms = document.getElementById('user_options-forms');


// // Add event listener to the "Sign Up" button
signupButton.addEventListener('click', () => {
    userForms.classList.remove('login-click')
    userForms.classList.add('signup-click')
}, false)


// // Add event listener to the "Login" button
loginButton.addEventListener('click', () => {
    userForms.classList.remove('signup-click')
    userForms.classList.add('login-click')
}, false)

var signupButton = document.getElementById("new-button");
var userForms = document.getElementById('user_options-forms');

signupButton.addEventListener('click', function () {
    userForms.classList.remove('login-click');
    userForms.classList.add('signup-click');
})


//Navbar 

var mainNav = document.getElementById("js-menu");
var navBarToggle = document.getElementById("js-navbar-toggle");

navBarToggle.addEventListener("click", function () {
    mainNav.classList.toggle("active");
});