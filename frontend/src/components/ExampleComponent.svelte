<script lang="ts">
  let { 
    count = 0, 
    message = 'Hello, Svelte!' 
  } = $props<{
    count?: number;
    message?: string;
  }>();

  function handleClick() {
    count += 1;
  }
</script>

<div class="container mt-5">
  <div class="card text-center">
    <div class="card-header bg-primary text-white">
      <h2 class="card-title mb-0">Welcome to Svelte!</h2>
    </div>
    <div class="card-body">
      <p class="card-text lead">This is a simple example component. {message}</p>
      <button 
        onclick={handleClick} 
        class="btn btn-primary"
      >
        Clicked {count} {count === 1 ? 'time' : 'times'}
      </button>
    </div>
    <div class="card-footer text-muted">
      Powered by Svelte & Bootstrap
    </div>
  </div>
</div>
