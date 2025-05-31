// O Estúdio - Comments JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Set up comment form handling
  initializeCommentForm();
  
  // Set up comment deletion
  initializeCommentDeletion();
  
  // Set up lazy loading for comments
  initializeLazyLoading();
});

// Function to handle comment form submission
function initializeCommentForm() {
  const commentForm = document.getElementById('comment-form');
  const commentsContainer = document.getElementById('comments-list');
  
  if (!commentForm || !commentsContainer) return;
  
  commentForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get form data
    const formData = new FormData(commentForm);
    
    // Submit form via AJAX
    fetch('/comment/add', {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      // Create new comment element
      const newComment = createCommentElement(data);
      
      // Add to comments container at the top
      commentsContainer.insertBefore(newComment, commentsContainer.firstChild);
      
      // Clear form input
      commentForm.reset();
      
      // Display success message
      showNotification('Comment posted successfully!', 'success');
    })
    .catch(error => {
      console.error('Error posting comment:', error);
      showNotification('Failed to post comment. Please try again.', 'danger');
    });
  });
}

// Function to create a comment element from data
function createCommentElement(data) {
  const commentElement = document.createElement('div');
  commentElement.className = 'comment-box';
  commentElement.id = `comment-${data.id}`;
  
  commentElement.innerHTML = `
    <div class="d-flex">
      <div class="flex-shrink-0">
        <img src="${data.author_picture || 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png'}" class="comment-avatar" alt="${data.author}">
      </div>
      <div class="flex-grow-1 ms-3">
        <div class="d-flex justify-content-between align-items-start">
          <h5 class="mb-1">
            ${data.author} 
            <small class="text-muted">${formatCommentDate(data.created_at)}</small>
          </h5>
          ${data.can_delete ? `
            <button class="btn btn-sm btn-link text-danger delete-comment" 
                    data-comment-id="${data.id}" 
                    title="Delete comment">
              <i class="fa fa-trash-o"></i>
            </button>
          ` : ''}
        </div>
        <p>${data.content}</p>
      </div>
    </div>
  `;
  
  return commentElement;
}

// Function to initialize comment deletion
function initializeCommentDeletion() {
  const commentsContainer = document.getElementById('comments-list');
  
  if (!commentsContainer) return;
  
  // Use event delegation for delete buttons
  commentsContainer.addEventListener('click', function(e) {
    const deleteButton = e.target.closest('.delete-comment');
    
    if (!deleteButton) return;
    
    e.preventDefault();
    const commentId = deleteButton.getAttribute('data-comment-id');
    
    if (confirm('Are you sure you want to delete this comment?')) {
      // Send delete request
      fetch(`/comment/${commentId}/delete`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Remove comment from DOM
          const commentElement = document.getElementById(`comment-${commentId}`);
          if (commentElement) {
            commentElement.remove();
          }
          
          // Show success message
          showNotification('Comment deleted successfully!', 'success');
        }
      })
      .catch(error => {
        console.error('Error deleting comment:', error);
        showNotification('Failed to delete comment. Please try again.', 'danger');
      });
    }
  });
}

// Function to initialize lazy loading for comments
function initializeLazyLoading() {
  const commentsContainer = document.getElementById('comments-list');
  const loadMoreButton = document.getElementById('load-more-comments');
  
  if (!commentsContainer || !loadMoreButton) return;
  
  loadMoreButton.addEventListener('click', function() {
    // Get current page from button data attribute
    const currentPage = parseInt(this.getAttribute('data-page') || 1);
    const nextPage = currentPage + 1;
    const concertId = this.getAttribute('data-concert-id');
    
    // Show loading indicator
    this.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Loading...';
    this.disabled = true;
    
    // Fetch more comments
    fetch(`/concert/${concertId}/comments?page=${nextPage}`, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      // Add comments to container
      data.comments.forEach(comment => {
        const commentElement = createCommentElement(comment);
        commentsContainer.appendChild(commentElement);
      });
      
      // Update button state
      this.innerHTML = 'Load more comments';
      this.disabled = false;
      
      // Update page number
      this.setAttribute('data-page', nextPage);
      
      // Hide button if no more comments
      if (data.comments.length < 10 || !data.has_more) {
        this.style.display = 'none';
      }
    })
    .catch(error => {
      console.error('Error loading more comments:', error);
      this.innerHTML = 'Load more comments';
      this.disabled = false;
      showNotification('Failed to load more comments. Please try again.', 'danger');
    });
  });
}

// Helper function to format comment date
function formatCommentDate(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  
  // For comments less than a day old, show relative time
  const diffMs = now - date;
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  
  if (diffHours < 24) {
    if (diffMins < 1) {
      return 'just now';
    } else if (diffMins < 60) {
      return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    }
  }
  
  // For older comments, show the date
  return date.toLocaleDateString();
}

// Function to show notifications
function showNotification(message, type = 'info') {
  // Create notification container if it doesn't exist
  let notificationContainer = document.getElementById('notification-container');
  
  if (!notificationContainer) {
    notificationContainer = document.createElement('div');
    notificationContainer.id = 'notification-container';
    notificationContainer.className = 'position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(notificationContainer);
  }
  
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `toast align-items-center text-white bg-${type} border-0`;
  notification.setAttribute('role', 'alert');
  notification.setAttribute('aria-live', 'assertive');
  notification.setAttribute('aria-atomic', 'true');
  
  notification.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">
        ${message}
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;
  
  // Add to container
  notificationContainer.appendChild(notification);
  
  // Initialize toast
  const toast = new bootstrap.Toast(notification, {
    delay: 5000,
    autohide: true
  });
  
  // Show toast
  toast.show();
  
  // Remove from DOM after hiding
  notification.addEventListener('hidden.bs.toast', function() {
    notification.remove();
  });
}
