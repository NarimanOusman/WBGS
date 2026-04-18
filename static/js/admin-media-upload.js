(() => {
  const config = window.WAUAdminUploadConfig || {};
  const cloudName = config.cloudName;
  const uploadPreset = config.uploadPreset;
  const uploadEndpoint = config.uploadEndpoint;

  const projectSelect = document.getElementById('mediaProject');
  const slotSelect = document.getElementById('mediaSlot');
  const captionInput = document.getElementById('mediaCaption');
  const orderInput = document.getElementById('mediaOrder');
  const fileInput = document.getElementById('mediaFile');
  const uploadButton = document.getElementById('uploadMediaBtn');
  const statusEl = document.getElementById('uploadStatus');

  const setStatus = (message, isError = false) => {
    if (!statusEl) return;
    statusEl.textContent = message;
    statusEl.style.color = isError ? '#b91c1c' : '#0f3f66';
  };

  const getCsrfToken = () => {
    const cookie = document.cookie.split('; ').find((item) => item.startsWith('csrftoken='));
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
  };

  const uploadToCloudinary = async (file) => {
    if (!cloudName || !uploadPreset) {
      throw new Error('Cloudinary upload config is missing.');
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', uploadPreset);

    const response = await fetch(`https://api.cloudinary.com/v1_1/${cloudName}/auto/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || 'Cloudinary upload failed.');
    }

    return response.json();
  };

  const saveMediaUrl = async ({ projectId, slot, mediaUrl, mediaType, caption, order }) => {
    const response = await fetch(uploadEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        project_id: projectId,
        slot,
        media_url: mediaUrl,
        media_type: mediaType,
        caption,
        order,
      }),
    });

    const data = await response.json();
    if (!response.ok || !data.ok) {
      throw new Error(data.error || 'Failed to save media.');
    }

    return data;
  };

  const handleUpload = async () => {
    try {
      const file = fileInput?.files?.[0];
      const projectId = projectSelect?.value;
      const slot = slotSelect?.value || 'cover';
      const caption = captionInput ? captionInput.value.trim() : '';
      const order = orderInput ? Number(orderInput.value || 0) : 0;

      if (!projectId) {
        setStatus('Select a project first.', true);
        return;
      }

      if (!file) {
        setStatus('Choose an image or video file first.', true);
        return;
      }

      setStatus('Uploading to Cloudinary...');
      uploadButton.disabled = true;

      const cloudinaryResult = await uploadToCloudinary(file);
      const mediaType = cloudinaryResult.resource_type === 'video' ? 'video' : 'image';

      setStatus('Saving media to the project...');

      await saveMediaUrl({
        projectId,
        slot,
        mediaUrl: cloudinaryResult.secure_url,
        mediaType,
        caption,
        order,
      });

      setStatus('Upload complete. Refreshing page...');
      window.location.reload();
    } catch (error) {
      setStatus(error.message || 'Upload failed.', true);
    } finally {
      if (uploadButton) {
        uploadButton.disabled = false;
      }
    }
  };

  if (uploadButton) {
    uploadButton.addEventListener('click', handleUpload);
  }
})();
