document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('pre').forEach(function(pre) {
    var button = document.createElement('button');
    button.className = 'copy-button';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code to clipboard');

    function showSuccess() {
      button.textContent = 'Copied!';
      button.classList.add('copied');
      setTimeout(function() {
        button.textContent = 'Copy';
        button.classList.remove('copied');
      }, 2000);
    }

    function showError() {
      button.textContent = 'Failed';
      button.classList.add('error');
      setTimeout(function() {
        button.textContent = 'Copy';
        button.classList.remove('error');
      }, 2000);
    }

    function fallbackCopy(text) {
      var textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        showSuccess();
      } catch (err) {
        showError();
      }
      document.body.removeChild(textarea);
    }

    button.addEventListener('click', function() {
      var code = pre.querySelector('code');
      var text = code ? code.textContent : pre.textContent;

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(showSuccess).catch(function() {
          fallbackCopy(text);
        });
      } else {
        fallbackCopy(text);
      }
    });

    pre.style.position = 'relative';
    pre.appendChild(button);
  });
});
