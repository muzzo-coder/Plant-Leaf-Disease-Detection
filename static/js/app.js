document.addEventListener('DOMContentLoaded', () => {
    
    // Core Elements
    const appLayout = document.querySelector('.app-layout');
    const headerEl = document.querySelector('.app-header');
    const historyPanel = document.getElementById('history-panel');
    const aboutPanel = document.getElementById('about-panel');
    const navLinks = document.querySelectorAll('.nav-links a');

    // Upload Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseLink = document.querySelector('.browse-link');
    const placeholder = document.getElementById('upload-placeholder');
    const previewArea = document.getElementById('preview-area');
    const imagePreview = document.getElementById('image-preview');
    const btnRemove = document.getElementById('btn-remove');
    const btnPredict = document.getElementById('btn-predict');
    
    const loadingState = document.getElementById('loading-state');
    const resultsPanel = document.getElementById('results-panel');
    const btnNewScan = document.getElementById('btn-new-scan');
    
    // Modal Elements
    const webcamModal = document.getElementById('webcam-modal');
    const videoElement = document.getElementById('webcam-video');
    const canvasElement = document.getElementById('webcam-canvas');
    let stream = null;

    let currentFile = null;

    // --- Navigation Routing ---
    function switchPage(pageId) {
        // Update nav UI
        navLinks.forEach(link => link.classList.remove('active'));
        document.getElementById(`nav-${pageId}`).classList.add('active');

        // Hide all major sections
        appLayout.classList.add('hidden');
        headerEl.classList.add('hidden');
        historyPanel.classList.add('hidden');
        aboutPanel.classList.add('hidden');

        if (pageId === 'detector') {
            appLayout.classList.remove('hidden');
            headerEl.classList.remove('hidden');
        } else if (pageId === 'history') {
            historyPanel.classList.remove('hidden');
            renderHistory();
        } else if (pageId === 'about') {
            aboutPanel.classList.remove('hidden');
        }
    }

    document.getElementById('nav-detector').addEventListener('click', (e) => { e.preventDefault(); switchPage('detector'); });
    document.getElementById('nav-history').addEventListener('click', (e) => { e.preventDefault(); switchPage('history'); });
    document.getElementById('nav-about').addEventListener('click', (e) => { e.preventDefault(); switchPage('about'); });

    // --- Webcam Flow ---
    document.getElementById('btn-webcam').addEventListener('click', async () => {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error("Browser security policy blocked camera access. It requires HTTPS or localhost.");
            }
            stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
            videoElement.srcObject = stream;
            webcamModal.classList.remove('hidden');
        } catch (err) {
            alert(`Camera Access Denied:\n\nIf you are accessing this on a phone or another computer over the network (e.g., 192.168.x.x), modern browsers block the camera unless it is served over HTTPS.\n\nPlease test it directly on http://127.0.0.1:8080 or http://localhost:8080, or deploy it to a secure server.\n\nTechnical Details: ${err.message}`);
            console.error(err);
        }
    });

    document.getElementById('btn-close-webcam').addEventListener('click', () => {
        closeWebcam();
    });

    document.getElementById('btn-capture').addEventListener('click', () => {
        if (!stream) return;
        
        // Draw frame to canvas
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        const ctx = canvasElement.getContext('2d');
        ctx.drawImage(videoElement, 0, 0);
        
        // Convert to blob
        canvasElement.toBlob((blob) => {
            const file = new File([blob], "webcam_capture.jpg", { type: "image/jpeg" });
            // Simulate Data Transfer list
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            
            // Fire manually
            handleFiles(fileInput.files);
            closeWebcam();
            
            // Bring user to detector view if they weren't there
            switchPage('detector');
        }, 'image/jpeg', 0.95);
    });

    function closeWebcam() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        webcamModal.classList.add('hidden');
    }

    // --- Drag and Drop Handlers ---
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-active'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-active'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // --- File Input Handlers ---
    browseLink.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            
            if (!file.type.match('image.*')) {
                alert('Please upload a valid image file (PNG, JPG, JPEG)');
                return;
            }
            if (file.size > 16 * 1024 * 1024) {
                alert('File is too large. Maximum size is 16MB.');
                return;
            }
            
            currentFile = file;
            const reader = new FileReader();
            
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                placeholder.classList.add('hidden');
                previewArea.classList.remove('hidden');
                btnPredict.disabled = false;
            }
            
            reader.readAsDataURL(file);
        }
    }

    // --- Action Handlers ---
    btnRemove.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        imagePreview.src = '';
        previewArea.classList.add('hidden');
        placeholder.classList.remove('hidden');
        btnPredict.disabled = true;
    });

    btnNewScan.addEventListener('click', () => {
        // Reset state
        appLayout.classList.remove('with-results');
        resultsPanel.classList.add('hidden');
        btnRemove.click();
    });

    // --- Prediction API Call ---
    btnPredict.addEventListener('click', async () => {
        if (!currentFile) {
            alert("No file selected.");
            return;
        }

        // Show loading state
        loadingState.classList.remove('hidden');
        btnPredict.disabled = true;
        
        const formData = new FormData();
        formData.append('image', currentFile);

        try {
            // Smart routing: 
            // If running via Live Server or file://, hit the local flask port directly.
            // If running in production (Render, AWS), use relative path.
            const baseUrl = (window.location.protocol === 'file:' || window.location.port === '5500') 
                            ? 'http://127.0.0.1:8080' 
                            : '';
            const endpoint = `${baseUrl}/predict`;
            
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                if (response.status === 413) {
                    throw new Error("File is too large.");
                }
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData && errorData.error ? errorData.error : `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Hide loading
            loadingState.classList.add('hidden');
            
            if (data.success) {
                if (data.is_plant === false) {
                    alert(data.message);
                    btnRemove.click();
                    return;
                }
                
                // --- Save To History ---
                saveToHistory(data, currentFile);

                showResults(data);
            } else {
                alert(`Error: ${data.error || "Unknown error occurred"}`);
                btnRemove.click();
            }
            
        } catch (error) {
            console.error('Prediction failed:', error);
            alert(`Failed to connect with prediction server: ${error.message}`);
            loadingState.classList.add('hidden');
            btnPredict.disabled = false;
        }
    });

    // --- Render Results ---
    function showResults(data) {
        // Expand layout
        appLayout.classList.add('with-results');
        resultsPanel.classList.remove('hidden');

        // Populate DOM elements
        document.getElementById('disease-name').textContent = data.result.name;
        document.getElementById('disease-desc').textContent = data.result.description;
        
        // Confidence Ring UI
        const confPercent = Math.round(data.confidence * 100);
        document.getElementById('confidence-val').textContent = `${confPercent}%`;
        const ring = document.getElementById('confidence-ring');
        
        // Color based on confidence
        let strokeColor = '#10b981'; // green
        if(confPercent < 70) strokeColor = '#f59e0b'; // orange
        if(confPercent < 50) strokeColor = '#ef4444'; // red
        
        ring.style.background = `conic-gradient(${strokeColor} ${confPercent}%, rgba(255,255,255,0.1) 0%)`;

        // Severity Logic
        const severityEl = document.getElementById('severity-val');
        const severityIconEl = document.querySelector('#severity-badge i');
        const sv = data.result.severity;
        severityEl.textContent = sv;
        
        severityIconEl.className = 'fa-solid fa-shield'; // reset
        
        if (sv === 'High') {
            severityEl.parentElement.className = 'severity-badge sev-high';
            severityIconEl.classList.add('fa-shield-virus');
        } else if (sv === 'Medium') {
            severityEl.parentElement.className = 'severity-badge sev-medium';
            severityIconEl.classList.add('fa-shield-halved');
        } else {
            severityEl.parentElement.className = 'severity-badge sev-low';
            severityIconEl.classList.add('fa-shield-check');
        }

        // Actionable Info (Tabs)
        document.getElementById('chemical-val').textContent = data.result.chemical_treatment;
        document.getElementById('organic-val').textContent = data.result.organic_treatment;
        document.getElementById('prevention-val').textContent = data.result.prevention_steps;
        document.getElementById('causes-val').textContent = data.result.causes;
        document.getElementById('care-val').textContent = data.result.care_tips;
    }

    // Tabs Navigation Setup
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.add('hidden'));

            // Add active to clicked
            btn.classList.add('active');
            const targetId = 'tab-' + btn.getAttribute('data-tab');
            document.getElementById(targetId).classList.remove('hidden');
        });
    });

    // --- Local Storage History Engine ---
    function saveToHistory(apiData, fileObject) {
        // Read image via FileReader to save base64 locally
        const reader = new FileReader();
        reader.onload = function(e) {
            const base64Img = e.target.result;
            
            let historyStr = localStorage.getItem('leafai_history');
            let historyArray = historyStr ? JSON.parse(historyStr) : [];
            
            historyArray.unshift({
                id: Date.now(),
                date: new Date().toLocaleDateString(),
                image: base64Img,
                diseaseName: apiData.result.name,
                confidence: Math.round(apiData.confidence * 100),
                severity: apiData.result.severity
            });

            // Keep only latest 12
            if (historyArray.length > 12) historyArray = historyArray.slice(0, 12);
            
            localStorage.setItem('leafai_history', JSON.stringify(historyArray));
        };
        reader.readAsDataURL(fileObject);
    }

    function renderHistory() {
        const grid = document.getElementById('history-grid');
        grid.innerHTML = '';
        
        let historyStr = localStorage.getItem('leafai_history');
        if (!historyStr) {
            grid.innerHTML = '<p class="text-muted" style="text-align:center; width:100%; grid-column:1/-1;">No history found yet. Scan a leaf to get started!</p>';
            return;
        }

        const historyArray = JSON.parse(historyStr);
        if (historyArray.length === 0) {
            grid.innerHTML = '<p class="text-muted" style="text-align:center; width:100%; grid-column:1/-1;">No history found yet. Scan a leaf to get started!</p>';
            return;
        }

        historyArray.forEach(item => {
            const card = document.createElement('div');
            card.className = 'history-item';
            
            let sevClass = '#10b981';
            let icon = '🛡️';
            if(item.severity === 'High') { sevClass = '#ef4444'; icon = '🚨'; }
            if(item.severity === 'Medium') { sevClass = '#f59e0b'; icon = '⚠️'; }

            card.innerHTML = `
                <img src="${item.image}" class="history-img" alt="Scan">
                <div class="history-info">
                    <div class="history-title">${item.diseaseName}</div>
                    <div class="history-meta">
                        <span>${item.date}</span>
                        <span style="color: ${sevClass}; font-weight: bold;">${icon} ${item.confidence}%</span>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        });
    }

});
