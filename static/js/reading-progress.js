document.addEventListener('DOMContentLoaded', function() {
  var progressBar = document.getElementById('reading-progress');
  if (!progressBar) return;

  var article = document.querySelector('article');
  if (!article) return;

  function updateProgress() {
    var articleRect = article.getBoundingClientRect();
    var articleTop = articleRect.top + window.scrollY;
    var articleHeight = article.offsetHeight;
    var windowHeight = window.innerHeight;
    var scrollY = window.scrollY;

    var start = articleTop;
    var end = articleTop + articleHeight - windowHeight;
    var progress = (scrollY - start) / (end - start);

    progress = Math.max(0, Math.min(1, progress));
    progressBar.style.transform = 'scaleX(' + progress + ')';
  }

  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();
});
