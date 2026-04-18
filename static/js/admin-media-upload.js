(function () {
  const cfg = window.WAUAdminUploadConfig || {};
  const cloudName = (cfg.cloudName || '').trim();
  const uploadPreset = (cfg.uploadPreset || '').trim();
  const uploadEndpoint = cfg.uploadEndpoint || '/upload-media/';

  const statusEl = document.getElementById('uploadStatus');

  const createBtn = document.getElementById('createProjectBtn');
  const titleEl = document.getElementById('newProjectTitle');
  const categoryEl = document.getElementById('newProjectCategory');
  const statusFieldEl = document.getElementById('newProjectStatus');
  const progressEl = document.getElementById('newProjectProgress');
  const descEl = document.getElementById('newProjectDescription');
  const coverFileEl = document.getElementById('newProjectCoverFile');
  const galleryFilesEl = document.getElementById('newProjectGalleryFiles');

  const mediaBtn = document.getElementById('uploadMediaBtn');
  const mediaProjectEl = document.getElementById('mediaProject');
  const mediaSlotEl = document.getElementById('mediaSlot');
  const mediaCaptionEl = document.getElementById('mediaCaption');
  const mediaOrderEl = document.getElementById('mediaOrder');
  const mediaFileEl = document.getElementById('mediaFile');

  const setStatus = (msg, isError) => {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.style.color = isError ? '#b91c1c' : '#0f766e';
  };

  const getCsrfToken = () => {
    const cookie = document.cookie
      .split(';')
      .map((c) => c.trim())
      .find((c) => c.startsWith('csrftoken='));
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
  };

  const uploadToCloudinary = async (file) => {
    if (!cloudName || !uploadPreset) {
      throw new Error('Cloudinary is not configured. Set cloud name and upload preset in environment variables.');
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', uploadPreset);
    formData.append('folder', 'projects');

    const res = await fetch(`https://api.cloudinary.com/v1_1/${cloudName}/auto/upload`, {
      method: 'POST',
      body: formData,
    });

    const data = await res.json();
    if (!res.ok || !data.public_id) {
      const detail = data && data.error && data.error.message ? data.error.message : 'Upload failed.';
      throw new Error(detail);
    }

    return {
      public_id: data.public_id,
      format: data.format || '',
      resource_type: data.resource_type || '',
      secure_url: data.secure_url || '',
    };
  };

  const postJson = async (payload) => {
    const res = await fetch(uploadEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify(payload),
    });

    let data = {};
    try {
      data = await res.json();
    } catch (err) {
      data = { ok: false, message: 'Unexpected server response.' };
    }

    if (!res.ok || !data.ok) {
      throw new Error(data.message || 'Request failed.');
    }

    return data;
  };

  if (createBtn) {
    createBtn.addEventListener('click', async () => {
      try {
        const title = (titleEl && titleEl.value || '').trim();
        const category = (categoryEl && categoryEl.value || '').trim();
        const status = (statusFieldEl && statusFieldEl.value || 'Planned').trim();
        const description = (descEl && descEl.value || '').trim();
        const progress = parseInt((progressEl && progressEl.value) || '0', 10);
        const coverFile = coverFileEl && coverFileEl.files && coverFileEl.files[0];
        const galleryFiles = galleryFilesEl && galleryFilesEl.files ? Array.from(galleryFilesEl.files) : [];

        if (!title || !category || !description) {
          setStatus('Title, category, and description are required.', true);
          return;
        }

        if (!coverFile) {
          setStatus('Please choose a cover image.', true);
          return;
        }

        createBtn.disabled = true;
        setStatus('Uploading cover image...', false);

        const coverAsset = await uploadToCloudinary(coverFile);

        const galleryAssets = [];
        for (let i = 0; i < galleryFiles.length; i += 1) {
          setStatus(`Uploading gallery image ${i + 1} of ${galleryFiles.length}...`, false);
          const asset = await uploadToCloudinary(galleryFiles[i]);
          galleryAssets.push({ asset, caption: '', order: i });
        }

        setStatus('Saving project record...', false);

        await postJson({
          action: 'create_project',
          title,
          category,
          status,
          progress: Number.isFinite(progress) ? progress : 0,
          description,
          cover_asset: coverAsset,
          gallery_assets: galleryAssets,
        });

        setStatus('Project created successfully.', false);

        if (titleEl) titleEl.value = '';
        if (categoryEl) categoryEl.value = '';
        if (descEl) descEl.value = '';
        if (progressEl) progressEl.value = '0';
        if (coverFileEl) coverFileEl.value = '';
        if (galleryFilesEl) galleryFilesEl.value = '';

        window.setTimeout(() => {
          window.location.reload();
        }, 800);
      } catch (err) {
        setStatus(err.message || 'Failed to create project.', true);
      } finally {
        createBtn.disabled = false;
      }
    });
  }

  if (mediaBtn) {
    mediaBtn.addEventListener('click', async () => {
      try {
        const projectId = mediaProjectEl ? mediaProjectEl.value : '';
        const slot = mediaSlotEl ? mediaSlotEl.value : 'gallery';
        const caption = mediaCaptionEl ? mediaCaptionEl.value.trim() : '';
        const order = parseInt((mediaOrderEl && mediaOrderEl.value) || '0', 10);
        const file = mediaFileEl && mediaFileEl.files && mediaFileEl.files[0];

        if (!projectId) {
          setStatus('Select a project first.', true);
          return;
        }

        if (!file) {
          setStatus('Choose an image or video to upload.', true);
          return;
        }

        mediaBtn.disabled = true;
        setStatus('Uploading media...', false);

        const asset = await uploadToCloudinary(file);

        setStatus('Saving media record...', false);

        await postJson({
          action: 'add_media',
          project_id: projectId,
          slot,
          caption,
          order: Number.isFinite(order) ? order : 0,
          asset,
        });

        setStatus('Media uploaded successfully.', false);
        if (mediaCaptionEl) mediaCaptionEl.value = '';
        if (mediaOrderEl) mediaOrderEl.value = '0';
        if (mediaFileEl) mediaFileEl.value = '';
      } catch (err) {
        setStatus(err.message || 'Failed to upload media.', true);
      } finally {
        mediaBtn.disabled = false;
      }
    });
  }

  if (!cloudName || !uploadPreset) {
    setStatus('Set CLOUDINARY_CLOUD_NAME and CLOUDINARY_UPLOAD_PRESET in Vercel to enable direct upload.', true);
  }
})();
