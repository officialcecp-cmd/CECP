/**
 * CECP Image Cropper — Reusable 1:1 Crop Modal
 * Works on: edit_profile.html (frontend) + Django Admin (ClubMember, ClubApplication)
 *
 * Usage (auto-binds if data-cropper-input and data-cropper-hidden are set):
 *   <input type="file"   id="id_profile_picture" data-cropper-input data-cropper-hidden="id_profile_picture_cropped">
 *   <input type="hidden" id="id_profile_picture_cropped" name="profile_picture_cropped">
 */

(function () {
    'use strict';

    // ── Inject modal + styles once ────────────────────────────────────────────
    function ensureModal() {
        if (document.getElementById('cecp-crop-modal')) return;

        const style = document.createElement('style');
        style.textContent = `
            #cecp-crop-modal {
                display: none; position: fixed; inset: 0; z-index: 99999;
                background: rgba(2,6,23,0.92); backdrop-filter: blur(8px);
                align-items: center; justify-content: center;
            }
            #cecp-crop-modal.active { display: flex; }
            #cecp-crop-box {
                background: #0f172a; border: 1px solid rgba(6,182,212,0.25);
                border-radius: 16px; padding: 24px; max-width: 520px; width: 95%;
                box-shadow: 0 0 60px rgba(6,182,212,0.15);
            }
            #cecp-crop-box h3 {
                font-family: 'Inter', sans-serif; font-weight: 700;
                font-size: 16px; color: #e2e8f0; margin-bottom: 16px;
                letter-spacing: 0.02em;
            }
            #cecp-crop-preview-wrap {
                max-height: 380px; overflow: hidden; border-radius: 10px;
                background: #020617; border: 1px solid rgba(6,182,212,0.12);
            }
            #cecp-crop-preview-wrap img { display: block; max-width: 100%; }
            .cecp-crop-actions {
                display: flex; gap: 12px; margin-top: 18px; justify-content: flex-end;
            }
            .cecp-crop-btn {
                padding: 10px 22px; border-radius: 10px; font-size: 14px;
                font-weight: 600; cursor: pointer; border: none; transition: all 0.2s;
            }
            .cecp-crop-btn.cancel {
                background: #1e293b; color: #94a3b8; border: 1px solid #334155;
            }
            .cecp-crop-btn.cancel:hover { background: #334155; color: #e2e8f0; }
            .cecp-crop-btn.confirm {
                background: linear-gradient(135deg,#06b6d4,#6366f1);
                color: #fff; box-shadow: 0 4px 14px rgba(6,182,212,0.35);
            }
            .cecp-crop-btn.confirm:hover { opacity: 0.88; transform: translateY(-1px); }
            /* Preview thumbnail shown after crop */
            .cecp-crop-thumb {
                width: 72px; height: 72px; border-radius: 50%; object-fit: cover;
                border: 2px solid rgba(6,182,212,0.6); margin-top: 10px;
                display: none;
            }
        `;
        document.head.appendChild(style);

        const modal = document.createElement('div');
        modal.id = 'cecp-crop-modal';
        modal.innerHTML = `
            <div id="cecp-crop-box">
                <h3>✂ Crop Your Photo — 1:1 Square</h3>
                <div id="cecp-crop-preview-wrap">
                    <img id="cecp-crop-img" src="" alt="Crop Preview">
                </div>
                <div class="cecp-crop-actions">
                    <button class="cecp-crop-btn cancel" id="cecp-crop-cancel">Cancel</button>
                    <button class="cecp-crop-btn confirm" id="cecp-crop-confirm">Use This Crop</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    // ── Load Cropper.js from CDN if not already present ───────────────────────
    function loadCropperJS(callback) {
        if (window.Cropper) { callback(); return; }

        // CSS
        if (!document.querySelector('link[href*="cropperjs"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.css';
            document.head.appendChild(link);
        }
        // JS
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.js';
        script.onload = callback;
        document.head.appendChild(script);
    }

    // ── Bind a single file input ──────────────────────────────────────────────
    function bindInput(fileInput) {
        if (fileInput._ceopCropBound) return;
        fileInput._ceopCropBound = true;

        // Find or create the hidden + preview elements
        const hiddenName = fileInput.dataset.cropperHidden || (fileInput.name + '_cropped');
        let hidden = document.getElementById(hiddenName) ||
                     document.querySelector(`[name="${hiddenName}"]`);
        if (!hidden) {
            hidden = document.createElement('input');
            hidden.type = 'hidden';
            hidden.name = hiddenName;
            hidden.id = hiddenName;
            fileInput.parentNode.insertBefore(hidden, fileInput.nextSibling);
        }

        // Thumbnail preview
        let thumb = fileInput.parentNode.querySelector('.cecp-crop-thumb');
        if (!thumb) {
            thumb = document.createElement('img');
            thumb.className = 'cecp-crop-thumb';
            thumb.alt = 'Cropped preview';
            fileInput.parentNode.appendChild(thumb);
        }

        fileInput.addEventListener('change', function () {
            const file = this.files[0];
            if (!file || !file.type.startsWith('image/')) return;

            loadCropperJS(function () {
                ensureModal();

                const reader = new FileReader();
                reader.onload = function (e) {
                    const modal = document.getElementById('cecp-crop-modal');
                    const img   = document.getElementById('cecp-crop-img');

                    // Destroy previous cropper instance if any
                    if (window._ceopCropperInstance) {
                        window._ceopCropperInstance.destroy();
                        window._ceopCropperInstance = null;
                    }

                    img.src = e.target.result;
                    modal.classList.add('active');

                    // Short delay so the image is rendered before Cropper initialises
                    setTimeout(function () {
                        window._ceopCropperInstance = new Cropper(img, {
                            aspectRatio: 1,
                            viewMode: 1,
                            autoCropArea: 0.85,
                            movable: true,
                            zoomable: true,
                            rotatable: false,
                            scalable: false,
                            cropBoxResizable: true,
                            guides: true,
                            center: true,
                            highlight: false,
                            background: false,
                            responsive: true,
                            checkCrossOrigin: false,
                        });
                    }, 150);

                    // Confirm
                    document.getElementById('cecp-crop-confirm').onclick = function () {
                        const canvas = window._ceopCropperInstance.getCroppedCanvas({
                            width: 512, height: 512,
                            imageSmoothingEnabled: true,
                            imageSmoothingQuality: 'high'
                        });
                        canvas.toBlob(function (blob) {
                            const dataURL = canvas.toDataURL('image/jpeg', 0.92);
                            hidden.value = dataURL;   // store as base64 in hidden field
                            thumb.src = dataURL;
                            thumb.style.display = 'block';
                            modal.classList.remove('active');
                            window._ceopCropperInstance.destroy();
                            window._ceopCropperInstance = null;
                            // Clear the file input so Django won't save the original
                            fileInput.value = '';
                        }, 'image/jpeg', 0.92);
                    };

                    // Cancel
                    document.getElementById('cecp-crop-cancel').onclick = function () {
                        modal.classList.remove('active');
                        if (window._ceopCropperInstance) {
                            window._ceopCropperInstance.destroy();
                            window._ceopCropperInstance = null;
                        }
                        fileInput.value = '';
                    };
                };
                reader.readAsDataURL(file);
            });
        });
    }

    // ── Auto-bind on DOMContentLoaded ────────────────────────────────────────
    function init() {
        // Frontend: any input with data-cropper-input attribute
        document.querySelectorAll('input[type="file"][data-cropper-input]')
            .forEach(bindInput);

        // Admin: bind specific field IDs used in ClubMember + ClubApplication admins
        ['id_profile_image', 'id_profile_photo'].forEach(function (id) {
            const el = document.getElementById(id);
            if (el) {
                el.setAttribute('data-cropper-input', '');
                el.setAttribute('data-cropper-hidden', id + '_cropped');
                bindInput(el);
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
