document.addEventListener('DOMContentLoaded', () => {
    fetch('Menu.html')
      .then(response => response.text())
      .then(data => {
        document.getElementById('menu-container').innerHTML = data;
        const menu = document.querySelector('.menu');
        const toggle = document.getElementById('menu-toggle');
  
        toggle.addEventListener('click', () => {
          toggle.classList.toggle('open');
          menu.classList.toggle('open');
          document.getElementById('menu-container').style.display = menu.classList.contains('open') ? 'block' : 'none';
        });
  
        const expandables = document.querySelectorAll('.expandable');
        expandables.forEach(item => {
          item.addEventListener('click', (e) => {
            e.preventDefault();
            const parentLi = item.parentElement;
  
            if (parentLi.parentElement === menu.querySelector('ul')) {
              const topLevelItems = menu.querySelectorAll('li');
              topLevelItems.forEach(topItem => {
                if (topItem !== parentLi) {
                  topItem.classList.remove('open');
                  closeChildren(topItem);
                }
              });
            }
  
            const siblingLis = parentLi.parentElement.children;
            Array.from(siblingLis).forEach(sibling => {
              if (sibling !== parentLi) {
                sibling.classList.remove('open');
                closeChildren(sibling);
              }
            });
  
            parentLi.classList.toggle('open');
          });
        });
  
        function closeChildren(element) {
          const openChildren = element.querySelectorAll('.open');
          openChildren.forEach(child => child.classList.remove('open'));
        }
  
        document.addEventListener('click', (e) => {
          if (!menu.contains(e.target) && !toggle.contains(e.target)) {
            menu.classList.remove('open');
            toggle.classList.remove('open');
            document.getElementById('menu-container').style.display = 'none';
          }
        });
  
        menu.addEventListener('click', (e) => {
          e.stopPropagation();
        });
      });
  });
  