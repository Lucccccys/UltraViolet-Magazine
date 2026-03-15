document.addEventListener('DOMContentLoaded', () => {
  const currentYearNodes = document.querySelectorAll('[data-current-year]');
  const year = new Date().getFullYear();
  currentYearNodes.forEach((node) => {
    node.textContent = year;
  });
});
