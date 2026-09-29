import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ChatWindow, type Message } from "./ChatWindow";

describe("ChatWindow", () => {
  it("shows a hint and no bubbles when there are no messages yet", () => {
    render(<ChatWindow messages={[]} pending={false} onSend={() => {}} />);

    expect(screen.getByText(/ask a product question/i)).toBeInTheDocument();
  });

  it("renders each message in a bubble", () => {
    const messages: Message[] = [
      { role: "user", content: "How do I rotate an API key?" },
      { role: "assistant", content: "From Settings > API Keys." },
    ];
    render(<ChatWindow messages={messages} pending={false} onSend={() => {}} />);

    expect(screen.getByText("How do I rotate an API key?")).toBeInTheDocument();
    expect(screen.getByText("From Settings > API Keys.")).toBeInTheDocument();
  });

  it("shows a thinking indicator while a turn is pending", () => {
    render(<ChatWindow messages={[]} pending={true} onSend={() => {}} />);

    expect(screen.getByText(/deskpilot is thinking/i)).toBeInTheDocument();
  });

  it("sends the trimmed input on button click and clears it", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatWindow messages={[]} pending={false} onSend={onSend} />);

    const input = screen.getByPlaceholderText(/ask deskpilot/i);
    await user.type(input, "  When does my plan renew?  ");
    await user.click(screen.getByRole("button", { name: /send/i }));

    expect(onSend).toHaveBeenCalledWith("When does my plan renew?");
    expect(input).toHaveValue("");
  });

  it("sends on Enter as well as on click", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatWindow messages={[]} pending={false} onSend={onSend} />);

    await user.type(screen.getByPlaceholderText(/ask deskpilot/i), "hello{Enter}");

    expect(onSend).toHaveBeenCalledWith("hello");
  });

  it("does not send an empty or whitespace-only message", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatWindow messages={[]} pending={false} onSend={onSend} />);

    await user.type(screen.getByPlaceholderText(/ask deskpilot/i), "   {Enter}");
    await user.click(screen.getByRole("button", { name: /send/i }));

    expect(onSend).not.toHaveBeenCalled();
  });

  it("does not send while a turn is pending", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatWindow messages={[]} pending={true} onSend={onSend} />);

    await user.type(screen.getByPlaceholderText(/ask deskpilot/i), "hello{Enter}");

    expect(onSend).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });
});
