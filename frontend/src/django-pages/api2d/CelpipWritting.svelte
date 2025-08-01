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

    // State variables
    let inputContent = $state('');
    let outputContent = $state('`待生成...`');
    let suggestionContent = $state('`待生成...`');
    let isProcessing = $state(false);
    let credit_consumed = $state(0);
    let credits = $state<{total_available: number} | null>(null);
    let last_credits = $state<number | null>(null);
    let errorMessage = $state('');
    
    // Update credits and calculate consumption
    async function updateCredits() {
        try {
            const response = await apiClient.fetchCredits(apiKey);
            
            // Calculate credit consumption if we have a previous value
            if (last_credits !== null) {
                const currentCredits = response.total_available;
                credit_consumed = last_credits - currentCredits;
            }
            
            // Update last_credits for next calculation
            last_credits = response.total_available;
            credits = response;
            
            return credits;
        } catch (error) {
            console.error('Error updating credits:', error);
            errorMessage = '更新积分信息失败';
            throw error;
        }
    }
    
    // Initialize credits on mount
    onMount(async () => {
        try {
            await updateCredits();
        } catch (error) {
            console.error('Failed to fetch initial credits:', error);
            errorMessage = '无法加载积分信息，请刷新页面重试';
        }
    });
    
    async function submit() {
        if (isProcessing) return;
        
        // Reset states
        isProcessing = true;
        errorMessage = '';
        credit_consumed = 0;
        
        try {
            // Get current credits before processing
            await updateCredits();
            
            // Process the request
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
                    stop_sequences: ['</grammar_focused_feedback>'],
                    max_tokens: 4096
                },
                '/claude/v1/messages'
            );

            // Process response
            if (response?.content?.[0]?.text) {
                const wrapped_xml_response = "<root><revised_text>" + response.content[0].text + "</grammar_focused_feedback></root>";
                const xml_response = new DOMParser().parseFromString(wrapped_xml_response, 'text/xml');
                
                outputContent = xml_response.getElementsByTagName('revised_text')[0]?.textContent || 'Error, please contact support';
                suggestionContent = xml_response.getElementsByTagName('grammar_focused_feedback')[0]?.textContent || 'Error, please contact support';
                
                // Update credits after successful processing
                await updateCredits();
            } else {
                throw new Error('Invalid response format from API');
            }
        } catch (error) {
            console.error('Error in submit:', error);
            
            if (ApiError.isApiError(error)) {
                errorMessage = error.data?.message || error.message || 'API请求失败';
            } else if (error instanceof Error) {
                errorMessage = error.message || '处理请求时出错';
            } else {
                errorMessage = '发生未知错误';
            }
        } finally {
            isProcessing = false;
        }
    }
</script>

<div class="container p-4">
    <TextInput showCounter={true} title="请在此写入作文内容" bind:message={inputContent}/>
    <div class="d-flex justify-content-center">
        <button 
            class="btn btn-primary my-2" 
            onclick={submit} 
            disabled={isProcessing || (credits?.total_available ?? 0) < 150}
            data-testid="submit-button"
        >
            {#if isProcessing}
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                处理中...
            {:else}
                提交
            {/if}
        </button>
    </div>
    
    <!-- Status and Credit Info -->
    <div class="text-center mb-3">
        
        {#if credits}
            <div class="small">
                <span class="text-success">
                    当前剩余积分: {credits.total_available}
                </span>
                
                {#if credit_consumed > 0}
                    <span class="text-success ms-2">
                        本次消耗积分: {credit_consumed}
                    </span>
                {/if}
            </div>
            
            {#if credits.total_available < 150}
                <div class="text-danger mt-1">
                    为避免因点数不足导致功能异常，请先充值积分至150点以上。
                </div>
            {/if}
        {/if}
        
        {#if errorMessage}
            <div class="alert alert-danger py-1 mt-2">
                {errorMessage}
            </div>
        {/if}
    </div>
    
    <div class='my-4'>
        <MarkdownArea title='1. 润色结果' content={outputContent} />
    </div>
    
    <div class='my-4'>
        <MarkdownArea title='2. 具体建议' content={`
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
