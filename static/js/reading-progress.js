document.addEventListener('DOMContentLoaded', function() {
  var progressBar = document.getElementById('reading-progress');
  if (!progressBar) return;

  var article = document.querySelector('article');
  if (!article) return;

  var ticking = false;

  function updateProgress() {
    var articleRect = article.getBoundingClientRect();
    var articleTop = articleRect.top + window.scrollY;
    var articleHeight = article.offsetHeight;
    var windowHeight = window.innerHeight;
    var scrollY = window.scrollY;

    var start = articleTop;
    var end = articleTop + articleHeight - windowHeight;

    if (end <= start) {
      progressBar.style.transform = 'scaleX(0)';
      return;
    }

    var progress = (scrollY - start) / (end - start);
    progress = Math.max(0, Math.min(1, progress));
    progressBar.style.transform = 'scaleX(' + progress + ')';
  }

  function onScroll() {
    if (!ticking) {
      requestAnimationFrame(function() {
        updateProgress();
        ticking = false;
      });
      ticking = true;
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  updateProgress();
});
