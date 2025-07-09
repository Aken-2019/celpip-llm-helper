<script lang="ts">
    import { marked } from 'marked';
    
    let { content = '', title = '', showCopyButton = false } = $props<string>();
    let html_content = $derived(marked(content));

    function copyToClipboard() {
        navigator.clipboard.writeText(content)
            .then(() => {
                // Optional: Show success feedback
                const button = document.querySelector('.copy-btn i');
                if (button) {
                    const originalClass = button.className;
                    button.className = 'bi bi-check me-1';
                    setTimeout(() => {
                        button.className = originalClass;
                    }, 2000);
                }
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
            });
    }
</script>

<div class="card">
    <div class="card-body">
        <h5 class="card-title">{title}</h5>
        <p class="card-text" id="card-text">
            {@html html_content}
        </p>
        {#if showCopyButton}
        <button 
            class="btn btn-outline-secondary btn-sm copy-btn" 
            onclick={copyToClipboard}
            title="复制到剪贴板">
            <i class="bi bi-clipboard me-1"></i>复制文字
        </button>
        {/if}
    </div>
</div>

<style>
    .copy-btn {
        transition: all 0.2s;
    }
    .copy-btn:active {
        transform: scale(0.95);
    }
</style>
