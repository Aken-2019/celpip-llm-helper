<script lang="ts">
    let { 
        showCounter = false, 
        message = $bindable(''),
        title = ''
    } = $props<{
        showCounter?: boolean;
        message?: string;
        title?: string;
    }>();

    let counts = $derived(
        message.trim() === '' ? 0 : message.trim().split(/\s+/).length
    );
</script>

<div class="d-flex justify-content-between align-items-center mb-2">
    <label class="form-label m-0" for="textInput-id">{title}</label>
    {#if showCounter}
        <span class="text-muted small">Count: {counts}</span>
    {/if}
</div>
<div class="input-group">
    <textarea id="textInput-id" class="form-control" bind:value={message} rows="12"></textarea>
</div>
