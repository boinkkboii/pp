import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../frontend/src/App';

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });
});
