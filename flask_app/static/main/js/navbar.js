// adds event listener to menu button to open and close the menu
function openNavMenu() {
    var menu = document.querySelector('.nav-links-mobile');
    if (menu.style.display === "flex") {
        menu.style.display = "none";
    } else {
        if (window.innerWidth <= 650) {
            menu.style.display = "flex";
        }
    }
}

// Close the menu when the window is resized
window.addEventListener('resize', function() {
    var menu = document.querySelector('.nav-links-mobile');
    if (window.innerWidth > 650) {
        menu.style.display = "none";
    } 
});



const menuIcon = document.querySelector('.menu-button img');
menuIcon.addEventListener('click', openNavMenu);
