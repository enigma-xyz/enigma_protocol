import { render, screen } from "@testing-library/react";
import Home from "@/pages/index";
import { useRouter } from "next/router";

jest.mock("next/router", () => ({
  useRouter: jest.fn(),
}));

describe("Home", () => {
  it("renders a heading", () => {
    useRouter.mockImplementation(() => ({
      route: "/",
      pathname: "/",
      query: {},
      asPath: "/",
    }));

    render(<Home />);

    const heading = screen.getByRole("heading", {
      name: /Instantly deploy your Next\.js!/i,
    });

    expect(heading).toBeInTheDocument();
  });
  it("renders a paragraph", () => {
    useRouter.mockImplementation(() => ({
      route: "/",
      pathname: "/",
      query: {},
      asPath: "/",
    }));

    render(<Home />);

    const p = screen.getByRole("paragraph");

    expect(p).toBeInTheDocument();
  });
});
