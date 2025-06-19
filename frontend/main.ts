// Import all your Svelte components here
import ExampleComponent from '@/components/ExampleComponent.svelte';
import { mount } from 'svelte';

console.log('main.ts loaded')
// Map of component names to their implementations
const components = {
  'exampleComponent': ExampleComponent,
  // Add more components here as needed
};


// Auto-initialize components when the DOM is loaded
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event triggered')
    Object.entries(components).forEach(([id, Component]) => {
      console.log(`Initializing ${id} components`);
      const elements = document.querySelectorAll<HTMLElement>(`[data-svelte-component="${id}"]`);
      console.log(`Found ${elements.length} elements with data-svelte-component="${id}"`);
      
      elements.forEach((element) => {
        try {
          // Debug the raw dataset
          console.log('Raw dataset:', { ...element.dataset });
          
          // Get and parse the dataset
          const props = element.dataset;
          console.log(`Creating component with props:`, props);
          
          // Debug the Component constructor
          console.log('Component constructor:', Component);
          
          // Create the component with the parsed props
          console.log('Creating component with:', { target: element, props });
          const component = mount(Component, {
            target: element,
            props: props
          });
          
          console.log(`Successfully initialized ${id} component`, component);
          return component;
        } catch (error) {
          console.error(`Error initializing ${id} component:`, error);
        }
      });
    });
  });
}
