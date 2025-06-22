<script lang="ts">
  export let count: number = 0;
  export let message: string = 'Hello, Svelte!';
  function handleClick() {
    count += 1;
  }
</script>

<div class="example-component">
  <h2>Welcome to Svelte!</h2>
  <p>This is a simple example component. {message}</p>
  <button on:click={handleClick}>
    Clicked {count} {count === 1 ? 'time' : 'times'}
  </button>
</div>

<style>
  .example-component {
    padding: 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    background-color: #f8fafc;
    margin: 1rem 0;
    max-width: 400px;
    text-align: center;
  }
  
  h2 {
    color: #1e40af;
    margin: 0 0 1rem 0;
  }
  
  p {
    color: #4b5563;
    margin: 0 0 1rem 0;
  }
  
  button {
    margin-top: 1rem;
    padding: 0.5rem 1.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.2s;
  }
  
  button:hover {
    background-color: #2563eb;
  }
  
  button:active {
    transform: translateY(1px);
  }
</style>
