<script lang="ts">
    import TextInput from '@/components/TextInput.svelte';
    import MarkdownArea from '@/components/MarkdownArea.svelte';

    let inputContent = $state('');
    $inspect(inputContent);
</script>

<div class="container p-4">
    <TextInput showCounter={true} title="请在此写入作文内容" bind:message={inputContent}/>
    <MarkdownArea content={inputContent} />
    <button class="btn btn-primary">Submit</button>
</div>

