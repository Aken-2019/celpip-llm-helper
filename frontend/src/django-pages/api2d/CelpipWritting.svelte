<script lang="ts">
    import TextInput from '@/components/TextInput.svelte';
    import MarkdownArea from '@/components/MarkdownArea.svelte';
    import { onMount } from 'svelte';
    import { ApiClient, ApiError } from '../../utils/apiClient';
    let {endpoint, 
        apiKey, 
        txtModel,
        improvePrompt,
    } = $props();
    let apiClient = new ApiClient({
        baseUrl: endpoint,
    });

    let inputContent = $state('');
    let outputContent = $state('`待生成...`');
    let suggestionContent = $state('`待生成...`');
    let isLoading = $state(false);
    let credit_comsumed = $state(-1)
    let total_available = $state(-1)
    let error_txt = $state('')
    
    onMount(async () => {
        try {
            const credits = await apiClient.fetchCredits(apiKey);
            total_available = credits.total_available;
        } catch (error) {
            console.error('Failed to fetch initial credits:', error);
            error_txt = '无法加载积分信息，请刷新页面重试';
        }
    });
    async function submit() {
        if (isLoading) return;
        credit_comsumed = -1
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
                    stop_sequences: ['</feedbacks>'],
                    max_tokens: 4096
                },
                '/v1/messages'
            );

            console.log(response)
            let wrapped_xml_response = "<root><revised_text>" + response.content[0]?.text + "</feedbacks></root>"
            let xml_response = new DOMParser().parseFromString(wrapped_xml_response, 'text/xml');
            outputContent = xml_response.getElementsByTagName('revised_text')[0]?.textContent || 'Error, please contact support';
            suggestionContent = xml_response.getElementsByTagName('grammar_focused_feedback')[0]?.textContent || 'Error, please contact support';
            credit_comsumed = response.usage.final_total
            const credit_after_submit = await apiClient.fetchCredits(apiKey)
            total_available = credit_after_submit.total_available;
        } 
        catch (error) {
            if (ApiError.isApiError(error)) {
                error_txt = error.data.message;
            }
            else {
                error_txt = error instanceof Error ? error.message : 'An unknown error occurred';
            }
        }
        finally {
            isLoading = false;
        }
    }
</script>

<div class="container p-4">
    <TextInput showCounter={true} title="请在此写入作文内容" bind:message={inputContent}/>
    <div class="d-flex justify-content-center">
        <button class="btn btn-primary my-2" onclick={submit} disabled={isLoading || total_available < 150}>
            {#if isLoading}
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                处理中...
            {:else}
                提交
            {/if}
        </button>
    </div>
    <div class="text-center mb-3">
            {#if credit_comsumed >= 0}
            <small class="badge bg-warning text-white px-2 py-1">
            本次消耗积分: {credit_comsumed}, 剩余积分: {total_available}
            </small>
            {/if}
            {#if total_available < 150 && total_available >=0 }
            <small class="badge bg-danger text-white px-2 py-1">
            余额（{total_available}）不足150，无法提交，请充值后刷新页面
            </small>
            {/if}
            {#if error_txt}
            <small class="badge bg-danger text-white px-2 py-1">
            {error_txt}
            </small>
            {/if}
    </div>
    <div class='my-4'>
        <MarkdownArea title='润色结果' content={outputContent} />
    </div>
    <div class='my-4'>
        <MarkdownArea title='语法建议' content={`
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
${suggestionContent}`} />
    </div>
</div>


