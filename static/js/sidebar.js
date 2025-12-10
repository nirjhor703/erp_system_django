document.addEventListener('DOMContentLoaded', function() {
    // Select all menu links that have a submenu toggle class
    const submenuToggles = document.querySelectorAll('.submenu-toggle');

    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault(); // Stop the default anchor behavior

            // The parent <li> element is the context for the toggle
            const parentLi = this.closest('.menu-item.has-submenu');

            if (parentLi) {
                // Check if the current menu is already open
                const isAlreadyOpen = parentLi.classList.contains('open');

                // 1. Close all currently open menus at the same level
                // This prevents multiple menus from being open simultaneously (Accordion behavior)
                const currentLevelUl = parentLi.closest('ul');
                if (currentLevelUl) {
                    currentLevelUl.querySelectorAll('.menu-item.has-submenu.open').forEach(openLi => {
                        // Only close siblings, not the one being clicked
                        if (openLi !== parentLi) {
                            openLi.classList.remove('open');
                        }
                    });
                }

                // 2. Toggle the 'open' class on the clicked parent <li>
                if (isAlreadyOpen) {
                    parentLi.classList.remove('open');
                } else {
                    parentLi.classList.add('open');
                }
            }
        });
    });
});