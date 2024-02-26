import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';

// This is the exported function that contains all the tests
export default function AppTests() {
  // Cleanup after each test
  afterEach(cleanup);

  describe('App component', () => {
    it('renders without crashing', () => {
      render(<BrowserRouter><App /></BrowserRouter>);
    });

    // Add more describe calls and it statements as needed
    describe('Navigation', () => {
      it('renders Register route', () => {
        render(<BrowserRouter><App /></BrowserRouter>);
        expect(screen.getByText('Register')).toBeInTheDocument();
      });

      // Add more it statements to test other routes
    });

    // Add more describe calls for other aspects of the App component
  });
}
