import { SvelteComponent } from 'svelte';

declare module '*.svelte' {
    import { SvelteComponent } from 'svelte';
    
    interface RecorderProps {
        length?: number;
        showPlayButton?: boolean;
        fileName?: string;
        metadata?: Record<string, any>;
        onRecordingComplete?: (detail: {
            blob: Blob;
            fileName: string;
            metadata: Record<string, any>;
        }) => void;
    }
    
    export default class Recorder extends SvelteComponent<RecorderProps> {
        // Add any methods or properties here if needed
    }
    
    // This makes TypeScript understand the custom event
    interface Window {
        addEventListener(
            type: 'recordingComplete', 
            listener: (event: CustomEvent<{
                blob: Blob;
                fileName: string;
                metadata: Record<string, any>;
            }>) => void,
            options?: boolean | AddEventListenerOptions
        ): void;
    }
}
