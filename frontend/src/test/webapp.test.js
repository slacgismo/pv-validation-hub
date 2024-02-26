import React from 'react';
import ReactDOM from 'react-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../components/App/App.jsx';

const AppTest = () => {
  it('should display initial UI', () => {
    render(<App />);
    expect(screen.getByText(/Welcome to the Developer Group Leaderboard!/i)).toBeInTheDocument();
  });
};

AppTest();
