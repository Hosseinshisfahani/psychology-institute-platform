import React from 'react';
import { render } from '@testing-library/react';
import App from './App';

test('renders psychology institute title', () => {
  const { getByText } = render(<App />);
  const titleElement = getByText(/مرکز مشاوره و خدمات روانشناسی سرمد/i);
  expect(titleElement).toBeInTheDocument();
});
