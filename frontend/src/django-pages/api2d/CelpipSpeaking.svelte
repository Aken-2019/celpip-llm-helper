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
    let credit_comsumed_stt = $state(-1);
    let credit_comsumed_txt = $state(-1);
    // Transcription results
    let transcription = $state('`待转写...`');
    let improvedText = $state('`待润色...`');
    let suggestionContent = $state('`待润色...`');

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

    // Update credit information
    async function updateCredits() {
        try {
            const response = await apiClient.fetchCredits(apiKey);
            credits = response;
        } catch (error) {
            console.error('Error fetching credits:', error);
            errorMessage = '无法加载积分信息';
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
            errorMessage = '不支持的音频格式。请上传 MP3, MP4, M4A, WAV 或 WebM 文件。';
            return;
        }
        
        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            errorMessage = `文件太大。最大支持 ${formatFileSize(MAX_FILE_SIZE)}。`;
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
    async function improveText() {
        if (!transcription) return;
        
        isProcessing = true;
        
        try {
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
            console.log(response)
            // let wrapped_xml_response = "<root><revised_text>" + response.choices[0]?.message.content + "</grammar_focused_feedback></root>"
            let wrapped_xml_response = "<root><revised_text>" + response.content[0]?.text + "</grammar_focused_feedback></root>"
            let xml_response = new DOMParser().parseFromString(wrapped_xml_response, 'text/xml');
            improvedText = xml_response.getElementsByTagName('revised_text')[0]?.textContent || 'Error, please contact support';
            suggestionContent = xml_response.getElementsByTagName('grammar_focused_feedback')[0]?.textContent || 'Error, please contact support';
            suggestionContent = suggestionContent.replace(/"/g, '`');
            improvedText = improvedText.replace(/"/g, '`');
            credit_comsumed_txt = response.usage.final_total
            await updateCredits()
        } catch (error) {
            console.error('Error improving text:', error);
            errorMessage = '改进文本时出错，请重试';
            throw error;
        } finally {
            isProcessing = false;
        }
    }
    
    // Handle form submission
    async function handleSubmit(e: Event) {
        e.preventDefault();
        if (isProcessing) return;
        
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
                errorMessage = '请先上传或录制音频';
                return;
            }
            
            // Transcribe audio
            await processAudioFile(audioFile);
            
            // Improve and extend text if transcription is successful
            if (transcription) {
                await improveText();
            }
        } catch (error) {
            console.error('Error processing audio:', error);
            errorMessage = '处理音频时出错，请重试';
        } finally {
            isProcessing = false;
        }
    }

    // Process audio file through API
    async function processAudioFile(file: File) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Show loading state for transcription
        transcription = '正在转写音频...';
        try {
                // Step 1: Transcribe audio
                const transcriptionResponse = await apiClient.transcribeAudio(
                    file,
                    apiKey,
                    sttModel,
                    language
                );
                
                transcription = transcriptionResponse.text || '未能识别到文本';
                credit_comsumed_stt = transcriptionResponse.usage.final_total;
            } catch (error) {
                console.error('Transcription error:', error);
                errorMessage = '转写失败: ' + (error instanceof Error ? error.message : '未知错误');
            }
    }
    
    // Copy text to clipboard
    function copyToClipboard(text: string) {
        navigator.clipboard.writeText(text).then(() => {
            // Show a temporary tooltip or notification
            const notification = document.createElement('div');
            notification.textContent = '已复制到剪贴板';
            notification.style.position = 'fixed';
            notification.style.bottom = '20px';
            notification.style.right = '20px';
            notification.style.backgroundColor = '#28a745';
            notification.style.color = 'white';
            notification.style.padding = '10px 20px';
            notification.style.borderRadius = '5px';
            notification.style.zIndex = '1000';
            document.body.appendChild(notification);
            
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text:', err);
            errorMessage = '复制失败，请手动选择并复制文本。';
        });
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
            title="使用测试文本">
        <label class="form-check-label" for="testModeToggle">测试模式</label>
    </div>
    {/if}
    
    {#if isTestMode}
    <div class="mb-3">
        <label for="testTranscription" class="form-label">测试文本</label>
        <textarea 
            class="form-control font-monospace" 
            id="testTranscription" 
            bind:value={testTranscription}
            rows="5" 
            placeholder="在此输入测试文本..."></textarea>
        <div class="form-text">测试模式下将使用此文本进行处理</div>
    </div>
    {/if}
    
    <div class="card-header bg-light d-flex justify-content-between align-items-center">
        <h4 class="mb-0">思培口语 - AI润色</h4>
        <button 
            class="btn btn-sm btn-primary" 
            type="button" 
            data-bs-toggle="collapse" 
            data-bs-target="#helpCollapse" 
            aria-expanded="false" 
            aria-controls="helpCollapse">
            <i class="bi bi-question-circle me-1"></i>使用说明
        </button>
    </div>
    
    <div class="card-body">
        <div class="collapse mb-4" id="helpCollapse">
            <div class="alert alert-info">
                <p class="mb-2"><strong>操作步骤</strong></p>
                <ol class="mb-3">
                    <li>选择"录制音频"开始录制您的口语录音 (或者选择"上传文件"上传您的口语录音)</li>
                    <li>点击下方润色按钮</li>
                </ol>
                <p class="mb-2"><strong>您将获得：</strong></p>
                <ul class="mb-0">
                    <li>口语文件准确的文字转写</li>
                    <li>为思培口语评分标准定制的语法和用词润色</li>
                    <li>充实的口语内容扩展</li>
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
                    🎙️ 录制音频
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button 
                    class="nav-link {activeTab === 'upload' ? 'active' : ''}" 
                    onclick={() => activeTab = 'upload'}
                    type="button"
                    data-testid="upload-tab-button">
                    📁 上传文件
                </button>
            </li>
        </ul>
        
        <form onsubmit={handleSubmit}>
            <!-- Record Tab -->
            {#if activeTab === 'record'}
            <div class="mb-3">
                <div class="form-label">选择录制时长</div>
                <div class="d-flex gap-4">
                    <div class="form-check">
                        <input 
                            class="form-check-input" 
                            type="radio" 
                            id="duration60" 
                            bind:group={recordingDuration}
                            value="60">
                        <label class="form-check-label" for="duration60">
                            60 秒 （第2，3，4，5，6，8题）
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
                            90 秒 （第1，7题）
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
                <label for="audioFile" class="form-label">选择音频文件</label>
                <input 
                    class="form-control" 
                    type="file" 
                    id="audioFile" 
                    accept="audio/*"
                    onchange={handleFileChange}
                    disabled={isProcessing}>
                <div class="form-text">
                    最大文件大小：10MB。支持格式：MP3, MP4, M4A, WAV, WebM。
                </div>
            </div>
            {/if}
            

            {#if audioUrl}
            <div class="mt-3">
                <h5>音频预览</h5>
                <div class="card">
                    <div class="card-body">
                        <audio 
                            src={audioUrl} 
                            class="w-100" 
                            controls 
                            preload="metadata">
                            您的浏览器不支持音频播放。
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
                    disabled={isProcessing || (activeTab === 'upload' && !audioFile) || (credits?.total_available ?? 0) < 100}>
                    {#if isProcessing}
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    处理中...
                    {:else}
                    开始润色与扩写
                    {/if}
                </button>
                
                <!-- Credit Info -->
                <div class="mt-2 small">
                    {#if credits}
                        {#if (credits.total_available ?? 0) < 100}
                        <span class="text-danger">
                            当前剩余积分: {credits.total_available}, 为避免因点数不足导致功能异常，请先充值积分至100点以上。
                        </span>
                        {:else}
                        <span class="text-success">
                            当前剩余积分: {credits.total_available}
                        </span>
                        {/if}
                    {:else}
                    <span>正在加载积分信息...</span>
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
                    title='1. 转文字' 
                    content={transcription}
                /> 
            </div>
            <div class='my-4' data-testid="improved-text">
                <MarkdownArea 
                    title='2. 润色结果' 
                    content={improvedText}
                />
            </div>
            <div class='my-4' data-testid="suggestion-text">
                <MarkdownArea 
                    title='3. 具体建议' 
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
