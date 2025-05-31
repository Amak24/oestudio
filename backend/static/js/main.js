// O Estúdio - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Handle mobile navbar toggle
  const navbarToggler = document.querySelector('.navbar-toggler');
  if (navbarToggler) {
    navbarToggler.addEventListener('click', function() {
      document.querySelector('.navbar-collapse').classList.toggle('show');
    });
  }

  // Initialize datetime picker for scheduling concerts
  const dateTimeFields = document.querySelectorAll('input[type="datetime-local"]');
  if (dateTimeFields.length > 0) {
    dateTimeFields.forEach(field => {
      if (field.value === '') {
        // Set default value to current date/time + 1 hour
        const now = new Date();
        now.setHours(now.getHours() + 1);
        field.value = now.toISOString().slice(0, 16);
      }
    });
  }

  // Handle "Is Live" checkbox to show/hide scheduled date
  const isLiveCheckbox = document.getElementById('is_live');
  const scheduledForGroup = document.getElementById('scheduled_for_group');
  
  if (isLiveCheckbox && scheduledForGroup) {
    // Initial state
    scheduledForGroup.style.display = isLiveCheckbox.checked ? 'block' : 'none';
    
    // Handle changes
    isLiveCheckbox.addEventListener('change', function() {
      scheduledForGroup.style.display = this.checked ? 'block' : 'none';
    });
  }

  // Handle like button interactions
  setupLikeButtons();
  
  // Handle comment form submissions
  setupCommentForm();
  
  // Handle search form
  setupSearchForm();
});

// Function to handle like button interactions
function setupLikeButtons() {
  const likeButtons = document.querySelectorAll('.like-btn');
  
  likeButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      
      const concertId = this.dataset.concertId;
      const likeIcon = this.querySelector('i');
      const likeCount = document.getElementById(`like-count-${concertId}`);
      
      // Send AJAX request
      fetch(`/concert/${concertId}/like`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
      })
      .then(response => response.json())
      .then(data => {
        // Update the button class and icon
        if (data.liked) {
          this.classList.add('liked');
          likeIcon.classList.remove('fa-heart-o');
          likeIcon.classList.add('fa-heart');
        } else {
          this.classList.remove('liked');
          likeIcon.classList.remove('fa-heart');
          likeIcon.classList.add('fa-heart-o');
        }
        
        // Update the count
        if (likeCount) {
          likeCount.textContent = data.count;
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
    });
  });
}

// Function to handle comment form submission
function setupCommentForm() {
  const commentForm = document.getElementById('comment-form');
  
  if (commentForm) {
    commentForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      
      fetch('/comment/add', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json())
      .then(data => {
        // Create new comment HTML
        const commentsList = document.getElementById('comments-list');
        const newComment = document.createElement('div');
        newComment.className = 'comment-box';
        newComment.innerHTML = `
          <div class="d-flex">
            <div class="flex-shrink-0">
              <img src="/static/images/default-avatar.jpg" class="comment-avatar" alt="${data.author}">
            </div>
            <div class="flex-grow-1 ms-3">
              <h5 class="mb-1">${data.author} <small class="text-muted">${data.created_at}</small></h5>
              <p>${data.content}</p>
            </div>
          </div>
        `;
        
        // Add to the top of comments list
        commentsList.insertBefore(newComment, commentsList.firstChild);
        
        // Clear the form
        this.reset();
      })
      .catch(error => {
        console.error('Error:', error);
      });
    });
  }
}

// Function to handle search form filtering
function setupSearchForm() {
  const searchForm = document.getElementById('search-form');
  
  if (searchForm) {
    // Update the URL with form data on submission
    searchForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      const params = new URLSearchParams();
      
      for (const pair of formData.entries()) {
        // Only add non-empty values
        if (pair[1]) {
          params.append(pair[0], pair[1]);
        }
      }
      
      // Navigate to the search URL with parameters
      window.location.href = `/concerts?${params.toString()}`;
    });
  }
}

// Format duration from seconds to MM:SS
function formatDuration(seconds) {
  if (!seconds) return '00:00';
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Format date for display
function formatDate(dateString) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}
