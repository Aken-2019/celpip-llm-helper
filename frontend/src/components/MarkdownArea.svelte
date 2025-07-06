<script lang="ts">
    import { marked } from 'marked';
    let {content=''} = $props<string>();

    let htmlContent = $derived(marked(content));
</script>

{@html htmlContent}