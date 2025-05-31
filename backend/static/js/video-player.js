// O Estúdio - Video Player JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Initialize video.js player if video element exists
  const videoElement = document.getElementById('concert-video');
  
  if (videoElement) {
    const isLive = videoElement.getAttribute('data-is-live') === 'true';
    
    // Initialize video.js with options
    const player = videojs('concert-video', {
      controls: true,
      autoplay: false,
      preload: 'auto',
      fluid: true,
      responsive: true,
      playbackRates: [0.5, 1, 1.5, 2],
      html5: {
        vhs: {
          overrideNative: true
        },
        nativeAudioTracks: false,
        nativeVideoTracks: false
      },
      controlBar: {
        children: [
          'playToggle',
          'volumePanel',
          'currentTimeDisplay',
          'timeDivider',
          'durationDisplay',
          'progressControl',
          'liveDisplay',
          'playbackRateMenuButton',
          'fullscreenToggle'
        ]
      }
    });
    
    // Add live indicator if live concert
    if (isLive) {
      player.addClass('vjs-live');
      
      // Show live indicator
      const liveIndicator = document.createElement('div');
      liveIndicator.className = 'live-indicator';
      liveIndicator.innerHTML = '<span class="pulse"></span> LIVE';
      player.el().appendChild(liveIndicator);
    }
    
    // Handle player events
    player.on('play', function() {
      console.log('Video playing');
    });
    
    player.on('pause', function() {
      console.log('Video paused');
    });
    
    player.on('ended', function() {
      console.log('Video ended');
      // Recommend similar concerts
      showRecommendations();
    });
    
    // Add error handling
    player.on('error', function() {
      console.error('Video player error:', player.error());
      
      // Display user-friendly error message
      const errorDisplay = document.createElement('div');
      errorDisplay.className = 'video-error-display';
      errorDisplay.innerHTML = `
        <div class="alert alert-danger">
          <i class="fa fa-exclamation-triangle"></i>
          <p>We're having trouble playing this video. Please try again later.</p>
        </div>
      `;
      
      // Replace video element with error message
      const videoContainer = document.querySelector('.video-container');
      if (videoContainer) {
        videoContainer.innerHTML = '';
        videoContainer.appendChild(errorDisplay);
      }
    });
    
    // Handle video quality selection if available
    setupQualitySelector(player);
  }
});

// Function to set up quality selector for the player
function setupQualitySelector(player) {
  // This would be implemented with actual quality sources in a real application
  // For this example, we'll create a simple mock
  
  const qualityLevels = [
    { label: '1080p', value: '1080', selected: true },
    { label: '720p', value: '720', selected: false },
    { label: '480p', value: '480', selected: false },
    { label: '360p', value: '360', selected: false },
    { label: 'Auto', value: 'auto', selected: false }
  ];
  
  // Create quality menu button
  const qualityButton = document.createElement('button');
  qualityButton.className = 'vjs-quality-button vjs-menu-button vjs-menu-button-popup vjs-control vjs-button';
  qualityButton.type = 'button';
  qualityButton.title = 'Quality';
  
  // Create button inner elements
  qualityButton.innerHTML = `
    <span class="vjs-icon-placeholder"></span>
    <span class="vjs-quality-value">1080p</span>
    <div class="vjs-menu">
      <ul class="vjs-menu-content" role="menu">
        ${qualityLevels.map(level => `
          <li class="vjs-menu-item ${level.selected ? 'vjs-selected' : ''}" 
              role="menuitemradio" 
              aria-checked="${level.selected}" 
              tabindex="-1" 
              data-quality="${level.value}">
            <span class="vjs-menu-item-text">${level.label}</span>
            <span class="vjs-control-text" aria-live="polite"></span>
          </li>
        `).join('')}
      </ul>
    </div>
  `;
  
  // Add to control bar if it exists
  const controlBar = player.getChild('controlBar');
  if (controlBar) {
    // Add quality button before fullscreen button
    const fullscreenToggle = controlBar.getChild('fullscreenToggle');
    if (fullscreenToggle) {
      controlBar.el().insertBefore(qualityButton, fullscreenToggle.el());
    } else {
      controlBar.el().appendChild(qualityButton);
    }
    
    // Add click handlers for quality options
    const qualityOptions = qualityButton.querySelectorAll('li[data-quality]');
    qualityOptions.forEach(option => {
      option.addEventListener('click', function() {
        // Get selected quality value
        const quality = this.getAttribute('data-quality');
        const qualityLabel = this.querySelector('.vjs-menu-item-text').textContent;
        
        // Update selected state in menu
        qualityOptions.forEach(opt => {
          opt.classList.remove('vjs-selected');
          opt.setAttribute('aria-checked', 'false');
        });
        this.classList.add('vjs-selected');
        this.setAttribute('aria-checked', 'true');
        
        // Update displayed quality value
        qualityButton.querySelector('.vjs-quality-value').textContent = qualityLabel;
        
        // In a real implementation, this would change the video source
        console.log(`Changing quality to ${quality}`);
      });
    });
  }
}

// Function to show recommendations when video ends
function showRecommendations() {
  const videoContainer = document.querySelector('.video-container');
  if (!videoContainer) return;
  
  // Get recommendations from the page if they exist
  const recommendationsContainer = document.getElementById('similar-concerts');
  if (recommendationsContainer) {
    // Create overlay with recommendations
    const overlay = document.createElement('div');
    overlay.className = 'video-ended-overlay';
    overlay.innerHTML = `
      <div class="recommendations-panel">
        <h3>Watch Next</h3>
        <div class="recommendations-content">
          ${recommendationsContainer.innerHTML}
        </div>
        <button class="btn btn-primary replay-button">
          <i class="fa fa-refresh"></i> Replay
        </button>
      </div>
    `;
    
    // Add overlay to container
    videoContainer.appendChild(overlay);
    
    // Handle replay button
    const replayButton = overlay.querySelector('.replay-button');
    if (replayButton) {
      replayButton.addEventListener('click', function() {
        // Remove overlay
        overlay.remove();
        
        // Restart video
        const player = videojs('concert-video');
        if (player) {
          player.currentTime(0);
          player.play();
        }
      });
    }
  }
}
