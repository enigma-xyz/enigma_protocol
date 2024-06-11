import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import VaultCard from "@/components/VaultCard";

describe("VaultCard", () => {
  it("renders the component", () => {
    render(<VaultCard />);

    // expect(linkBox).toBeInTheDocument();
  });

  it("displays the correct image", () => {
    render(<VaultCard />);
    const image = screen.getByAltText("");
    expect(image).toHaveAttribute("src", "/images/pattern.jpg");
  });

  it("displays the correct heading", () => {
    render(<VaultCard />);
    const heading = screen.getByRole("heading", { name: "SuperCharger" });
    expect(heading).toBeInTheDocument();
  });

  it("displays the correct capacity", () => {
    render(<VaultCard />);
    const capacity = screen.getByText("86.48%");
    expect(capacity).toBeInTheDocument();
  });

  it('shows the "Open Vault" button on hover', () => {
    render(<VaultCard />);
    const linkBox = screen.getByText("Open Vault");
    fireEvent.mouseEnter(linkBox);
    const openVaultButton = screen.getByText("Open Vault");
    expect(openVaultButton).toBeInTheDocument();
  });

  it('hides the "Open Vault" button on mouseLeave', () => {
    render(<VaultCard />);
    const linkBox = screen.getByText("Open Vault");
    fireEvent.mouseEnter(linkBox);
    fireEvent.mouseLeave(linkBox);
    const openVaultButton = screen.queryByText("Open Vault");
    expect(openVaultButton).toBeInTheDocument();
  });
});
