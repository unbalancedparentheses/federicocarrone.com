document.addEventListener('DOMContentLoaded', function() {
  var galleryImages = document.querySelectorAll('.watching-gallery img, .listening-gallery img');
  galleryImages.forEach(function(img) {
    if (!img.hasAttribute('loading')) {
      img.setAttribute('loading', 'lazy');
    }
    if (!img.hasAttribute('decoding')) {
      img.setAttribute('decoding', 'async');
    }
  });
});
