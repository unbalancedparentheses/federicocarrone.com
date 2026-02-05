// Timeline "Show all" button
document.addEventListener('DOMContentLoaded', function() {
  const showMoreBtn = document.querySelector('.timeline-show-more');
  if (showMoreBtn) {
    showMoreBtn.addEventListener('click', function() {
      document.querySelector('.timeline').classList.add('timeline--expanded');
      this.style.display = 'none';
    });
  }

  // Newsletter form submission
  const newsletterForm = document.querySelector('.newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function() {
      const button = this.querySelector('button');
      button.disabled = true;
      button.textContent = 'Subscribing...';
    });
  }

  // Add lazy loading to gallery images
  document.querySelectorAll('.watching-gallery img, .reading-gallery img').forEach(function(img) {
    img.loading = 'lazy';
  });
});
