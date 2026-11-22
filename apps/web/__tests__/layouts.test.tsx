import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import AppLayout from "@/app/(app)/layout";
import ShareLayout from "@/app/share/[token]/layout";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
  useRouter: () => ({ push: vi.fn() }),
}));

afterEach(cleanup);

describe("route group layouts", () => {
  it("the app group renders the rail and the tab bar", () => {
    const { container } = render(<AppLayout>content</AppLayout>);
    expect(container.querySelector(".rail")).not.toBeNull();
    expect(container.querySelector(".tabbar")).not.toBeNull();
  });

  it("the share layout has no rail or tab bar in the DOM at all", () => {
    const { container } = render(<ShareLayout>content</ShareLayout>);
    expect(container.querySelector(".share-root")).not.toBeNull();
    expect(container.querySelector(".rail")).toBeNull();
    expect(container.querySelector(".tabbar")).toBeNull();
  });
});
