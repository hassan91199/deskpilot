import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { AccountSwitcher, DEMO_ACCOUNTS } from "./AccountSwitcher";

describe("AccountSwitcher", () => {
  it("lists all seeded demo accounts", () => {
    render(<AccountSwitcher accountId="acct-1" onChange={() => {}} />);

    for (const account of DEMO_ACCOUNTS) {
      expect(screen.getByRole("option", { name: account.label })).toBeInTheDocument();
    }
  });

  it("reflects the currently selected account", () => {
    render(<AccountSwitcher accountId="acct-2" onChange={() => {}} />);

    expect(screen.getByRole("combobox")).toHaveValue("acct-2");
  });

  it("calls onChange with the newly selected account id", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<AccountSwitcher accountId="acct-1" onChange={onChange} />);

    await user.selectOptions(screen.getByRole("combobox"), "acct-3");

    expect(onChange).toHaveBeenCalledWith("acct-3");
  });
});
