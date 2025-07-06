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

<label class="form-label" for="textInput-id">{title}</label>
<div class="input-group">
    <textarea id="textInput-id" class="form-control" bind:value={message} rows="15"></textarea>
</div>
<div class="d-flex justify-content-end">
    {#if showCounter}
        <span>Count: {counts}</span>
    {/if}
</div>
