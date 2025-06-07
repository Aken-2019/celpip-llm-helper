/**
 * Handles MP3 file processing entirely in the browser
 * 
 * Features:
 * - Audio file processing
 * - File size validation
 * - Progress tracking
 * - Error handling
 */

document.addEventListener('DOMContentLoaded', async function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Check if test mode toggle exists (admin only)
    const testModeToggle = document.getElementById('testModeToggle');
    const testModeContent = document.getElementById('testModeContent');
    const testTranscriptionTextarea = document.getElementById('testTranscription');
    
    let isTestMode = false;

    if (testModeToggle && testModeContent) {
        // Toggle test mode content visibility
        const toggleTestMode = () => {
            isTestMode = testModeToggle.checked;
            testModeContent.style.display = isTestMode ? 'block' : 'none';
            console.log('Test mode:', isTestMode ? 'enabled' : 'disabled');
        };
        
        // Initialize and set up event listener
        testModeToggle.addEventListener('change', toggleTestMode);
        toggleTestMode(); // Initialize the state
    }

    // Initialize the API client using configuration from template
    const apiClient = new ApiClient({
        baseUrl: window.api2dConfig.endpoint,
        useCsrf: false,
    });

    // Store the API key from configuration
    const apiKey = window.api2dConfig.apiKey;
    const sttModel   = window.api2dConfig.sttModel;
    const language = window.api2dConfig.language;
    const txtModel = window.api2dConfig.txtModel;
    const celpip_improve_sys_prompt = window.api2dConfig.celpip_improve_sys_prompt;
    const celpip_extend_sys_prompt = window.api2dConfig.celpip_extend_sys_prompt;

    // Get elements
    const form = document.getElementById('audioUploadForm');
    const resultDiv = document.getElementById('uploadResult');
    const errorMessage = document.getElementById('errorMessage');

    // Helper functions
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.parentElement.style.display = 'block';
    }

    function hideError() {
        errorMessage.parentElement.style.display = 'none';
    }
    const fileInput = document.querySelector('input[type="file"]');
    
    // Maximum file size in bytes (10MB)
    const MAX_FILE_SIZE = 10 * 1024 * 1024;

    // Format bytes to human readable format
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Process the selected file
    function processFile(file) {
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        
        // Hide any previous messages
        resultDiv.style.display = 'none';
        // For now, just simulate processing
        setTimeout(() => {
            // Show success message with file info
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileSize').textContent = formatFileSize(file.size);
            resultDiv.style.display = 'block';
            
            // Reset form and button
            form.reset();
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
            
            console.log('File processed successfully:', {
                name: file.name,
                size: file.size,
                type: file.type,
                lastModified: new Date(file.lastModified).toLocaleString()
            });
        }, 1000); // Simulate processing time
    }
    
    // Handle file selection
    fileInput.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Show audio player if file is selected
        document.getElementById('audioPlayer').style.display = 'block';
        const audioPlayer = document.getElementById('audioPlayerElement');
        
        // Create object URL for the file
        const objectUrl = URL.createObjectURL(file);
        audioPlayer.src = objectUrl;
        
        // Clean up the object URL when no longer needed
        audioPlayer.addEventListener('ended', () => {
            URL.revokeObjectURL(objectUrl);
        });
        audioPlayer.addEventListener('error', () => {
            URL.revokeObjectURL(objectUrl);
        });
        audioPlayer.addEventListener('pause', () => {
            URL.revokeObjectURL(objectUrl);
        });
        audioPlayer.addEventListener('loadstart', () => {
            URL.revokeObjectURL(objectUrl);
        });

        // Show file info
        // document.getElementById('fileInfo').style.display = 'block';
        // document.getElementById('transcriptionSection').style.display = 'block';
        // document.getElementById('fileDetails').textContent = `
        //     File name: ${file.name}
        //     Size: ${(file.size / 1024 / 1024).toFixed(2)} MB
        //     Type: ${file.type}
        // `;
        
        // Check file type
        const supportedExtensions = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'];
        const fileExtension = file.name.toLowerCase().split('.').pop();
        if (!supportedExtensions.includes('.' + fileExtension)) {
            showError('Only audio files are allowed (MP3, MP4, M4A, WAV, WebM, etc.).');
            fileInput.value = '';
            return;
        }
        
        // Check file size
        if (file.size > MAX_FILE_SIZE) {
            showError(`File too large. Maximum size is ${formatFileSize(MAX_FILE_SIZE)}.`);
            fileInput.value = '';
            return;
        }
        
        // Clear any previous errors
        hideError();
        
        // Process the file
        // processFile(file);
    });
    
    // Prevent form submission (we're handling it with JavaScript)
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById('audioFile');
        const file = fileInput.files[0];

        if (!file) {
            showError('Please select an audio file.');
            return;
        }

        try {
            // Show loading state
            document.getElementById('uploadError').style.display = 'none';
            document.getElementById('transcriptionSection').style.display = 'block';



            // Show all sections
            document.getElementById('transcriptionSection').style.display = 'block';
            
            // Initialize status messages and show spinners
            document.getElementById('transcriptionStatus').textContent = 'Transcribing audio...';
            document.getElementById('transcriptionSpinner').style.display = 'inline-block';
            
            // Initialize word count section
            document.getElementById('wordCountStatus').textContent = 'Waiting for transcription...';
            document.getElementById('wordCountSpinner').style.display = 'none';
            
            // Initialize detailed analysis section
            document.getElementById('elaborateTextStatus').textContent = 'Waiting for transcription...';
            document.getElementById('elaborateTextSpinner').style.display = 'none';

            let transcription;
            const initCreditsResponse = await apiClient.fetchCredits(apiKey);
            const initUserCredit = initCreditsResponse.total_available
            if (isTestMode && testTranscriptionTextarea) {
                // Use text from the test transcription textarea
                transcription = {
                    text: testTranscriptionTextarea.value.trim() || 'No test text provided.'
                };
                document.getElementById('transcriptionStatus').textContent = 'Using test transcription';
            } else {
                // Call the actual API
                document.getElementById('transcriptionStatus').textContent = 'Transcribing audio...';
                try {
                    transcription = await apiClient.transcribeAudio(file, apiKey, sttModel, language);
                    const afterTranscriptionResponse = await apiClient.fetchCredits(apiKey);
                    const afterTranscriptionUserCredit = afterTranscriptionResponse.total_available;
                    let nUserCredit = initUserCredit - afterTranscriptionUserCredit;
                    document.getElementById('transcriptionStatus').textContent = `Transcription takes ${nUserCredit} credits!`;
                } catch (error) {
                    document.getElementById('transcriptionStatus').textContent = 'Error in transcription';
                    throw error;
                }
            }
            // Update transcription result
            document.getElementById('transcriptionSpinner').style.display = 'none';
            document.getElementById('transcriptionText').textContent = transcription.text;
            
            await improveTranscription(transcription.text)
            await elaborateTextAnalysis(transcription.text)

        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'An error occurred during processing');
        }
    });

    async function improveTranscription(text) {
        // Show spinner and update status
        document.getElementById('wordCountStatus').textContent = 'Improving text...';
        document.getElementById('wordCountSpinner').style.display = 'inline-block';
        document.getElementById('wordCountResult').style.display = 'block';
        
        try {
            // Get initial credits before improvement
            const creditsResponse = await apiClient.fetchCredits(apiKey);
            const initUserCredit = creditsResponse.total_available;
            
            const response = await apiClient.chatCompletion(
                apiKey,
                txtModel,
                [
                    {
                        role: 'system',
                        content: celpip_improve_sys_prompt
                    },
                    {
                        role: 'user',
                        content: "Below is my transcript, please revise:\n\n" + text
                    }
                ],
                {
                    temperature: 0.5,
                    max_tokens: 500
                }
            );
            
            const afterImproveResponse = await apiClient.fetchCredits(apiKey);
            const afterImproveUserCredit = afterImproveResponse.total_available;
            const nUserCredit = initUserCredit - afterImproveUserCredit;
            
            document.getElementById('wordCountStatus').textContent = `Improvement completed (used ${nUserCredit} credits)`;
            document.getElementById('wordCountAdvice').textContent = response.choices[0]?.message?.content;
        } catch (error) {
            console.error('Error improving text:', error);
            document.getElementById('wordCountStatus').textContent = 'Error improving text';
            document.getElementById('wordCountAdvice').textContent = 'Could not generate improvement. Please try again.';
        } finally {
            document.getElementById('wordCountSpinner').style.display = 'none';
        }
    }

    async function elaborateTextAnalysis(text) {
        // Show spinner and update status
        document.getElementById('elaborateTextStatus').textContent = 'Analyzing text in detail...';
        document.getElementById('elaborateTextSpinner').style.display = 'inline-block';
        document.getElementById('elaborateTextResult').style.display = 'block';
        
        try {
            // Get initial credits before analysis
            const initCreditsResponse = await apiClient.fetchCredits(apiKey);
            const initUserCredit = initCreditsResponse.total_available;
            
            // Call the chat completion API for elaborate analysis
            const response = await apiClient.chatCompletion(
                apiKey,
                txtModel,
                [
                    {
                        role: 'system',
                        content: celpip_extend_sys_prompt
                    },
                    {
                        role: 'user',
                        content: "Please elaborate on the following text:\n\n" + text
                    }
                ],
                {
                    temperature: 0.7,
                    max_tokens: 1000
                }
            );
            
            // Get credits after analysis
            const afterAnalysisResponse = await apiClient.fetchCredits(apiKey);
            const afterAnalysisCredit = afterAnalysisResponse.total_available;
            const creditsUsed = initUserCredit - afterAnalysisCredit;
            
            // Update the UI with the elaborate analysis
            document.getElementById('elaborateTextStatus').textContent = `Detailed analysis completed (used ${creditsUsed} credits)`;
            document.getElementById('elaborateTextContent').innerHTML = response.choices[0]?.message?.content.replace(/\n/g, '<br>');
        } catch (error) {
            console.error('Error in elaborate text analysis:', error);
            document.getElementById('elaborateTextStatus').textContent = 'Error in detailed analysis';
            document.getElementById('elaborateTextContent').textContent = 'Could not generate detailed analysis. Please try again.';
        } finally {
            // Hide the spinner
            document.getElementById('elaborateTextSpinner').style.display = 'none';
        }
    }
});
