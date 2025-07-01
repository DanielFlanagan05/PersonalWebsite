document.addEventListener('DOMContentLoaded', (event) => {
    const feedbackButton = document.getElementById('feedbackButton');
    const feedbackForm = document.querySelector('form');
  
    feedbackButton.addEventListener('click', function() {
      if (feedbackForm.style.display === 'block') {
        feedbackForm.style.display = 'none';
      } else {
        feedbackForm.style.display = 'block';
      }
    });
  });
  