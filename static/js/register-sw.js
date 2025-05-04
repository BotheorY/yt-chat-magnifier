// Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/static/js/service-worker.js')
      .then(function(registration) {
        console.log('Service Worker successfully registered:', registration.scope);
      })
      .catch(function(error) {
        console.log('Service Worker registration failed:', error);
      });
  });
}