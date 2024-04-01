import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, cleanup } from '@testing-library/react';
import App from './App.jsx';

// Mock window.location
global.window = Object.create(window);
Object.defineProperty(window, 'location', {
  value: {
    hostname: 'localhost',
    origin: 'http://localhost', // add this line
    href: 'http://localhost/', // add this line
  },
});

// This is the exported function that contains all the tests
export default function AppTests() {
  // Cleanup after each test
  afterEach(cleanup);

  describe('App component', () => {
    it('renders without crashing', () => {
      render(<App />);
    });

    // Add more describe calls and it statements as needed
    describe('Navigation', () => {
      it('renders Register route', () => {
        render(<App />);
        expect(screen.getByText('Register')).toBeInTheDocument();
        expect(screen.getByText('PV Validation HUB')).toBeInTheDocument();
      });

      // Add more it statements to test other routes
    });

    // Add more describe calls for other aspects of the App component
  });
}
