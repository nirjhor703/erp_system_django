document.addEventListener('DOMContentLoaded', function() {
    const submenuToggles = document.querySelectorAll('.submenu-toggle');

    // Toggle submenus
    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            const parentLi = this.closest('.menu-item.has-submenu');
            if (!parentLi) return;

            const submenu = parentLi.querySelector('.submenu');
            if (!submenu) return;

            e.preventDefault(); // Prevent any navigation

            const isOpen = parentLi.classList.contains('open');

            // Close sibling menus (accordion effect)
            const parentUl = parentLi.closest('ul');
            if (parentUl) {
                parentUl.querySelectorAll('.menu-item.has-submenu.open').forEach(li => {
                    if (li !== parentLi) li.classList.remove('open', 'active-parent');
                });
            }

            // Toggle current menu
            if (isOpen) {
                parentLi.classList.remove('open', 'active-parent');
            } else {
                parentLi.classList.add('open');
            }
        });
    });

    // Highlight active links & parents
    function setActiveMenu() {
        const currentURL = window.location.href;
        const links = document.querySelectorAll('.menu-item a');

        // Reset all
        links.forEach(link => link.classList.remove('active-link'));
        document.querySelectorAll('.menu-item.has-submenu').forEach(li => li.classList.remove('open', 'active-parent'));

        let activeLink = null;

        // Find the child link matching current URL
        links.forEach(link => {
            // Skip links with href="#" (top-level toggle)
            if (link.getAttribute('href') !== '#' && link.href === currentURL) {
                activeLink = link;
            }
        });

        if (activeLink) {
            activeLink.classList.add('active-link');

            // Open all parent menus
            let parentLi = activeLink.closest('.menu-item.has-submenu');
            while (parentLi) {
                parentLi.classList.add('open', 'active-parent');
                parentLi = parentLi.parentElement.closest('.menu-item.has-submenu');
            }
        }
    }

    setActiveMenu();
});