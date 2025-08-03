<script lang="ts">
    import { onMount } from 'svelte';
    import MarkdownArea from '@/components/MarkdownArea.svelte';
    import Recorder from '@/components/Recorder.svelte';
    import { ApiClient } from '../../utils/apiClient';
    
    // Define the shape of the recording complete event detail
    type RecordingCompleteEventDetail = {
        blob: Blob;
        fileName: string;
        metadata: {
            mimeType?: string;
            duration?: number;
            timestamp?: string;
            [key: string]: any;
        };
    } | null;

    // Component props using Svelte 5 runes
    const {
        endpoint = '',
        apiKey = '',
        sttModel = '',
        txtModel = '',
        language = 'en',
        celpipImproveSysPrompt = '',
        isTestMode = false
    } = $props();

    // State variables
    let testTranscription = $state('Harry is a nice boy and he likes his cat.');
    let activeTab = $state('record');
    let recordingDuration = $state('60');
    let audioFile = $state<File | null>(null);
    let audioUrl = $state<string | null>(null);
    let isProcessing = $state(false);
    let errorMessage = $state('');
    let credits = $state<{total_available: number} | null>(null);
    let credit_consumed = $state(0);
    let last_credits = $state<number | null>(null);
    // Transcription results
    let transcription = $state('`Waiting input...`');
    let improvedText = $state('`Waiting input...`');
    let suggestionContent = $state('`Waiting input...`');

    // Initialize API client
    const apiClient = new ApiClient({
        baseUrl: endpoint,
        useCsrf: false
    });


    // Load credits on mount
    onMount(() => {
        updateCredits();
        return () => {
            // Cleanup function
            if (audioUrl) {
                URL.revokeObjectURL(audioUrl);
            }
        };
    });

    // Update credit information and track consumption
    async function updateCredits(): Promise<boolean> {
        try {
            const response = await apiClient.fetchCredits(apiKey);
            
            // Calculate credit consumption if we have a previous value
            if (last_credits !== null) {
                const currentCredits = response.total_available;
                credit_consumed = last_credits - currentCredits;
            }
            
            // Update last_credits for next calculation
            last_credits = response.total_available;
            credits = response;
            
            return true;
        } catch (error) {
            console.error('Failed to load credit information:', error);
            throw error;
        }
    }

    // Handle file selection
    function handleFileChange(event: Event) {
        const input = event.target as HTMLInputElement;
        if (!input.files || input.files.length === 0) return;
        
        const file = input.files[0];
        const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
        
        // Validate file type
        const supportedTypes = [
            'audio/mp3', 'audio/mp4', 'audio/mpeg', 'audio/x-m4a', 'audio/m4a', 
            'audio/wav', 'audio/wave', 'audio/x-wav', 'audio/webm', 'audio/x-m4a'
        ];
        const fileExt = file.name.split('.').pop()?.toLowerCase();
        
        // Check both MIME type and file extension for better compatibility
        if (!supportedTypes.includes(file.type) && fileExt !== 'm4a') {
            errorMessage = 'Unsupported audio format. Please upload MP3, MP4, M4A, WAV, or WebM files.';
            return;
        }
        
        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            errorMessage = `File too large. Maximum size supported is ${formatFileSize(MAX_FILE_SIZE)}.`;
            return;
        }
        
        // Set the file and create object URL
        audioFile = file;
        audioUrl = URL.createObjectURL(file);
        errorMessage = '';
    }

    // Format file size
    function formatFileSize(bytes: number): string {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Improve transcribed text
    async function improveText(): Promise<boolean> {
        improvedText = 'Improving text...';
        suggestionContent = 'Generating suggestions...';
        const response = await apiClient.chatCompletion(
            apiKey,
            txtModel,
            [
                { role: 'system', content: celpipImproveSysPrompt },
                { role: 'user', content: transcription },
                {
                    role: 'assistant',
                    content: "<revised_text>"
                }
            ],
            {
                stop_sequences: ['</grammar_focused_feedback>'],
                max_tokens: 4096
            },
            '/claude/v1/messages'
        );
        
        const wrapped_xml_response = "<root><revised_text>" + response.content[0]?.text + "</grammar_focused_feedback></root>";
        const xml_response = new DOMParser().parseFromString(wrapped_xml_response, 'text/xml');
        
        improvedText = xml_response.getElementsByTagName('revised_text')[0]?.textContent || 'Error, please contact support';
        suggestionContent = xml_response.getElementsByTagName('grammar_focused_feedback')[0]?.textContent || 'Error, please contact support';
        suggestionContent = suggestionContent.replace(/"/g, '`');
        improvedText = improvedText.replace(/"/g, '`');
        return true;
    }
    
    // Process audio file through API
    async function processAudioFile(file: File): Promise<void> {
        transcription = 'Transcribing audio...';
        
        const transcriptionResponse = await apiClient.transcribeAudio(
            file,
            apiKey,
            sttModel,
            language
        );
        
        transcription = transcriptionResponse.text || 'No text recognized';
    }
    
    // Handle form submission
    async function handleSubmit(e: Event) {
        e.preventDefault();
        if (isProcessing) return;
        
        isProcessing = true;
        errorMessage = '';
        
        try {
            // Handle test mode
            if (isTestMode) {
                transcription = testTranscription;
                await improveText();
                return;
            }
            
            // Handle file upload
            if (!audioFile) {
                errorMessage = 'Please upload or record an audio file first';
                return;
            }
            
            // Process audio and improve text
            await processAudioFile(audioFile);
            await improveText();
            
        } catch (error) {
            const message = error instanceof Error ? error.message : '未知错误';
            console.error('处理请求时出错:', error);
            errorMessage = `处理请求时出错: ${message}`;
        } finally {
            isProcessing = false;
            await updateCredits();
        }
    }

    function handleRecordingComplete({ detail }: { detail: RecordingCompleteEventDetail }) {
        console.log(detail)
        if (!detail) {
            console.error('No recording details found in event');
            return;
        }

        const { 
            blob: audioBlob, 
            fileName = 'recording.m4a',
            metadata = {}
        } = detail;
        
        console.log('Processing recording:', { fileName, metadata });
        
        try {
            // Create a file object from the blob
            const file = new File([audioBlob], fileName, { 
                type: metadata.mimeType || 'audio/mp4',
                lastModified: metadata.timestamp ? new Date(metadata.timestamp).getTime() : Date.now(),
            });
            
            // Update the component state
            audioFile = file;
            audioUrl = URL.createObjectURL(file);
            
            console.log('Audio URL created:', audioUrl);

        } catch (error) {
            console.error('Error processing recording:', error);
            errorMessage = 'Failed to process the recording. Please try again.';
        }
    }
</script>

<div class="card shadow" style="max-width: 800px; margin: 0 auto;">
    <!-- Test Mode Toggle (Admin Only) -->
    {#if isTestMode}
    <div class="mb-3 form-check form-switch">
        <input 
            class="form-check-input" 
            type="checkbox" 
            id="testModeToggle" 
            data-bs-toggle="tooltip" 
            data-bs-placement="top" 
            title="Use test text">
        <label class="form-check-label" for="testModeToggle">Test Mode</label>
    </div>
    {/if}
    
    {#if isTestMode}
    <div class="mb-3">
        <label for="testTranscription" class="form-label">Test Text</label>
        <textarea 
            class="form-control font-monospace" 
            id="testTranscription" 
            bind:value={testTranscription}
            rows="5" 
            placeholder="Enter test text here..."></textarea>
        <div class="form-text">Test mode will use this text for processing</div>
    </div>
    {/if}
    
    <div class="card-header bg-light d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Celpip Speaking - AI Polish</h4>
        <button 
            class="btn btn-sm btn-primary" 
            type="button" 
            data-bs-toggle="collapse" 
            data-bs-target="#helpCollapse" 
            aria-expanded="false" 
            aria-controls="helpCollapse">
            <i class="bi bi-question-circle me-1"></i>Instructions
        </button>
    </div>
    
    <div class="card-body">
        <div class="collapse mb-4" id="helpCollapse">
            <div class="alert alert-info">
                <p class="mb-2"><strong>Instructions</strong></p>
                <ol class="mb-3">
                    <li>Choose "Record Audio" to start recording your speaking audio (or choose "Upload File" to upload your speaking audio)</li>
                    <li>Click the polish button below</li>
                </ol>
                <p class="mb-2"><strong>You will receive:</strong></p>
                <ul class="mb-0">
                    <li>Accurate text transcription of your speaking audio</li>
                    <li>Grammar and vocabulary polish tailored to Celpip speaking evaluation criteria</li>
                    <li>Expanded speaking content enrichment</li>
                </ul>
            </div>
        </div>
        
        <!-- Tabs for recording/uploading -->
        <ul class="nav nav-pills mb-4" id="audioSourceTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button 
                    class="nav-link {activeTab === 'record' ? 'active' : ''}" 
                    onclick={() => activeTab = 'record'}
                    type="button">
                    🎙️ Record Audio
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button 
                    class="nav-link {activeTab === 'upload' ? 'active' : ''}" 
                    onclick={() => activeTab = 'upload'}
                    type="button"
                    data-testid="upload-tab-button">
                    📁 Upload File
                </button>
            </li>
        </ul>
        
        <form onsubmit={handleSubmit}>
            <!-- Record Tab -->
            {#if activeTab === 'record'}
            <div class="mb-3">
                <div class="form-label">Select recording duration</div>
                <div class="d-flex gap-4">
                    <div class="form-check">
                        <input 
                            class="form-check-input" 
                            type="radio" 
                            id="duration60" 
                            bind:group={recordingDuration}
                            value="60">
                        <label class="form-check-label" for="duration60">
                            60 seconds (Questions 2, 3, 4, 5, 6, 8)
                        </label>
                    </div>
                    <div class="form-check">
                        <input 
                            class="form-check-input" 
                            type="radio" 
                            id="duration90" 
                            bind:group={recordingDuration}
                            value="90">
                        <label class="form-check-label" for="duration90">
                            90 seconds (Questions 1, 7)
                        </label>
                    </div>
                </div>
                
                <div class="mt-3">
                    <Recorder
                        length={Number(recordingDuration)}
                        showPlayButton={true}
                        fileName="recording.m4a"
                        onRecordingComplete={handleRecordingComplete}
                    />
                </div>
            </div>
            
            <!-- Upload Tab -->
            {:else}
            <div class="mb-3">
                <label for="audioFile" class="form-label">Choose audio file</label>
                <input 
                    class="form-control" 
                    type="file" 
                    id="audioFile" 
                    accept="audio/*"
                    onchange={handleFileChange}
                    disabled={isProcessing}>
                <div class="form-text">
                    Maximum file size: 10MB. Supported formats: MP3, MP4, M4A, WAV, WebM.
                </div>
            </div>
            {/if}
            

            {#if audioUrl}
            <div class="mt-3">
                <h5>Audio Preview</h5>
                <div class="card">
                    <div class="card-body">
                        <audio 
                            src={audioUrl} 
                            class="w-100" 
                            controls 
                            preload="metadata">
                            Your browser does not support audio playback.
                        </audio>
                    </div>
                </div>
            </div>
            {/if}

            <!-- Submit Button -->
            <div class="text-center mt-3">
                <button 
                    type="submit" 
                    class="btn btn-primary"
                    data-testid="submit-button"
                    disabled={isProcessing || (activeTab === 'upload' && !audioFile) || (credits?.total_available ?? 0) < 150}>
                    {#if isProcessing}
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Processing...
                    {:else}
                    Start Polish and Enrich
                    {/if}
                </button>
                
                <!-- Credit Info -->
                <div class="mt-2 small">
                    {#if credits}
                        <span class="text-success">
                            Current credits: {credits.total_available}
                        </span>
                            {#if credit_consumed > 0}
                            <span class="text-success">
                                Credits consumed this time: {credit_consumed}
                            </span>
                            {/if}
                            {#if (credits.total_available ?? 0) < 150}
                            <span class="text-danger">
                                Please recharge your credits to at least 150 to avoid functionality issues.
                            </span>
                            {/if}
                    {:else}
                    <span>Loading credit information...</span>
                    {/if}
                </div>
            </div>
        </form>
        
        <!-- Error Message -->
        {#if errorMessage}
        <div class="alert alert-danger mt-3 mb-0">
            {errorMessage}
        </div>
        {/if}
        
            <div class='my-4' data-testid="transcription-text">
                <MarkdownArea 
                    title='1. Transcription' 
                    content={transcription}
                /> 
            </div>
            <div class='my-4' data-testid="improved-text">
                <MarkdownArea 
                    title='2. Improved Text' 
                    content={improvedText}
                />
            </div>
            <div class='my-4' data-testid="suggestion-text">
                <MarkdownArea 
                    title='3. Detailed Suggestions' 
                    content={`
<style>
table {
border-collapse: collapse;
width: 100%;
}

th, td {
text-align: left;
padding: 8px;
}

tr:nth-child(even){background-color: #f2f2f2}

th {
background-color: #04AA6D;
color: white;
}
</style>
${suggestionContent}`} 
                />
            </div>
        </div>
    </div>
