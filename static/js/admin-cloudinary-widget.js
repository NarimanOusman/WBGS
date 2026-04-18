(function () {
  function getCloudinaryConfig(input) {
    return {
      cloudName: (input.dataset.cloudinaryCloudName || '').trim(),
      uploadPreset: (input.dataset.cloudinaryUploadPreset || '').trim(),
      slot: (input.dataset.cloudinarySlot || '').trim(),
    };
  }

  function makeStatusElement(anchor) {
    var status = document.createElement('span');
    status.className = 'help cloudinary-upload-status';
    status.style.marginLeft = '8px';
    status.textContent = '';
    anchor.parentNode.insertBefore(status, anchor.nextSibling);
    return status;
  }

  function setStatus(statusEl, message, isError) {
    if (!statusEl) return;
    statusEl.textContent = message;
    statusEl.style.color = isError ? '#b91c1c' : '#0f766e';
  }

  async function uploadFileToCloudinary(file, config) {
    var formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', config.uploadPreset);

    var response = await fetch('https://api.cloudinary.com/v1_1/' + config.cloudName + '/auto/upload', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      var text = await response.text();
      throw new Error(text || 'Upload failed.');
    }

    return response.json();
  }

  function fieldById(id) {
    return document.getElementById(id);
  }

  function connectUpload(urlInput) {
    if (!urlInput || urlInput.dataset.cloudinaryBound === '1') {
      return;
    }
    urlInput.dataset.cloudinaryBound = '1';

    var config = getCloudinaryConfig(urlInput);

    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'button';
    button.textContent = 'Upload to Cloudinary';
    button.style.marginLeft = '6px';

    var statusEl = makeStatusElement(urlInput);

    if (!config.cloudName || !config.uploadPreset) {
      button.disabled = true;
      setStatus(statusEl, 'Set CLOUDINARY_URL and CLOUDINARY_UPLOAD_PRESET in environment variables.', true);
    }

    urlInput.parentNode.insertBefore(button, urlInput.nextSibling);

    button.addEventListener('click', function () {
      var picker = document.createElement('input');
      picker.type = 'file';
      picker.accept = 'image/*,video/*';
      picker.style.display = 'none';
      document.body.appendChild(picker);

      picker.addEventListener('change', async function () {
        var file = picker.files && picker.files[0];
        if (!file) {
          document.body.removeChild(picker);
          return;
        }

        try {
          button.disabled = true;
          setStatus(statusEl, 'Uploading...', false);
          var result = await uploadFileToCloudinary(file, config);
          var mediaType = result.resource_type === 'video' ? 'video' : 'image';

          urlInput.value = result.secure_url || '';

          var urlId = urlInput.id || '';
          var mediaTypeInput = fieldById(urlId.replace('media_url', 'media_type').replace('cover_media_url', 'cover_media_type'));
          if (mediaTypeInput) {
            mediaTypeInput.value = mediaType;
          }

          var imageInput = fieldById(urlId.replace('media_url', 'image').replace('cover_media_url', 'image'));
          var videoInput = fieldById(urlId.replace('media_url', 'video').replace('cover_media_url', 'video'));
          if (imageInput) imageInput.value = '';
          if (videoInput) videoInput.value = '';

          setStatus(statusEl, 'Upload complete. Click Save to store changes.', false);
        } catch (error) {
          setStatus(statusEl, error.message || 'Upload failed.', true);
        } finally {
          button.disabled = false;
          document.body.removeChild(picker);
        }
      });

      picker.click();
    });
  }

  function bindAll() {
    var inputs = document.querySelectorAll('input.cloudinary-url-field');
    for (var i = 0; i < inputs.length; i++) {
      connectUpload(inputs[i]);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    bindAll();

    var observer = new MutationObserver(function () {
      bindAll();
    });

    observer.observe(document.body, { childList: true, subtree: true });
  });
})();
