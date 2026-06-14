import { render, screen } from "@testing-library/react";
import { App } from "./App";

test("renders the scaffold heading", () => {
  render(<App />);
  expect(screen.getByRole("heading", { name: /scaffold ready/i })).toBeInTheDocument();
});
