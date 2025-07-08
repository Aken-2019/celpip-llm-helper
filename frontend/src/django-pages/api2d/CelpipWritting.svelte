<script lang="ts">
    import TextInput from '@/components/TextInput.svelte';
    import MarkdownArea from '@/components/MarkdownArea.svelte';
    import { ApiClient } from '../../utils/apiClient';
    let {endpoint, 
        apiKey, 
        txtModel,
        improvePrompt,
    } = $props();
    let apiClient = new ApiClient({
        baseUrl: endpoint,
    });

    let inputContent = $state('');
    let outputContent = $state('待生成...');
    let suggestionContent = $state('待生成...');
    let isLoading = $state(false);
    let credit_comsumed = $state(-1)
    let total_available = $state(-1)
    async function submit() {
        if (isLoading) return;
        const credit_before_submit =  await apiClient.fetchCredits(apiKey)

        isLoading = true;
        try {
            const response = await apiClient.chatCompletion(
                apiKey,
                txtModel,
                [
                    {
                        role: 'system',
                        content: improvePrompt,
                    },
                    {
                        role: 'user',
                        content: "<user_input>" + inputContent + "</user_input>"
                    },
                    {
                        role: 'assistant',
                        content: "<revised_text>"
                    }
                ],
                {
                    stop_sequences: ['</feedbacks>']
                },
                '/v1/messages'
            );
            let wrapped_xml_response = "<root><revised_text>" + response.content[0]?.text + "</feedbacks></root>"
            let xml_response = new DOMParser().parseFromString(wrapped_xml_response, 'text/xml');
            outputContent = xml_response.getElementsByTagName('revised_text')[0]?.textContent || 'Error, please contact support';
            suggestionContent = xml_response.getElementsByTagName('feedbacks')[0]?.textContent || 'Error, please contact support';
            
                


            const credit_after_submit = await apiClient.fetchCredits(apiKey)
            total_available = credit_after_submit.total_available;
            credit_comsumed = credit_before_submit.total_available - credit_after_submit.total_available;
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="container p-4">
    <TextInput showCounter={true} title="请在此写入作文内容" bind:message={inputContent}/>
    <div class="d-flex justify-content-center">
        <button class="btn btn-primary my-2" onclick={submit} disabled={isLoading}>
            {#if isLoading}
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                处理中...
            {:else}
                提交
            {/if}
        </button>
    </div>
    <div class="text-center mb-3">
        <small class="badge bg-warning text-white px-2 py-1">
            {#if credit_comsumed >= 0}
            本次消耗积分: {credit_comsumed}, 剩余积分: {total_available}
            {/if}
        </small>
    </div>
    <div class='my-4'>
        <MarkdownArea title='润色结果' content={outputContent} />
    </div>
    <div class='my-4'>
        <MarkdownArea title='分析与建议' content={suggestionContent} />
    </div>
</div>
