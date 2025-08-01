<script lang="ts">
import { onMount, onDestroy } from 'svelte';

// Define the recording details type
type RecordingDetails = {
  blob: Blob;
  fileName: string;
  metadata: Record<string, any>;
} | null;

// Component props
let {
  length,
  showPlayButton,
  fileName,
  metadata,
  audioRecord = $bindable(null),
  onRecordingComplete = null,
} = $props<{
  length?: number;
  showPlayButton?: boolean;
  fileName?: string;
  metadata?: Record<string, any>;
  audioRecord?: RecordingDetails | null
  onRecordingComplete?: (event: { detail: RecordingDetails | null }) => void;
}>();

// State
const lengthValue = $state(length ?? 60);
const fileNameValue = $state(fileName ?? 'recording.m4a');
const metadataValue = $state(metadata ?? {});

let remainingTime = $state(lengthValue);

  let timer: number | null = null;

  // State variables
  let mediaRecorder: MediaRecorder;
  let audioChunks: Blob[] = [];
  let audioUrl: string = $state('');
  let isRecording: boolean = $state(false);
  let audioPlayer = $state<HTMLAudioElement | null>(null);
  let stream: MediaStream;
  let audioContext: AudioContext;
  let analyser: AnalyserNode;
  let dataArray: Uint8Array;
  let animationId: number;

  
async function  startRecording() {
    try {
        // Reset remaining time
        remainingTime = length;
        
        // Clear any existing timer
        if (timer) {
            clearInterval(timer);
        }
        
        // Start the countdown timer
        timer = window.setInterval(() => {
            remainingTime--;
            if (remainingTime <= 0) {
                stopRecording();
            }
        }, 1000);
        
        // Initialize audioContext if it doesn't exist
        if (!audioContext) {
            audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        }
        
        // stream may contain both audio and video tracks
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Check if the browser supports the MP4/AAC MIME type
        const mimeType = MediaRecorder.isTypeSupported('audio/mp4') ? 'audio/mp4' : 'audio/mp4; codecs=mp4a.40.2';
        mediaRecorder = new MediaRecorder(stream, { mimeType });
        console.log('Using MIME type:', mediaRecorder.mimeType);

        audioChunks = [];
        // get audio from the stream
        const source = audioContext.createMediaStreamSource(stream);
        // analyser is used to capture time and frequency info
        analyser = audioContext.createAnalyser();
        source.connect(analyser);
        //A higher fftSize (e.g., 8192) might be better for analyzing the frequency components of spoken words, while a lower fftSize (e.g., 512) might be more suitable for detecting high-frequency components of background noise.
        analyser.fftSize = 8192;

        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        mediaRecorder.ondataavailable = (event: BlobEvent) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        // Set up the onstop handler before starting
        mediaRecorder.onstop = handleRecordingStop;
        mediaRecorder.start();
        isRecording = true;
        draw();

    } catch (err) {
        console.error('Error accessing media devices.', err);
    }
}



function handleRecordingStop() {
  const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/mp4' });
  audioUrl = URL.createObjectURL(audioBlob);
  // Update the recording details
  const recordingFileName = fileNameValue.endsWith('.m4a') ? fileNameValue : `${fileNameValue}.m4a`;
  const recordingMetadata = {
    ...metadataValue,
    duration: lengthValue - remainingTime,
    timestamp: new Date().toISOString(),
    mimeType: mediaRecorder.mimeType || 'audio/mp4'
  };
  
  // Update the recording details
  audioRecord = {
    blob: audioBlob,
    fileName: recordingFileName,
    metadata: recordingMetadata
  };
  


  // Call the onRecordingComplete callback if provided
  if (typeof onRecordingComplete === 'function') {
    try {
      onRecordingComplete({
        detail: audioRecord
      });
    } catch (err) {
      console.error('Error in onRecordingComplete callback:', err);
    }
  }
}

async function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        isRecording = false;
        cancelAnimationFrame(animationId);
        if (stream) {
            stream.getTracks().forEach((track: MediaStreamTrack) => track.stop());
        }
        
        // Clear the timer
        if (timer) {
            clearInterval(timer);
            timer = null;
        }
    }

}

async function  playRecording() {
    if (audioUrl && audioPlayer) {
        audioPlayer.play();
    }
}

  // Visualize the audio
  function draw() {
    if (!isRecording) return;
    
    const canvas = document.querySelector('canvas');
    if (!canvas) {
        console.error('Canvas element not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('Could not get 2D context');
        return;
    }
    const WIDTH = canvas.width;
    const HEIGHT = canvas.height;
    
    analyser.getByteFrequencyData(dataArray);
    
    ctx.clearRect(0, 0, WIDTH, HEIGHT);
    
    const barWidth = (WIDTH / dataArray.length) * 2.5;
    let x = 0;
    
    for (let i = 0; i < dataArray.length; i++) {
      const barHeight = dataArray[i] / (300/HEIGHT);
      const hue = i / dataArray.length * 360;
      ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
      ctx.fillRect(x, HEIGHT - barHeight, barWidth, barHeight);
      x += barWidth + 1;
    }
    
    animationId = requestAnimationFrame(draw);
  }
  
onMount(() => {
    return () => {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  });

onDestroy(() => {
    if (timer) {
        clearInterval(timer);
    }
  });
</script>

<div class="recorder-container">
    
    <div class="visualizer">
      <canvas height="20" class='w-100'></canvas>
    </div>
    <!-- Progress bar section on a new line -->
    <div class="progress mw-100" style="height: 24px;">
      <div 
        class="progress-bar bg-primary" 
        style={`width: ${(1-(remainingTime / length)) * 100}%; transition: width 0.3s ease;`}
        role="progressbar"
        aria-valuenow={1-(remainingTime / length)}
        aria-valuemin="0"
        aria-valuemax="1"
      ></div>
    </div>
    <br />

    <div class="controls">
      <div class="controls d-flex flex-column flex-md-row gap-2">
        <div class="w-100 w-md-auto flex-grow-1">
          {#if !isRecording}
            <button type="button" onclick={startRecording} class="btn w-100 text-nowrap btn-success">▶️ Start Recording</button>
          {:else}
            <button type="button" onclick={stopRecording} class="btn w-100 text-nowrap btn-danger">⏹️ Stop Recording</button>
          {/if}
        </div>
        <div class="w-100 w-md-auto flex-grow-1">
          <a 
            href={audioUrl} 
            download={`${new Date().toISOString().replace(/[:.]/g, '-')}.m4a`} 
            class="btn w-100 btn-warning text-nowrap {!audioUrl || isRecording ? 'disabled' : ''}"
            aria-disabled={!audioUrl || isRecording}
          >
            ⬇️ Download
          </a>
        </div>
      </div>
    </div>

  </div>

<style>

</style>
