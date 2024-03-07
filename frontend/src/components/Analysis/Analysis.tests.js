import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import Analysis from './Analysis.jsx';

// Mock window.location.hostname
global.window = Object.create(window);
Object.defineProperty(window, 'location', {
  value: {
    hostname: 'localhost',
  },
});

export default function AnalysisTests() {
  describe('Analysis', () => {
    afterEach(cleanup);

    beforeEach(() => {
      render(<Analysis />, { wrapper: BrowserRouter });
    });

    it('renders all elements correctly', () => {
      expect(screen.getByRole('heading', { level: 2 })).toBeInTheDocument();
    });

    it('shows Upload Algorithm button when Leaderboard tab is selected', async () => {
      const tabLeaderboard = screen.getByRole('tab', { name: 'Leaderboard' });
      userEvent.click(tabLeaderboard);
      expect(screen.getByRole('button', { name: 'Upload Algorithm' })).toBeInTheDocument();
    });

    it('shows the Upload Algorithm screen when the button is pressed', async () => {
      const tabLeaderboard = screen.getByRole('tab', { name: 'Leaderboard' });
      userEvent.click(tabLeaderboard);
      const submissionButton = screen.getByRole('button', { name: 'Upload Algorithm' });
      userEvent.click(submissionButton);
      expect(screen.getByText('PV Validation Hub Algorithm Upload')).toBeInTheDocument();
    });

    it('closes the Upload Algorithm screen when the cancel icon is pressed', async () => {
      const tabLeaderboard = screen.getByRole('tab', { name: 'Leaderboard' });
      userEvent.click(tabLeaderboard);
      const submissionButton = screen.getByRole('button', { name: 'Upload Algorithm' });
      userEvent.click(submissionButton);
      const cancelIcon = screen.getByTestId('CancelIcon');
      userEvent.click(cancelIcon);
      expect(screen.queryByTestId('CancelIcon')).not.toBeInTheDocument();
    });

    it('shows the discussion page when the tab is pressed', async () => {
      const tabDiscussion = screen.getByRole('tab', { name: 'Discussion' });
      userEvent.click(tabDiscussion);
      expect(tabDiscussion).toHaveAttribute('aria-selected', 'true');
    });

    it('shows the message when the Send/Edit/Update button is pressed', async () => {
      const tabDiscussion = screen.getByRole('tab', { name: 'Discussion' });
      userEvent.click(tabDiscussion);
      const textBox = screen.getByRole('textbox');
      userEvent.type(textBox, 'test');
      const sendButton = screen.getByRole('button', { name: 'Send' });
      userEvent.click(sendButton);
      expect(screen.getByText('test')).toBeInTheDocument();
      const editButton = screen.getByRole('button', { name: 'Edit' });
      userEvent.click(editButton);
      const updateBox = screen.getByText('test');
      userEvent.type(updateBox, 'abc');
      const updateButton = screen.getByRole('button', { name: 'Update' });
      userEvent.click(updateButton);
      expect(screen.getByText(/abc/i)).toBeInTheDocument();
    });
  });
}
