/**
 * Multilingual AI Smart Meeting Recorder & Intelligent Assistant - Client Application
 * Frontend Web Audio, Multilingual STT, Translation, Summarization, Email Drafting,
 * Action Item Rendering, Unicode PDF Engine, and College Demo Mode Orchestration.
 */

document.addEventListener('DOMContentLoaded', () => {
    // =========================================================================
    // STATE & DOM REFERENCES
    // =========================================================================
    let mediaRecorder = null;
    let audioChunks = [];
    let audioContext = null;
    let analyser = null;
    let microphoneStream = null;
    let animationFrameId = null;
    let recordingStartTime = 0;
    let timerInterval = null;
    let sttPollInterval = null;

    // Layout & Navigation
    const sidebarToggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const toastContainer = document.getElementById('toast-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const spinnerTitle = document.getElementById('spinner-title');
    const spinnerDesc = document.getElementById('spinner-desc');
    const headerDetectedLang = document.getElementById('header-detected-lang');

    // Artifact Status Badges
    const badgeAudio = document.getElementById('badge-audio');
    const badgeTranscript = document.getElementById('badge-transcript');
    const badgeSummary = document.getElementById('badge-summary');
    const badgeEmail = document.getElementById('badge-email');
    const badgePdf = document.getElementById('badge-pdf');

    // Dashboard Metrics
    const metricLanguage = document.getElementById('metric-language');
    const metricDuration = document.getElementById('metric-duration');
    const metricWords = document.getElementById('metric-words');
    const metricActions = document.getElementById('metric-actions');
    const metricPriority = document.getElementById('metric-priority');

    // Global Language Toolbar Selectors
    const globalSpeechLang = document.getElementById('global-speech-lang');
    const globalTransLang = document.getElementById('global-trans-lang');
    const globalSummaryLang = document.getElementById('global-summary-lang');

    // Demo Modal Elements
    const demoModal = document.getElementById('demo-modal');
    const btnOpenDemoModal = document.getElementById('btn-open-demo-modal');
    const btnCloseDemoModal = document.getElementById('btn-close-demo-modal');
    const btnResetSession = document.getElementById('btn-reset-session');

    // Module 1: Audio Recorder
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

    // Module 2 & 3: Speech to Text & Translation
    const sttLangSelect = document.getElementById('stt-lang-select');
    const btnConvertStt = document.getElementById('btn-convert-stt');
    const btnQuickTranscribe = document.getElementById('btn-quick-transcribe');
    const transcriptTextarea = document.getElementById('transcript-textarea');
    const translatedTextarea = document.getElementById('translated-textarea');
    const btnCopyTranscript = document.getElementById('btn-copy-transcript');
    const btnCopyTranslated = document.getElementById('btn-copy-translated');
    const transcriptTargetLang = document.getElementById('transcript-target-lang');
    const btnRunTranslation = document.getElementById('btn-run-translation');
    const sttAlert = document.getElementById('stt-alert');
    const sttAlertText = document.getElementById('stt-alert-text');
    const audioFileStatus = document.getElementById('audio-file-status');
    const transcriptDetectedLang = document.getElementById('transcript-detected-lang');
    const transcriptConfidenceVal = document.getElementById('transcript-confidence-val');
    const transcriptWordCount = document.getElementById('transcript-word-count');
    const badgeOrigLang = document.getElementById('badge-orig-lang');
    const badgeTransLang = document.getElementById('badge-trans-lang');

    // Module 4: Summarization & Action Extraction
    const summaryLangSelect = document.getElementById('summary-lang-select');
    const btnGenerateSummary = document.getElementById('btn-generate-summary');
    const summaryContent = document.getElementById('summary-content');
    const summaryAlert = document.getElementById('summary-alert');
    const summaryAlertText = document.getElementById('summary-alert-text');
    const summaryLanguageTag = document.getElementById('summary-language-tag');
    const btnCopySummary = document.getElementById('btn-copy-summary');
    const actionItemsTbody = document.getElementById('action-items-tbody');
    const actionCountPill = document.getElementById('action-count-pill');
    const decisionsList = document.getElementById('decisions-list');

    // Module 5: Email Drafting Assistant
    const emailLanguageSelect = document.getElementById('email-language-select');
    const btnGenerateEmail = document.getElementById('btn-generate-email');
    const emailPriorityPill = document.getElementById('email-priority-pill');
    const emailPriorityLabel = document.getElementById('email-priority-label');
    const emailPriorityReason = document.getElementById('email-priority-reason');
    const emailSubjectInput = document.getElementById('email-subject-input');
    const emailRecipientsInput = document.getElementById('email-recipients-input');
    const emailBodyTextarea = document.getElementById('email-body-textarea');
    const btnCopyEmail = document.getElementById('btn-copy-email');
    const btnMailtoEmail = document.getElementById('btn-mailto-email');
    const emailAlert = document.getElementById('email-alert');
    const emailAlertText = document.getElementById('email-alert-text');

    // Module 6: Unicode PDF Report
    const reportLangSelect = document.getElementById('report-lang-select');
    const btnGeneratePdf = document.getElementById('btn-generate-pdf');
    const btnDownloadPdf = document.getElementById('btn-download-pdf');
    const reportSuccessAlert = document.getElementById('report-success-alert');
    const reportErrorAlert = document.getElementById('report-error-alert');
    const reportErrorText = document.getElementById('report-error-text');

    // =========================================================================
    // INITIALIZATION & EVENT BINDINGS
    // =========================================================================
    fetchSystemStatus();

    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Canvas visualizer setup
    let canvasCtx = null;
    if (waveformCanvas) {
        canvasCtx = waveformCanvas.getContext('2d');
        drawIdleWaveform(canvasCtx, waveformCanvas.width, waveformCanvas.height);
    }

    // Bind demo buttons
    bindDemoButtons();

    // Bind global toolbar synchronization
    if (globalSpeechLang && sttLangSelect) {
        globalSpeechLang.addEventListener('change', () => {
            sttLangSelect.value = globalSpeechLang.value;
        });
        sttLangSelect.addEventListener('change', () => {
            globalSpeechLang.value = sttLangSelect.value;
        });
    }

    if (globalTransLang && transcriptTargetLang) {
        globalTransLang.addEventListener('change', () => {
            transcriptTargetLang.value = globalTransLang.value;
        });
        transcriptTargetLang.addEventListener('change', () => {
            globalTransLang.value = transcriptTargetLang.value;
        });
    }

    if (globalSummaryLang && summaryLangSelect) {
        globalSummaryLang.addEventListener('change', () => {
            summaryLangSelect.value = globalSummaryLang.value;
            if (reportLangSelect) reportLangSelect.value = globalSummaryLang.value;
        });
    }

    // Demo Modal handlers
    if (btnOpenDemoModal && demoModal) {
        btnOpenDemoModal.addEventListener('click', () => demoModal.classList.remove('hidden'));
    }
    if (btnCloseDemoModal && demoModal) {
        btnCloseDemoModal.addEventListener('click', () => demoModal.classList.add('hidden'));
    }
    if (demoModal) {
        demoModal.addEventListener('click', (e) => {
            if (e.target === demoModal) demoModal.classList.add('hidden');
        });
    }

    // Reset Session Button
    if (btnResetSession) {
        btnResetSession.addEventListener('click', async () => {
            if (confirm("Reset current meeting session and clear all recorded artifacts?")) {
                await resetMeetingSession();
            }
        });
    }

    // =========================================================================
    // SYSTEM STATUS & METRIC UPDATER
    // =========================================================================
    async function fetchSystemStatus() {
        try {
            const response = await fetch('/api/status');
            if (!response.ok) return;

            const data = await response.json();
            updateArtifactBadges(data);
            updateWorkflowStepper(data);
            updateMetrics(data);

            // Update Header Detected Language Pill
            if (headerDetectedLang) {
                headerDetectedLang.textContent = data.has_transcript ? data.detected_language_name : 'Auto Detect';
            }

            // Module 2: Transcript updates
            if (transcriptTextarea && data.transcript) {
                transcriptTextarea.value = data.transcript;
            }
            if (translatedTextarea && data.translated_transcript) {
                translatedTextarea.value = data.translated_transcript;
            }
            if (transcriptDetectedLang) {
                transcriptDetectedLang.textContent = data.detected_language_name || 'Auto Detect';
            }
            if (transcriptConfidenceVal) {
                const confPercent = Math.round((data.transcription_confidence || 0.95) * 100);
                transcriptConfidenceVal.textContent = `${confPercent}% Confidence`;
            }
            if (transcriptWordCount) {
                transcriptWordCount.textContent = `${data.word_count || 0} words`;
            }
            if (badgeOrigLang) {
                badgeOrigLang.textContent = data.detected_language_name || 'Original Script';
            }
            if (badgeTransLang && data.translation_language_name) {
                badgeTransLang.textContent = data.translation_language_name;
            }

            // Module 3: Summary updates
            if (summaryContent && data.summary) {
                summaryContent.innerHTML = formatSummaryText(data.summary);
            }
            if (summaryLanguageTag && data.summary_language) {
                summaryLanguageTag.textContent = data.summary_language === 'same'
                    ? (data.detected_language_name || 'Meeting Language')
                    : (data.summary_language_name || data.summary_language);
            }

            // Action Items & Decisions
            renderActionItems(data.action_items || []);
            renderDecisions(data.decisions || []);

            // Module 5: Email Draft updates
            if (data.email_draft && data.email_draft.body) {
                renderEmailDraft(data.email_draft);
            }

            // Module 6: PDF download status
            const btnViewPdf = document.getElementById('btn-view-pdf');
            const btnTopDownload = document.getElementById('btn-top-download');
            const btnTopView = document.getElementById('btn-top-view');
            const btnAlertDownload = document.getElementById('btn-alert-download');

            const allDownloadBtns = [btnDownloadPdf, btnTopDownload, btnAlertDownload].filter(Boolean);
            const allViewBtns = [btnViewPdf, btnTopView].filter(Boolean);

            if (data.has_pdf) {
                allDownloadBtns.forEach(btn => {
                    btn.classList.remove('disabled');
                    btn.removeAttribute('disabled');
                    btn.setAttribute('href', '/download/Meeting_Report.pdf');
                    btn.setAttribute('download', 'Meeting_Report.pdf');
                });
                allViewBtns.forEach(btn => {
                    btn.classList.remove('disabled');
                    btn.removeAttribute('disabled');
                    btn.setAttribute('href', '/view/Meeting_Report.pdf');
                });
                if (reportSuccessAlert) reportSuccessAlert.classList.remove('hidden');
            } else {
                allDownloadBtns.forEach(btn => btn.classList.add('disabled'));
                allViewBtns.forEach(btn => btn.classList.add('disabled'));
            }

            // Audio tag status
            if (audioFileStatus) {
                audioFileStatus.className = data.has_audio ? 'status-tag tag-ready' : 'status-tag tag-wait';
                audioFileStatus.innerHTML = data.has_audio
                    ? '<i class="fa-solid fa-circle-check"></i> meetings/meeting.wav Ready'
                    : '<i class="fa-solid fa-clock"></i> Awaiting meetings/meeting.wav';
            }

            // Module Page status tags
            const mod1Status = document.getElementById('mod1-status');
            const mod2Status = document.getElementById('mod2-status');
            const mod3Status = document.getElementById('mod3-status');
            const mod4Status = document.getElementById('mod4-status');
            const mod5Status = document.getElementById('mod5-status');
            const mod6Status = document.getElementById('mod6-status');

            if (mod1Status) mod1Status.innerHTML = data.has_audio ? '<span class="text-success">Available</span>' : 'Not Recorded';
            if (mod2Status) mod2Status.innerHTML = data.has_transcript ? `<span class="text-success">${data.detected_language_name}</span>` : 'Not Transcribed';
            if (mod3Status) mod3Status.innerHTML = data.has_translation ? '<span class="text-success">Translated</span>' : 'Optional';
            if (mod4Status) mod4Status.innerHTML = data.has_summary ? '<span class="text-success">Summarized</span>' : 'Not Generated';
            if (mod5Status) mod5Status.innerHTML = data.has_email ? '<span class="text-success">Drafted</span>' : 'Not Drafted';
            if (mod6Status) mod6Status.innerHTML = data.has_pdf ? '<span class="text-success">Unicode PDF Ready</span>' : 'Not Created';

        } catch (err) {
            console.error('Error fetching system status:', err);
        }
    }

    function updateArtifactBadges(data) {
        if (badgeAudio) badgeAudio.className = data.has_audio ? 'badge badge-success' : 'badge badge-neutral';
        if (badgeTranscript) badgeTranscript.className = data.has_transcript ? 'badge badge-success' : 'badge badge-neutral';
        if (badgeSummary) badgeSummary.className = data.has_summary ? 'badge badge-success' : 'badge badge-neutral';
        if (badgeEmail) badgeEmail.className = data.has_email ? 'badge badge-success' : 'badge badge-neutral';
        if (badgePdf) badgePdf.className = data.has_pdf ? 'badge badge-success' : 'badge badge-neutral';
    }

    function updateWorkflowStepper(data) {
        const step1 = document.getElementById('step-1');
        const step2 = document.getElementById('step-2');
        const step3 = document.getElementById('step-3');
        const step4 = document.getElementById('step-4');
        const step5 = document.getElementById('step-5');
        const step6 = document.getElementById('step-6');

        if (step1) step1.classList.toggle('active', true);
        if (step2) step2.classList.toggle('active', data.has_audio || data.has_transcript);
        if (step3) step3.classList.toggle('active', data.has_translation);
        if (step4) step4.classList.toggle('active', data.has_summary);
        if (step5) step5.classList.toggle('active', data.has_email);
        if (step6) step6.classList.toggle('active', data.has_pdf);
    }

    function updateMetrics(data) {
        if (metricLanguage) {
            metricLanguage.textContent = data.has_transcript ? data.detected_language_name : 'Auto Detect';
        }
        if (metricDuration) {
            const secs = Math.round(data.duration || 0);
            const m = String(Math.floor(secs / 60)).padStart(2, '0');
            const s = String(secs % 60).padStart(2, '0');
            metricDuration.textContent = `${m}:${s}`;
        }
        if (metricWords) {
            metricWords.textContent = data.word_count || 0;
        }
        if (metricActions) {
            const actionsCount = (data.action_items && data.action_items.length) || 0;
            metricActions.textContent = actionsCount;
        }
        if (metricPriority) {
            const draft = data.email_draft || {};
            metricPriority.textContent = draft.priority || 'Normal';
        }
    }

    // =========================================================================
    // COLLEGE DEMO SCENARIO LOADER
    // =========================================================================
    function bindDemoButtons() {
        const demoButtons = document.querySelectorAll('.btn-load-scenario');
        demoButtons.forEach(btn => {
            btn.addEventListener('click', async () => {
                const scenarioId = btn.getAttribute('data-id');
                await loadDemoScenario(scenarioId);
                if (demoModal) demoModal.classList.add('hidden');
            });
        });
    }

    async function loadDemoScenario(scenarioId) {
        showSpinner('Loading Demonstration Meeting...', 'Populating multilingual transcript, executive summary, action items, email draft, and generating Unicode PDF report.');

        try {
            const response = await fetch('/api/load_demo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ scenario_id: scenarioId })
            });

            const result = await response.json();
            hideSpinner();

            if (response.ok && result.status === 'success') {
                showToast(`Loaded ${result.scenario.title}!`, 'success');
                await fetchSystemStatus();
            } else {
                showToast(result.message || 'Failed to load demo scenario', 'error');
            }
        } catch (err) {
            hideSpinner();
            showToast('Demo loading error: ' + err.message, 'error');
        }
    }

    async function resetMeetingSession() {
        showSpinner('Resetting Meeting Session...', 'Clearing audio and generated meeting artifacts.');
        try {
            const res = await fetch('/api/reset', { method: 'POST' });
            hideSpinner();
            if (res.ok) {
                showToast('Meeting session reset successfully.', 'info');
                setTimeout(() => window.location.reload(), 600);
            }
        } catch (e) {
            hideSpinner();
            showToast('Reset failed: ' + e.message, 'error');
        }
    }

    // =========================================================================
    // MODULE 1: BROWSER AUDIO RECORDING & UPLOAD
    // =========================================================================
    if (btnStartRecord) btnStartRecord.addEventListener('click', startMicrophoneRecording);
    if (btnStopRecord) btnStopRecord.addEventListener('click', stopMicrophoneRecording);
    if (uploadForm) uploadForm.addEventListener('submit', handleFileUpload);

    async function startMicrophoneRecording() {
        if (recordingSuccessAlert) recordingSuccessAlert.classList.add('hidden');
        if (recordingErrorAlert) recordingErrorAlert.classList.add('hidden');

        try {
            audioChunks = [];
            microphoneStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });

            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            const source = audioContext.createMediaStreamSource(microphoneStream);
            source.connect(analyser);

            let mimeType = 'audio/webm';
            if (window.MediaRecorder) {
                if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) mimeType = 'audio/webm;codecs=opus';
                else if (MediaRecorder.isTypeSupported('audio/mp4')) mimeType = 'audio/mp4';
            }

            mediaRecorder = new MediaRecorder(microphoneStream, { mimeType });
            mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const finalMime = mediaRecorder.mimeType || 'audio/webm';
                const audioBlob = new Blob(audioChunks, { type: finalMime });
                await saveAudioToServer(audioBlob);
            };

            mediaRecorder.start(100);

            btnStartRecord.disabled = true;
            btnStopRecord.disabled = false;
            if (recStatusPill) recStatusPill.className = 'rec-status-pill recording';
            if (recStatusLabel) recStatusLabel.textContent = 'Recording Live Speech...';

            recordingStartTime = Date.now();
            updateTimerDisplay();
            timerInterval = setInterval(updateTimerDisplay, 1000);

            if (canvasCtx && waveformCanvas) {
                visualizeLiveWaveform(canvasCtx, waveformCanvas.width, waveformCanvas.height);
            }

            showToast('Microphone recording started. Speak naturally in any language.', 'info');
        } catch (err) {
            console.error('Microphone error:', err);
            btnStartRecord.disabled = false;
            btnStopRecord.disabled = true;
            const msg = 'Microphone access error: ' + (err.message || 'Permission denied.');
            if (recordingErrorAlert && recordingErrorText) {
                recordingErrorText.textContent = msg;
                recordingErrorAlert.classList.remove('hidden');
            }
            showToast(msg, 'error');
        }
    }

    function stopMicrophoneRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
        if (microphoneStream) {
            microphoneStream.getTracks().forEach(track => track.stop());
        }
        clearInterval(timerInterval);
        if (animationFrameId) cancelAnimationFrame(animationFrameId);

        if (canvasCtx && waveformCanvas) {
            drawIdleWaveform(canvasCtx, waveformCanvas.width, waveformCanvas.height);
        }

        btnStartRecord.disabled = false;
        btnStopRecord.disabled = true;
        if (recStatusPill) recStatusPill.className = 'rec-status-pill';
        if (recStatusLabel) recStatusLabel.textContent = 'Processing Audio...';
    }

    async function saveAudioToServer(blob) {
        showSpinner('Saving Audio Recording...', 'Uploading microphone audio to meetings/meeting.wav');
        try {
            const formData = new FormData();
            formData.append('audio_file', blob, 'meeting.wav');

            const res = await fetch('/api/save_audio', { method: 'POST', body: formData });
            const result = await res.json();
            hideSpinner();

            if (res.ok && result.status === 'success') {
                if (recordingSuccessAlert) recordingSuccessAlert.classList.remove('hidden');
                showToast('Audio recording saved successfully!', 'success');
                fetchSystemStatus();
            } else {
                showToast(result.message || 'Failed to save audio recording', 'error');
            }
        } catch (err) {
            hideSpinner();
            showToast('Error saving audio: ' + err.message, 'error');
        }
    }

    async function handleFileUpload(e) {
        e.preventDefault();
        if (!audioFileInput || !audioFileInput.files[0]) {
            showToast('Please select an audio file first.', 'error');
            return;
        }

        const file = audioFileInput.files[0];
        showSpinner('Uploading Audio File...', 'Saving uploaded audio to meetings/meeting.wav');

        try {
            const formData = new FormData();
            formData.append('audio_file', file, file.name);

            const res = await fetch('/api/save_audio', { method: 'POST', body: formData });
            const result = await res.json();
            hideSpinner();

            if (res.ok && result.status === 'success') {
                if (recordingSuccessAlert) recordingSuccessAlert.classList.remove('hidden');
                showToast('Audio uploaded and saved as meetings/meeting.wav', 'success');
                fetchSystemStatus();
            } else {
                showToast(result.message || 'Upload failed', 'error');
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
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
                x += sliceWidth;
            }

            ctx.lineTo(width, height / 2);
            ctx.stroke();
        }
        draw();
    }

    // =========================================================================
    // MODULE 2: MULTILINGUAL SPEECH TO TEXT
    // =========================================================================
    if (btnConvertStt) btnConvertStt.addEventListener('click', runSpeechToText);
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
                showToast('Original transcript copied to clipboard!', 'success');
            }
        });
    }

    async function runSpeechToText() {
        const langCode = (sttLangSelect && sttLangSelect.value) || (globalSpeechLang && globalSpeechLang.value) || 'auto';
        showSpinner('Detecting Language & Transcribing...', `Running Groq Whisper speech recognition (Language: ${langCode})...`);

        if (sttAlert && sttAlertText) {
            sttAlert.className = 'alert alert-info';
            sttAlertText.textContent = `Connecting to Groq Whisper in ${langCode} mode...`;
            sttAlert.classList.remove('hidden');
        }

        try {
            const res = await fetch('/api/transcribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: langCode })
            });
            const result = await res.json();

            if (!res.ok || result.status === 'error') {
                hideSpinner();
                const errMessage = result.message || 'Speech to text conversion failed.';
                if (sttAlert && sttAlertText) {
                    sttAlert.className = 'alert alert-danger';
                    sttAlertText.textContent = errMessage;
                    sttAlert.classList.remove('hidden');
                }
                showToast(errMessage, 'error');
                return;
            }

            // Direct fast-path: transcript returned immediately
            if (result.transcript) {
                hideSpinner();
                if (transcriptTextarea) transcriptTextarea.value = result.transcript;
                if (transcriptDetectedLang) transcriptDetectedLang.textContent = result.detected_language_name || 'Detected';
                if (headerDetectedLang) headerDetectedLang.textContent = result.detected_language_name || 'Detected';
                if (badgeOrigLang) badgeOrigLang.textContent = result.detected_language_name || 'Original Script';
                if (transcriptConfidenceVal) {
                    const confPercent = Math.round((result.transcription_confidence || 0.95) * 100);
                    transcriptConfidenceVal.textContent = `${confPercent}% Confidence`;
                }
                if (transcriptWordCount) {
                    transcriptWordCount.textContent = `${result.word_count || 0} words`;
                }

                if (sttAlert && sttAlertText) {
                    sttAlert.className = 'alert alert-success';
                    sttAlertText.textContent = `Speech recognized successfully as ${result.detected_language_name || 'Meeting Language'}! Preserved in meetings/transcript.txt`;
                    sttAlert.classList.remove('hidden');
                }
                showToast(`Spoken language detected: ${result.detected_language_name}!`, 'success');
                fetchSystemStatus();
                return;
            }

            startSttPolling();
        } catch (err) {
            hideSpinner();
            showToast('Transcription API error: ' + err.message, 'error');
        }
    }

    function startSttPolling() {
        if (sttPollInterval) clearInterval(sttPollInterval);
        let pollCount = 0;

        sttPollInterval = setInterval(async () => {
            pollCount++;
            if (pollCount > 10) {
                clearInterval(sttPollInterval);
                sttPollInterval = null;
                hideSpinner();
                fetchSystemStatus();
                return;
            }

            try {
                const res = await fetch('/api/status');
                if (!res.ok) return;

                const data = await res.json();
                updateArtifactBadges(data);
                updateWorkflowStepper(data);
                updateMetrics(data);

                if (data.transcription_status === 'completed' || data.has_transcript) {
                    clearInterval(sttPollInterval);
                    sttPollInterval = null;
                    hideSpinner();

                    if (transcriptTextarea && data.transcript) transcriptTextarea.value = data.transcript;
                    if (transcriptDetectedLang) transcriptDetectedLang.textContent = data.detected_language_name;
                    if (headerDetectedLang) headerDetectedLang.textContent = data.detected_language_name;

                    if (sttAlert && sttAlertText) {
                        sttAlert.className = 'alert alert-success';
                        sttAlertText.textContent = `Speech recognized successfully as ${data.detected_language_name}! Preserved in meetings/transcript.txt`;
                        sttAlert.classList.remove('hidden');
                    }
                    showToast(`Spoken language detected: ${data.detected_language_name}!`, 'success');
                    fetchSystemStatus();

                } else if (data.transcription_status === 'error') {
                    clearInterval(sttPollInterval);
                    sttPollInterval = null;
                    hideSpinner();

                    const errorMsg = data.transcription_error || 'Transcription failed.';
                    if (sttAlert && sttAlertText) {
                        sttAlert.className = 'alert alert-danger';
                        sttAlertText.textContent = errorMsg;
                        sttAlert.classList.remove('hidden');
                    }
                    showToast(errorMsg, 'error');
                }
            } catch (err) {
                console.error('STT polling error:', err);
            }
        }, 1500);
    }

    // =========================================================================
    // MODULE 3: CONTEXT-AWARE AI TRANSLATION
    // =========================================================================
    if (btnRunTranslation) {
        btnRunTranslation.addEventListener('click', runTranslation);
    }

    if (btnCopyTranslated) {
        btnCopyTranslated.addEventListener('click', () => {
            if (translatedTextarea && translatedTextarea.value) {
                navigator.clipboard.writeText(translatedTextarea.value);
                showToast('Translated transcript copied to clipboard!', 'success');
            }
        });
    }

    async function runTranslation() {
        const targetLang = (transcriptTargetLang && transcriptTargetLang.value) || 'en';
        showSpinner('Translating Meeting Transcript...', `Translating full meeting conversation to ${targetLang} using contextual AI...`);

        try {
            const res = await fetch('/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_language: targetLang })
            });
            const result = await res.json();
            hideSpinner();

            if (res.ok && result.status === 'success') {
                if (translatedTextarea) translatedTextarea.value = result.translated_transcript;
                if (badgeTransLang) badgeTransLang.textContent = result.target_language_name;
                showToast(`Transcript translated to ${result.target_language_name}!`, 'success');
                fetchSystemStatus();
            } else {
                showToast(result.message || 'Translation failed.', 'error');
            }
        } catch (err) {
            hideSpinner();
            showToast('Translation error: ' + err.message, 'error');
        }
    }

    // =========================================================================
    // MODULE 4: MULTILINGUAL SUMMARIZATION & ACTION ITEMS
    // =========================================================================
    if (btnGenerateSummary) {
        btnGenerateSummary.addEventListener('click', runSummarization);
    }

    if (btnCopySummary) {
        btnCopySummary.addEventListener('click', () => {
            const sumText = document.getElementById('summary-content')?.innerText || '';
            if (sumText) {
                navigator.clipboard.writeText(sumText);
                showToast('Meeting summary copied to clipboard!', 'success');
            }
        });
    }

    async function runSummarization() {
        const sumLang = (summaryLangSelect && summaryLangSelect.value) || 'same';
        showSpinner('Generating Multilingual Summary & Action Items...', 'Distilling discussions into 7 structured executive sections and extracting tasks...');

        try {
            const res = await fetch('/api/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ summary_language: sumLang })
            });
            const result = await res.json();
            hideSpinner();

            if (res.ok && result.status === 'success') {
                if (summaryContent) summaryContent.innerHTML = formatSummaryText(result.summary);
                if (summaryLanguageTag) summaryLanguageTag.textContent = result.language_name;
                if (summaryAlert && summaryAlertText) {
                    summaryAlert.className = 'alert alert-success';
                    summaryAlertText.textContent = `Meeting summary generated successfully in ${result.language_name}!`;
                    summaryAlert.classList.remove('hidden');
                }

                renderActionItems(result.action_items || []);
                renderDecisions(result.decisions || []);

                showToast(`Executive summary generated in ${result.language_name}!`, 'success');
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
            showToast('Error generating summary: ' + err.message, 'error');
        }
    }

    function formatSummaryText(text) {
        if (!text) return '<p class="placeholder-text">No summary content available.</p>';
        const paragraphs = text.split('\n\n');
        return paragraphs.map(p => {
            p = p.trim();
            if (!p) return '';
            if (/^\d+\./.test(p)) {
                return `<h4 style="margin-top: 14px; margin-bottom: 6px; color: var(--primary);">${p}</h4>`;
            }
            return `<p>• ${p.replace(/\n/g, '<br>')}</p>`;
        }).join('');
    }

    function renderActionItems(items) {
        if (!actionItemsTbody) return;
        if (!items || items.length === 0) {
            actionItemsTbody.innerHTML = `
                <tr>
                    <td colspan="6" class="table-placeholder">
                        No action items extracted yet. Generate summary to identify deliverables.
                    </td>
                </tr>
            `;
            if (actionCountPill) actionCountPill.textContent = '0 items';
            return;
        }

        if (actionCountPill) actionCountPill.textContent = `${items.length} items`;

        actionItemsTbody.innerHTML = items.map((item, idx) => {
            const prio = (item.priority || 'Medium').toLowerCase();
            const prioClass = (prio === 'high' || prio === 'urgent') ? 'prio-high' : (prio === 'medium' ? 'prio-medium' : 'prio-low');

            return `
                <tr>
                    <td><strong>${idx + 1}</strong></td>
                    <td><strong>${item.task || 'Task'}</strong></td>
                    <td><i class="fa-solid fa-user" style="color: var(--secondary); margin-right: 4px;"></i> ${item.assigned_to || 'Unassigned'}</td>
                    <td><i class="fa-solid fa-calendar-day" style="color: var(--secondary); margin-right: 4px;"></i> ${item.deadline || 'TBD'}</td>
                    <td><span class="prio-pill ${prioClass}">${item.priority || 'Medium'}</span></td>
                    <td><span class="status-pill-sub">${item.status || 'Pending'}</span></td>
                </tr>
            `;
        }).join('');
    }

    function renderDecisions(decisions) {
        if (!decisionsList) return;
        if (!decisions || decisions.length === 0) {
            decisionsList.innerHTML = '<li class="placeholder-li">No decisions extracted yet.</li>';
            return;
        }
        decisionsList.innerHTML = decisions.map(d => `<li><strong>${d}</strong></li>`).join('');
    }

    // =========================================================================
    // MODULE 5: EMAIL DRAFTING & PRIORITIZATION ASSISTANT
    // =========================================================================
    if (btnGenerateEmail) {
        btnGenerateEmail.addEventListener('click', runGenerateEmail);
    }

    if (btnCopyEmail) {
        btnCopyEmail.addEventListener('click', () => {
            const subj = emailSubjectInput ? emailSubjectInput.value : '';
            const to = emailRecipientsInput ? emailRecipientsInput.value : '';
            const body = emailBodyTextarea ? emailBodyTextarea.value : '';

            const fullEmail = `Subject: ${subj}\nTo: ${to}\n\n${body}`;
            navigator.clipboard.writeText(fullEmail);
            showToast('Follow-up email copied to clipboard!', 'success');
        });
    }

    async function runGenerateEmail() {
        const emailLang = (emailLanguageSelect && emailLanguageSelect.value) || 'en';
        showSpinner('Drafting Follow-Up Email...', `Assessing meeting urgency and crafting follow-up in ${emailLang}...`);

        try {
            const res = await fetch('/api/generate_email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email_language: emailLang })
            });
            const result = await res.json();
            hideSpinner();

            if (res.ok && result.status === 'success') {
                renderEmailDraft(result.email_draft);
                if (emailAlert && emailAlertText) {
                    emailAlert.className = 'alert alert-success';
                    emailAlertText.textContent = 'Follow-up email drafted with priority assessment!';
                    emailAlert.classList.remove('hidden');
                }
                showToast(`Email drafted (Priority: ${result.email_draft.priority})!`, 'success');
                fetchSystemStatus();
            } else {
                showToast(result.message || 'Email drafting failed.', 'error');
            }
        } catch (err) {
            hideSpinner();
            showToast('Email drafting error: ' + err.message, 'error');
        }
    }

    function renderEmailDraft(draft) {
        if (!draft) return;

        if (emailSubjectInput) emailSubjectInput.value = draft.subject || '';
        if (emailRecipientsInput) emailRecipientsInput.value = draft.recipients || '';
        if (emailBodyTextarea) emailBodyTextarea.value = draft.body || '';

        // Update Priority pill
        const prio = (draft.priority || 'Medium').toLowerCase();
        if (emailPriorityPill) {
            emailPriorityPill.className = `priority-pill prio-${prio}`;
        }
        if (emailPriorityLabel) {
            emailPriorityLabel.textContent = `Priority: ${draft.priority || 'Medium'}`;
        }
        if (emailPriorityReason) {
            emailPriorityReason.textContent = draft.priority_reason || 'Standard meeting follow-up.';
        }

        // Build mailto link
        if (btnMailtoEmail) {
            const subjectEnc = encodeURIComponent(draft.subject || 'Meeting Follow-up');
            const bodyEnc = encodeURIComponent(draft.body || '');
            btnMailtoEmail.href = `mailto:?subject=${subjectEnc}&body=${bodyEnc}`;
        }
    }

    // =========================================================================
    // MODULE 6: UNICODE PDF REPORT GENERATION
    // =========================================================================
    if (btnGeneratePdf) {
        btnGeneratePdf.addEventListener('click', runReportGeneration);
    }

    async function runReportGeneration() {
        const repLang = (reportLangSelect && reportLangSelect.value) || 'en';
        showSpinner('Building Unicode PDF Report...', `Compiling intelligence with embedded Google Noto fonts (Format: ${repLang})...`);

        try {
            const res = await fetch('/api/generate_report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ report_language: repLang })
            });
            const result = await res.json();
            hideSpinner();

            if (res.ok && result.status === 'success') {
                if (reportSuccessAlert) reportSuccessAlert.classList.remove('hidden');
                if (reportErrorAlert) reportErrorAlert.classList.add('hidden');

                // Enable all download & view buttons
                const btnTopDownload = document.getElementById('btn-top-download');
                const btnTopView = document.getElementById('btn-top-view');
                const btnAlertDownload = document.getElementById('btn-alert-download');
                const btnViewPdf = document.getElementById('btn-view-pdf');

                const dlBtns = [btnDownloadPdf, btnTopDownload, btnAlertDownload].filter(Boolean);
                const viewBtns = [btnViewPdf, btnTopView].filter(Boolean);

                dlBtns.forEach(btn => {
                    btn.classList.remove('disabled');
                    btn.removeAttribute('disabled');
                    btn.setAttribute('href', '/download/Meeting_Report.pdf');
                    btn.setAttribute('download', 'Meeting_Report.pdf');
                });
                viewBtns.forEach(btn => {
                    btn.classList.remove('disabled');
                    btn.removeAttribute('disabled');
                    btn.setAttribute('href', '/view/Meeting_Report.pdf');
                });

                // Trigger automatic file download to the user's Downloads folder
                const dlLink = document.createElement('a');
                dlLink.href = '/download/Meeting_Report.pdf?t=' + Date.now();
                dlLink.setAttribute('download', 'Meeting_Report.pdf');
                document.body.appendChild(dlLink);
                dlLink.click();
                setTimeout(() => {
                    if (dlLink.parentNode) dlLink.parentNode.removeChild(dlLink);
                }, 500);

                showToast('Unicode PDF Report Downloaded Successfully!', 'success');
                fetchSystemStatus();
            } else {
                if (reportErrorAlert && reportErrorText) {
                    reportErrorText.textContent = result.message || 'PDF generation failed.';
                    reportErrorAlert.classList.remove('hidden');
                }
                showToast(result.message || 'PDF generation error', 'error');
            }
        } catch (err) {
            hideSpinner();
            showToast('PDF generator error: ' + err.message, 'error');
        }
    }

    // =========================================================================
    // UTILITIES: SPINNER & TOAST NOTIFICATIONS
    // =========================================================================
    let spinnerWatchdogTimer = null;

    function showSpinner(title, desc) {
        if (spinnerTitle) spinnerTitle.textContent = title || 'Processing...';
        if (spinnerDesc) spinnerDesc.textContent = desc || 'Connecting modules and analyzing meeting data.';
        if (loadingSpinner) loadingSpinner.classList.remove('hidden');

        // Watchdog: auto-dismiss spinner after 15 seconds if an unhandled network freeze occurs
        if (spinnerWatchdogTimer) clearTimeout(spinnerWatchdogTimer);
        spinnerWatchdogTimer = setTimeout(() => {
            if (loadingSpinner && !loadingSpinner.classList.contains('hidden')) {
                hideSpinner();
                showToast('Operation took longer than usual. Synchronizing meeting data...', 'info');
                fetchSystemStatus();
            }
        }, 15000);
    }

    function hideSpinner() {
        if (spinnerWatchdogTimer) {
            clearTimeout(spinnerWatchdogTimer);
            spinnerWatchdogTimer = null;
        }
        if (loadingSpinner) loadingSpinner.classList.add('hidden');
    }

    // Dismiss spinner on close button click, backdrop click, or Escape key
    const btnCloseSpinner = document.getElementById('btn-close-spinner');
    const btnSpinnerCancel = document.getElementById('btn-spinner-cancel');
    if (btnCloseSpinner) btnCloseSpinner.addEventListener('click', hideSpinner);
    if (btnSpinnerCancel) btnSpinnerCancel.addEventListener('click', hideSpinner);
    if (loadingSpinner) {
        loadingSpinner.addEventListener('click', (e) => {
            if (e.target === loadingSpinner) hideSpinner();
        });
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') hideSpinner();
    });

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
