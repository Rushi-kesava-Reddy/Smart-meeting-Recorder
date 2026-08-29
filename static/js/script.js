/**
 * Smart Meeting Recorder using Generative AI - Client Application Script
 * Frontend Web Audio Recording, Canvas Visualization, REST API Integration & UI State Management
 */

document.addEventListener('DOMContentLoaded', () => {
    // =========================================================================
    // GLOBAL STATE & DOM ELEMENTS
    // =========================================================================
    let mediaRecorder = null;
    let audioChunks = [];
    let audioContext = null;
    let analyser = null;
    let microphoneStream = null;
    let animationFrameId = null;
    let recordingStartTime = 0;
    let timerInterval = null;

    // DOM Elements - Navigation & Layout
    const sidebarToggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const toastContainer = document.getElementById('toast-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const spinnerTitle = document.getElementById('spinner-title');
    const spinnerDesc = document.getElementById('spinner-desc');

    // DOM Elements - Status Badges
    const badgeAudio = document.getElementById('badge-audio');
    const badgeTranscript = document.getElementById('badge-transcript');
    const badgeSummary = document.getElementById('badge-summary');
    const badgePdf = document.getElementById('badge-pdf');

    // DOM Elements - Audio Recorder (Module 1)
    const btnStartRecord = document.getElementById('btn-start-record');
    const btnStopRecord = document.getElementById('btn-stop-record');
    const waveformCanvas = document.getElementById('waveform-canvas');
    const recordingTimer = document.getElementById('recording-timer');
    const recStatusPill = document.getElementById('rec-status-pill');
    const recStatusLabel = document.getElementById('rec-status-label');
    const recordingSuccessAlert = document.getElementById('recording-success-alert');
    const recordingErrorAlert = document.getElementById('recording-error-alert');
    const recordingErrorText = document.getElementById('recording-error-text');
    const uploadForm = document.getElementById('upload-form');
    const audioFileInput = document.getElementById('audio-file-input');

    // DOM Elements - Speech To Text (Module 2)
    const btnConvertStt = document.getElementById('btn-convert-stt');
    const transcriptTextarea = document.getElementById('transcript-textarea');
    const btnCopyTranscript = document.getElementById('btn-copy-transcript');
    const sttAlert = document.getElementById('stt-alert');
    const sttAlertText = document.getElementById('stt-alert-text');
    const audioFileStatus = document.getElementById('audio-file-status');
    const btnQuickTranscribe = document.getElementById('btn-quick-transcribe');

    // DOM Elements - Summarizer (Module 3)
    const btnGenerateSummary = document.getElementById('btn-generate-summary');
    const summaryContent = document.getElementById('summary-content');
    const summaryAlert = document.getElementById('summary-alert');
    const summaryAlertText = document.getElementById('summary-alert-text');
    const transcriptFileStatus = document.getElementById('transcript-file-status');

    // DOM Elements - PDF Report (Module 4)
    const btnGeneratePdf = document.getElementById('btn-generate-pdf');
    const btnDownloadPdf = document.getElementById('btn-download-pdf');
    const reportSuccessAlert = document.getElementById('report-success-alert');
    const reportErrorAlert = document.getElementById('report-error-alert');
    const reportErrorText = document.getElementById('report-error-text');
    const reportInputsStatus = document.getElementById('report-inputs-status');

    // =========================================================================
    // INITIALIZATION & ARTIFACT STATUS CHECK
    // =========================================================================
    fetchSystemStatus();

    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Canvas setup if canvas exists
    let canvasCtx = null;
    if (waveformCanvas) {
        canvasCtx = waveformCanvas.getContext('2d');
        drawIdleWaveform(canvasCtx, waveformCanvas.width, waveformCanvas.height);
    }

    // =========================================================================
    // SYSTEM STATUS & STEP TRACKER
    // =========================================================================
    async function fetchSystemStatus() {
        try {
            const response = await fetch('/api/status');
            if (!response.ok) return;

            const data = await response.json();
            updateArtifactBadges(data);
            updateWorkflowStepper(data);

            // Update transcript textarea if available
            if (transcriptTextarea && data.transcript) {
                transcriptTextarea.value = data.transcript;
            }

            // Update summary card if available
            if (summaryContent && data.summary) {
                summaryContent.innerHTML = formatSummaryText(data.summary);
            }

            // Module status tags
            if (audioFileStatus) {
                audioFileStatus.className = data.has_audio ? 'status-tag tag-ready' : 'status-tag tag-wait';
                audioFileStatus.innerHTML = data.has_audio
                    ? '<i class="fa-solid fa-circle-check"></i> meetings/meeting.wav Ready'
                    : '<i class="fa-solid fa-clock"></i> Awaiting meetings/meeting.wav';
            }

            if (transcriptFileStatus) {
                transcriptFileStatus.className = data.has_transcript ? 'status-tag tag-ready' : 'status-tag tag-wait';
                transcriptFileStatus.innerHTML = data.has_transcript
                    ? '<i class="fa-solid fa-circle-check"></i> meetings/transcript.txt Ready'
                    : '<i class="fa-solid fa-clock"></i> Awaiting meetings/transcript.txt';
            }

            if (reportInputsStatus) {
                const inputsReady = data.has_transcript && data.has_summary;
                reportInputsStatus.className = inputsReady ? 'status-tag tag-ready' : 'status-tag tag-wait';
                reportInputsStatus.innerHTML = inputsReady
                    ? '<i class="fa-solid fa-circle-check"></i> Transcript & Summary Ready'
                    : '<i class="fa-solid fa-clock"></i> Transcript/Summary Missing';
            }

            if (btnDownloadPdf) {
                if (data.has_pdf) {
                    btnDownloadPdf.classList.remove('disabled');
                    btnDownloadPdf.removeAttribute('disabled');
                    if (reportSuccessAlert) reportSuccessAlert.classList.remove('hidden');
                } else {
                    btnDownloadPdf.classList.add('disabled');
                }
            }

            // Module page meta status tags
            const mod1Status = document.getElementById('mod1-status');
            const mod2Status = document.getElementById('mod2-status');
            const mod3Status = document.getElementById('mod3-status');
            const mod4Status = document.getElementById('mod4-status');

            if (mod1Status) mod1Status.innerHTML = data.has_audio ? '<span class="text-success">Available</span>' : 'Not Recorded';
            if (mod2Status) mod2Status.innerHTML = data.has_transcript ? '<span class="text-success">Transcribed</span>' : 'Not Generated';
            if (mod3Status) mod3Status.innerHTML = data.has_summary ? '<span class="text-success">Summarized</span>' : 'Not Generated';
            if (mod4Status) mod4Status.innerHTML = data.has_pdf ? '<span class="text-success">PDF Ready</span>' : 'Not Created';

        } catch (err) {
            console.error('Error fetching system status:', err);
        }
    }

    function updateArtifactBadges(data) {
        if (badgeAudio) {
            badgeAudio.className = data.has_audio ? 'badge badge-success' : 'badge badge-neutral';
        }
        if (badgeTranscript) {
            badgeTranscript.className = data.has_transcript ? 'badge badge-success' : 'badge badge-neutral';
        }
        if (badgeSummary) {
            badgeSummary.className = data.has_summary ? 'badge badge-success' : 'badge badge-neutral';
        }
        if (badgePdf) {
            badgePdf.className = data.has_pdf ? 'badge badge-success' : 'badge badge-neutral';
        }
    }

    function updateWorkflowStepper(data) {
        const step1 = document.getElementById('step-1');
        const step2 = document.getElementById('step-2');
        const step3 = document.getElementById('step-3');
        const step4 = document.getElementById('step-4');
        const step5 = document.getElementById('step-5');

        if (step1) step1.classList.toggle('active', true);
        if (step2) step2.classList.toggle('active', data.has_audio);
        if (step3) step3.classList.toggle('active', data.has_transcript);
        if (step4) step4.classList.toggle('active', data.has_summary);
        if (step5) step5.classList.toggle('active', data.has_pdf);
    }

    // =========================================================================
    // MODULE 1: AUDIO RECORDING (BROWSER MICROPHONE & WEBAUDIO)
    // =========================================================================
    if (btnStartRecord) {
        btnStartRecord.addEventListener('click', startMicrophoneRecording);
    }

    if (btnStopRecord) {
        btnStopRecord.addEventListener('click', stopMicrophoneRecording);
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFileUpload);
    }

    function getAudioMediaStream() {
        if (navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
            return navigator.mediaDevices.getUserMedia({ audio: true, video: false });
        }

        const legacyGetUserMedia = navigator.getUserMedia ||
                                   navigator.webkitGetUserMedia ||
                                   navigator.mozGetUserMedia ||
                                   navigator.msGetUserMedia;

        if (legacyGetUserMedia) {
            return new Promise((resolve, reject) => {
                legacyGetUserMedia.call(navigator, { audio: true, video: false }, resolve, reject);
            });
        }

        return Promise.reject(new Error(
            "Microphone API (navigator.mediaDevices.getUserMedia) is not supported or security context blocked it. Access via http://127.0.0.1:5000 or HTTPS."
        ));
    }

    function resetRecordingUI() {
        if (btnStartRecord) btnStartRecord.disabled = false;
        if (btnStopRecord) btnStopRecord.disabled = true;
        if (recStatusPill) recStatusPill.className = 'rec-status-pill';
        if (recStatusLabel) recStatusLabel.textContent = 'Ready';
        if (timerInterval) clearInterval(timerInterval);
        if (recordingTimer) recordingTimer.textContent = '00:00';
    }

    function handleMicrophoneError(err) {
        let userMsg = '';
        const errName = err ? (err.name || '') : '';
        const errMsg = err ? (err.message || '') : '';

        if (errName === 'NotAllowedError' || errName === 'PermissionDeniedError') {
            userMsg = 'Microphone permission was denied. Please click the lock icon in your browser address bar to allow microphone access.';
        } else if (errName === 'NotFoundError' || errName === 'DevicesNotFoundError') {
            userMsg = 'No microphone hardware found. Please connect a microphone and try again.';
        } else if (errName === 'NotReadableError' || errName === 'TrackStartError') {
            userMsg = 'Microphone is currently in use by another application (e.g. Zoom, Teams, Discord). Please close other apps and retry.';
        } else if (errName === 'SecurityError') {
            userMsg = 'Microphone access blocked due to insecure HTTP context. Open via http://127.0.0.1:5000, http://localhost:5000, or HTTPS.';
        } else if (errName === 'AbortError') {
            userMsg = 'Microphone recording request was aborted.';
        } else {
            userMsg = 'Microphone error: ' + (errMsg || errName || 'Permission denied or browser unsupported.');
        }

        showMicrophoneError(userMsg);
    }

    function showMicrophoneError(msg) {
        if (recordingErrorAlert && recordingErrorText) {
            recordingErrorText.textContent = msg;
            recordingErrorAlert.classList.remove('hidden');
        }
        showToast(msg, 'error');
    }

    async function startMicrophoneRecording() {
        console.log("Microphone request started");

        if (recordingSuccessAlert) recordingSuccessAlert.classList.add('hidden');
        if (recordingErrorAlert) recordingErrorAlert.classList.add('hidden');

        if (!navigator.mediaDevices && !navigator.getUserMedia && !navigator.webkitGetUserMedia && !navigator.mozGetUserMedia) {
            const msg = "Browser does not support mediaDevices.getUserMedia or security context blocked it. Access via http://127.0.0.1:5000 or HTTPS.";
            console.error(msg);
            showMicrophoneError(msg);
            resetRecordingUI();
            return;
        }

        try {
            audioChunks = [];
            microphoneStream = await getAudioMediaStream();
            console.log("Microphone permission granted");

            // Initialize AudioContext & Analyser for Canvas Animation
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            const source = audioContext.createMediaStreamSource(microphoneStream);
            source.connect(analyser);

            let mimeType = '';
            if (window.MediaRecorder) {
                if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                    mimeType = 'audio/webm;codecs=opus';
                } else if (MediaRecorder.isTypeSupported('audio/webm')) {
                    mimeType = 'audio/webm';
                } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
                    mimeType = 'audio/mp4';
                } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
                    mimeType = 'audio/ogg';
                }
            }

            const recorderOptions = mimeType ? { mimeType } : {};
            mediaRecorder = new MediaRecorder(microphoneStream, recorderOptions);

            mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                console.log("Recording stopped");
                const finalMimeType = (mediaRecorder && mediaRecorder.mimeType) ? mediaRecorder.mimeType : 'audio/webm';
                const audioBlob = new Blob(audioChunks, { type: finalMimeType });
                console.log("Audio blob created", { size: audioBlob.size, type: audioBlob.type });
                await saveAudioToServer(audioBlob);
            };

            mediaRecorder.start(100);
            console.log("Recording started");

            // UI State Changes
            btnStartRecord.disabled = true;
            btnStopRecord.disabled = false;
            if (recStatusPill) recStatusPill.className = 'rec-status-pill recording';
            if (recStatusLabel) recStatusLabel.textContent = 'Recording Live...';

            // Start Timer
            recordingStartTime = Date.now();
            updateTimerDisplay();
            timerInterval = setInterval(updateTimerDisplay, 1000);

            // Start Waveform Canvas Animation
            if (canvasCtx && waveformCanvas) {
                visualizeLiveWaveform(canvasCtx, waveformCanvas.width, waveformCanvas.height);
            }

            showToast('Microphone recording started.', 'info');
        } catch (err) {
            console.error('Microphone access error:', err);
            resetRecordingUI();
            handleMicrophoneError(err);
        }
    }

    function stopMicrophoneRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }

        // Stop Microphone Streams
        if (microphoneStream) {
            microphoneStream.getTracks().forEach(track => track.stop());
        }

        // Stop Timer
        clearInterval(timerInterval);

        // Cancel Canvas Animation
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }

        if (canvasCtx && waveformCanvas) {
            drawIdleWaveform(canvasCtx, waveformCanvas.width, waveformCanvas.height);
        }

        // Reset UI Buttons
        btnStartRecord.disabled = false;
        btnStopRecord.disabled = true;
        if (recStatusPill) recStatusPill.className = 'rec-status-pill';
        if (recStatusLabel) recStatusLabel.textContent = 'Ready';
    }

    async function saveAudioToServer(blob) {
        console.log("Upload started");
        showSpinner('Saving Audio Recording...', 'Uploading microphone recording to meetings/meeting.wav');
        try {
            const formData = new FormData();
            formData.append('audio_file', blob, 'meeting.wav');

            const response = await fetch('/api/save_audio', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            hideSpinner();

            if (response.ok && result.status === 'success') {
                console.log("Upload completed");
                if (recordingSuccessAlert) recordingSuccessAlert.classList.remove('hidden');
                showToast('Recording Completed Successfully', 'success');
                fetchSystemStatus();
            } else {
                console.error("Upload failed:", result.message);
                showMicrophoneError(result.message || 'Failed to save audio recording.');
            }
        } catch (err) {
            hideSpinner();
            console.error('Error saving audio to server:', err);
            showMicrophoneError('Network error saving audio: ' + err.message);
        }
    }


    async function handleFileUpload(e) {
        e.preventDefault();
        if (!audioFileInput || !audioFileInput.files[0]) {
            showToast('Please select a WAV audio file first.', 'error');
            return;
        }

        const file = audioFileInput.files[0];
        showSpinner('Uploading Audio File...', 'Saving uploaded audio to meetings/meeting.wav');

        try {
            const formData = new FormData();
            formData.append('audio_file', file, 'meeting.wav');

            const response = await fetch('/api/save_audio', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            hideSpinner();

            if (response.ok && result.status === 'success') {
                if (recordingSuccessAlert) recordingSuccessAlert.classList.remove('hidden');
                showToast('Audio uploaded and saved as meetings/meeting.wav', 'success');
                fetchSystemStatus();
            } else {
                showToast(result.message || 'Failed to upload audio file', 'error');
            }
        } catch (err) {
            hideSpinner();
            showToast('Upload error: ' + err.message, 'error');
        }
    }

    function updateTimerDisplay() {
        if (!recordingTimer) return;
        const elapsedSec = Math.floor((Date.now() - recordingStartTime) / 1000);
        const mins = String(Math.floor(elapsedSec / 60)).padStart(2, '0');
        const secs = String(elapsedSec % 60).padStart(2, '0');
        recordingTimer.textContent = `${mins}:${secs}`;
    }

    // Canvas Animation Functions
    function drawIdleWaveform(ctx, width, height) {
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, width, height);

        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        ctx.lineTo(width, height / 2);
        ctx.stroke();
    }

    function visualizeLiveWaveform(ctx, width, height) {
        if (!analyser) return;

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        function draw() {
            animationFrameId = requestAnimationFrame(draw);
            analyser.getByteTimeDomainData(dataArray);

            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, width, height);

            ctx.lineWidth = 3;
            ctx.strokeStyle = '#60a5fa';
            ctx.beginPath();

            const sliceWidth = width * 1.0 / bufferLength;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                const v = dataArray[i] / 128.0;
                const y = v * height / 2;

                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }

                x += sliceWidth;
            }

            ctx.lineTo(width, height / 2);
            ctx.stroke();
        }

        draw();
    }

    // =========================================================================
    // MODULE 2: SPEECH TO TEXT (OPENAI WHISPER)
    // =========================================================================
    if (btnConvertStt) {
        btnConvertStt.addEventListener('click', runSpeechToText);
    }

    if (btnQuickTranscribe) {
        btnQuickTranscribe.addEventListener('click', async () => {
            await runSpeechToText();
            window.location.href = '/transcript';
        });
    }

    if (btnCopyTranscript) {
        btnCopyTranscript.addEventListener('click', () => {
            if (transcriptTextarea && transcriptTextarea.value) {
                navigator.clipboard.writeText(transcriptTextarea.value);
                showToast('Transcript copied to clipboard!', 'success');
            }
        });
    }

    let sttPollInterval = null;

    async function runSpeechToText() {
        showSpinner('Converting Speech to Text...', 'Executing OpenAI Whisper model on meetings/meeting.wav...');

        if (sttAlert && sttAlertText) {
            sttAlert.className = 'alert alert-info';
            sttAlertText.textContent = 'Executing speech_to_text.py with OpenAI Whisper...';
            sttAlert.classList.remove('hidden');
        }

        try {
            const response = await fetch('/api/transcribe', { method: 'POST' });
            const result = await response.json();

            if (!response.ok || result.status === 'error') {
                hideSpinner();
                const errMessage = result.message || 'Speech to text conversion failed to start.';
                if (sttAlert && sttAlertText) {
                    sttAlert.className = 'alert alert-danger';
                    sttAlertText.textContent = errMessage;
                    sttAlert.classList.remove('hidden');
                }
                showToast(errMessage, 'error');
                return;
            }

            // Start polling status until transcription finishes or errors out
            startSttPolling();

        } catch (err) {
            hideSpinner();
            console.error('Speech to text API error:', err);
            if (sttAlert && sttAlertText) {
                sttAlert.className = 'alert alert-danger';
                sttAlertText.textContent = 'Network or server error: ' + err.message;
                sttAlert.classList.remove('hidden');
            }
            showToast('Error calling transcription endpoint: ' + err.message, 'error');
        }
    }

    function startSttPolling() {
        if (sttPollInterval) {
            clearInterval(sttPollInterval);
        }

        sttPollInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/status');
                if (!response.ok) return;

                const data = await response.json();
                updateArtifactBadges(data);
                updateWorkflowStepper(data);

                if (data.transcription_status === 'completed') {
                    clearInterval(sttPollInterval);
                    sttPollInterval = null;
                    hideSpinner();

                    if (transcriptTextarea) {
                        transcriptTextarea.value = data.transcript;
                    }
                    if (sttAlert && sttAlertText) {
                        sttAlert.className = 'alert alert-success';
                        sttAlertText.textContent = 'Speech converted to text successfully and saved to meetings/transcript.txt!';
                        sttAlert.classList.remove('hidden');
                    }
                    showToast('Speech To Text Completed Successfully!', 'success');
                    fetchSystemStatus();

                } else if (data.transcription_status === 'error') {
                    clearInterval(sttPollInterval);
                    sttPollInterval = null;
                    hideSpinner();

                    const errorMsg = data.transcription_error || 'Transcription failed due to an error.';
                    if (sttAlert && sttAlertText) {
                        sttAlert.className = 'alert alert-danger';
                        sttAlertText.textContent = errorMsg;
                        sttAlert.classList.remove('hidden');
                    }
                    showToast(errorMsg, 'error');
                }
            } catch (err) {
                console.error('Error polling transcription status:', err);
            }
        }, 1500);
    }


    // =========================================================================
    // MODULE 3: MEETING SUMMARIZATION (TRANSFORMERS)
    // =========================================================================
    if (btnGenerateSummary) {
        btnGenerateSummary.addEventListener('click', runSummarization);
    }

    async function runSummarization() {
        showSpinner('Generating AI Summary...', 'Executing summarizer.py to extract core highlights and decision points.');
        try {
            const response = await fetch('/api/summarize', { method: 'POST' });
            const result = await response.json();
            hideSpinner();

            if (response.ok && result.status === 'success') {
                if (summaryContent) {
                    summaryContent.innerHTML = formatSummaryText(result.summary);
                }
                if (summaryAlert && summaryAlertText) {
                    summaryAlert.className = 'alert alert-success';
                    summaryAlertText.textContent = 'Meeting summary generated successfully and saved to meetings/summary.txt!';
                    summaryAlert.classList.remove('hidden');
                }
                showToast('Meeting Summary Generated Successfully!', 'success');
                fetchSystemStatus();
            } else {
                if (summaryAlert && summaryAlertText) {
                    summaryAlert.className = 'alert alert-danger';
                    summaryAlertText.textContent = result.message || 'Summarization failed.';
                    summaryAlert.classList.remove('hidden');
                }
                showToast(result.message || 'Summarization error', 'error');
            }
        } catch (err) {
            hideSpinner();
            console.error('Summarization API error:', err);
            showToast('Error generating summary: ' + err.message, 'error');
        }
    }

    function formatSummaryText(text) {
        if (!text) return '<p class="placeholder-text">No summary content available.</p>';
        const paragraphs = text.split('\n\n');
        return paragraphs.map(p => `<p>• ${p.replace(/\n/g, '<br>')}</p>`).join('');
    }

    // =========================================================================
    // MODULE 4: PDF REPORT GENERATION (REPORTLAB)
    // =========================================================================
    if (btnGeneratePdf) {
        btnGeneratePdf.addEventListener('click', runReportGeneration);
    }

    async function runReportGeneration() {
        showSpinner('Building PDF Report...', 'Executing report_generator.py using ReportLab document engine.');
        try {
            const response = await fetch('/api/generate_report', { method: 'POST' });
            const result = await response.json();
            hideSpinner();

            if (response.ok && result.status === 'success') {
                if (reportSuccessAlert) reportSuccessAlert.classList.remove('hidden');
                if (reportErrorAlert) reportErrorAlert.classList.add('hidden');

                if (btnDownloadPdf) {
                    btnDownloadPdf.classList.remove('disabled');
                    btnDownloadPdf.removeAttribute('disabled');
                }

                showToast('Report Generated Successfully', 'success');
                fetchSystemStatus();
            } else {
                if (reportErrorAlert && reportErrorText) {
                    reportErrorText.textContent = result.message || 'Failed to generate PDF report.';
                    reportErrorAlert.classList.remove('hidden');
                }
                showToast(result.message || 'PDF Generation Error', 'error');
            }
        } catch (err) {
            hideSpinner();
            console.error('PDF report API error:', err);
            showToast('Error calling PDF report generator: ' + err.message, 'error');
        }
    }

    // =========================================================================
    // UTILITY HELPERS: SPINNER & TOAST NOTIFICATIONS
    // =========================================================================
    function showSpinner(title, desc) {
        if (spinnerTitle) spinnerTitle.textContent = title || 'Processing...';
        if (spinnerDesc) spinnerDesc.textContent = desc || 'Please wait while the system processes request.';
        if (loadingSpinner) loadingSpinner.classList.remove('hidden');
    }

    function hideSpinner() {
        if (loadingSpinner) loadingSpinner.classList.add('hidden');
    }

    function showToast(message, type = 'info') {
        if (!toastContainer) return;
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        let icon = 'fa-circle-info';
        if (type === 'success') icon = 'fa-circle-check';
        if (type === 'error') icon = 'fa-circle-exclamation';

        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
});
