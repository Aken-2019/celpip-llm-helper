// Import all your Svelte components here
import ExampleComponent from '@/components/ExampleComponent.svelte';
import Recorder from '@/components/Recorder.svelte';
import TextInput from '@/components/TextInput.svelte';
import MarkdownArea from '@/components/MarkdownArea.svelte';
import CelpipWritting from '@/django-pages/api2d/CelpipWritting.svelte';
import { mount } from 'svelte';

console.log('main.ts loaded')

// Define the expected props interface for our components
interface ComponentProps {
  [key: string]: string | number | boolean | null | undefined;
}

// Helper function to parse dataset with type safety
function parseDataset(element: HTMLElement): ComponentProps {
  const props: ComponentProps = {};
  const dataset = element.dataset;

  Object.entries(dataset).forEach(([key, value]) => {
    if (value === undefined) return;
    
    // Try to parse the value based on its content
    if (value === 'true' || value === 'false') {
      props[key] = value === 'true';
    } else if (value === 'null') {
      props[key] = null;
    } else if (value === 'undefined') {
      props[key] = undefined;
    } else if (!isNaN(Number(value))) {
      // If it's a number, convert it
      props[key] = Number(value);
    } else {
      // Otherwise keep as string
      props[key] = value;
    }
  });

  return props;
}

// Map of component names to their implementations
const components = {
  'exampleComponent': ExampleComponent,
  'recorder': Recorder,
  'textInput': TextInput,
  'markdownArea': MarkdownArea,
  'celpipWritting': CelpipWritting,
  // Add more components here as needed
};

// Auto-initialize components when the DOM is loaded
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event triggered')
    Object.entries(components).forEach(([id, Component]) => {
      const elements = document.querySelectorAll<HTMLElement>(`[data-svelte-component="${id}"]`);
      
      elements.forEach((element) => {
        try {
          // Debug the raw dataset
          console.log('Raw dataset:', { ...element.dataset });
          
          // Use our type-safe parser
          const props = parseDataset(element);
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
