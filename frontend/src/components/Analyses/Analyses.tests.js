import React from 'react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import {
  render, screen, cleanup, waitForElementToBeRemoved, waitFor, fireEvent, getByTestId, findByTestId,
} from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import * as router from 'react-router';
import Dashboard from './Analyses.jsx';

// Mock window.location.hostname
global.window = Object.create(window);
Object.defineProperty(window, 'location', {
  value: {
    hostname: 'localhost',
  },
});

// Mock the DashboardService module
jest.mock('../../services/dashboard_service.js', () => ({
  useGetAnalysisSet: jest.fn(() => [false, false, [{ id: 'development', title: 'Dev Analysis' }]]),
}));

// This is the exported function that contains all the tests
export default function DashboardTests() {
  // Cleanup after each test
  afterEach(cleanup);

  describe('Analyses component', () => {
    it('renders without crashing', () => {
      render(<Dashboard />, { wrapper: BrowserRouter });
    });

    it('displays circular progress bar while loading', () => {
      render(<Dashboard />, { wrapper: BrowserRouter });
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('updates card once loading is done', async () => {
      render(<Dashboard />, { wrapper: BrowserRouter });
      await waitForElementToBeRemoved(() => screen.getByRole('progressbar'));
      expect(screen.getByText('Dev Analysis')).toBeInTheDocument();
    });
  });
/*
This test needs to be fixed/completed when I have more time. Its... tricky.
  describe('Analysis Cards', () => {
    it('Should navigate to each analysis page when the card was clicked', async () => {
      render(<Dashboard />, { wrapper: BrowserRouter });

      const navigate = jest.fn();
      jest.spyOn(router, 'useNavigate').mockImplementation(() => navigate);

      // Wait for the progress bar to be removed
      await waitForElementToBeRemoved(() => screen.getByRole('progressbar'));

      // Find the card by its analysis_name
      const card = screen.getByTestId('analysis-card0');

      // Simulate a user clicking the card
      await userEvent.click(card);
      console.log("here", navigate);

      // Check if navigation was called
      await waitFor(() => expect(navigate).toHaveBeenCalled());
    });
  });
  */
}
