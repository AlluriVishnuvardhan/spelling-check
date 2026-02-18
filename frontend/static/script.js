let stream = null;
let video = document.getElementById('video');
let canvas = document.getElementById('canvas');

function openCamera() {
    document.getElementById('camera-modal').style.display = 'block';
}

function closeCamera() {
    document.getElementById('camera-modal').style.display = 'none';
    stopCamera();
}

async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.style.display = 'block';
        
        // Show capture button, hide start button
        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('captureBtn').style.display = 'inline-block';
        
        // Clear previous results
        document.getElementById('cameraResults').innerHTML = '';
        
    } catch (error) {
        alert('Error accessing camera: ' + error.message);
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.style.display = 'none';
        stream = null;
        
        // Reset buttons
        document.getElementById('startBtn').style.display = 'inline-block';
        document.getElementById('captureBtn').style.display = 'none';
    }
}

async function capturePhoto() {
    if (!stream) {
        alert('Please start the camera first');
        return;
    }
    
    const resultsDiv = document.getElementById('cameraResults');
    resultsDiv.innerHTML = '<p style="text-align: center; color: #667eea;">📸 Processing photo and checking spelling...</p>';
    
    // Capture photo from video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    // Convert to base64
    const imageData = canvas.toDataURL('image/png');
    
    // Stop camera after capture
    stopCamera();
    
    try {
        const response = await fetch('/api/check-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        displayCameraResults(data);
    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = '<p style="color: #e74c3c; text-align: center;">Error processing image. Please try again.</p>';
    }
}

function displayCameraResults(data) {
    const resultsDiv = document.getElementById('cameraResults');
    
    if (data.error) {
        resultsDiv.innerHTML = `<p style="color: #e74c3c; text-align: center; padding: 15px;">${data.error}</p>`;
        return;
    }
    
    let html = `<h3>Detected Text:</h3><div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #ddd;">${data.extracted_text}</div>`;
    
    if (data.mistakes && data.mistakes.length > 0) {
        html += '<h3>Spelling Corrections:</h3>';
        data.mistakes.forEach(mistake => {
            html += `
                <div class="correction">
                    <div class="mistake-word">
                        <span class="wrong">'${mistake.word}'</span> → 
                        <span class="right">'${mistake.suggestion}'</span>
                    </div>
                    ${mistake.context ? `<div class="context-info">${mistake.context}</div>` : ''}
                </div>
            `;
        });
    } else {
        html += '<div class="perfect-camera">✅ No mistakes detected!</div>';
    }
    
    resultsDiv.innerHTML = html;
}

// PDF Upload Handler
async function handlePDFUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (file.type !== 'application/pdf') {
        alert('Please upload a PDF file');
        event.target.value = '';
        return;
    }
    
    const textarea = document.getElementById('textInput');
    textarea.value = '📄 Processing PDF...';
    
    const formData = new FormData();
    formData.append('pdf', file);
    
    try {
        const response = await fetch('/api/extract-pdf', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        console.log('PDF Response:', data);
        
        if (response.ok && data.text) {
            textarea.value = data.text;
            alert('✅ PDF text extracted! Click "Check Spelling" button.');
        } else if (data.error) {
            alert('❌ ' + data.error);
            textarea.value = '';
        } else {
            alert('❌ Could not extract text from PDF');
            textarea.value = '';
        }
    } catch (error) {
        console.error('PDF Error:', error);
        alert('❌ Network error. Check if server is running.');
        textarea.value = '';
    }
    
    event.target.value = '';
}

// Image Upload Handler
async function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file');
        event.target.value = '';
        return;
    }
    
    const textarea = document.getElementById('textInput');
    textarea.value = '🖼️ Processing image...';
    
    // Convert image to base64
    const reader = new FileReader();
    reader.onload = async function(e) {
        const imageData = e.target.result;
        
        try {
            const response = await fetch('/api/check-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageData })
            });
            
            const data = await response.json();
            console.log('Image Response:', data);
            
            if (response.ok && data.extracted_text) {
                textarea.value = data.extracted_text;
                alert('✅ Text extracted from image! Click "Check Spelling" button.');
            } else if (data.error) {
                alert('❌ ' + data.error);
                textarea.value = '';
            } else {
                alert('❌ Could not extract text from image');
                textarea.value = '';
            }
        } catch (error) {
            console.error('Image Error:', error);
            alert('❌ Network error. Check if server is running.');
            textarea.value = '';
        }
    };
    
    reader.readAsDataURL(file);
    event.target.value = '';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('camera-modal');
    if (event.target == modal) {
        closeCamera();
    }
}

// ZIP Upload Handler
async function handleZIPUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!file.name.endsWith('.zip')) {
        alert('Please upload a ZIP file');
        event.target.value = '';
        return;
    }
    
    const textarea = document.getElementById('textInput');
    textarea.value = '🌐 Processing website ZIP...';
    
    const formData = new FormData();
    formData.append('zip', file);
    
    try {
        const response = await fetch('/api/check-website-zip', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.text) {
            let result = `✅ Website Spell Check Complete!\n\n`;
            result += `📁 Processed ${data.total_files} files:\n${data.files_processed.join('\n')}\n\n`;
            
            if (data.mistakes && data.mistakes.length > 0) {
                result += `❌ Found ${data.mistakes.length} spelling mistakes:\n\n`;
                data.mistakes.slice(0, 20).forEach((m, i) => {
                    result += `${i+1}. "${m.word}" → "${m.suggestion}"${m.context ? ' (' + m.context + ')' : ''}\n`;
                });
                if (data.mistakes.length > 20) {
                    result += `\n... and ${data.mistakes.length - 20} more mistakes`;
                }
            } else {
                result += '✅ No spelling mistakes found! Your website text is perfect!';
            }
            
            textarea.value = result;
            alert('Website ZIP processed successfully!');
        } else if (data.error) {
            alert('ZIP Error: ' + data.error);
            textarea.value = '';
        } else {
            alert('Could not process ZIP file');
            textarea.value = '';
        }
    } catch (error) {
        console.error('ZIP Error:', error);
        alert('Error processing ZIP. Please check console for details.');
        textarea.value = '';
    }
    
    event.target.value = '';
}