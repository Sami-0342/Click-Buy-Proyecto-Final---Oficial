const menu = document.getElementById("menu")
const sidebar = document.getElementById("sidebar")

menu.addEventListener('click',()=> {
    sidebar.classList.toggle('menu-toggle')
});
const boxes = document.querySelectorAll('.box');

window.addEventListener('scroll', () => {
  boxes.forEach(box => {
    const rect = box.getBoundingClientRect();
    if (rect.top < window.innerHeight) {
      box.classList.add('show');
    }
  });
});
