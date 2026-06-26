from pathlib import Path

import anthropic

from agents.tools import execute_tool


def run_agent(
    name: str,
    system: str,
    tools: list[dict],
    messages: list[dict],
    model: str,
    run_dir: Path,
    client: anthropic.Anthropic,
    project_root: Path,
) -> anthropic.types.Message:
    prefix = f"[{name}]"
    messages = list(messages)

    while True:
        print(f"\n{prefix} ", end="", flush=True)

        with client.messages.stream(
            model=model,
            max_tokens=64000,
            system=system,
            tools=tools,
            thinking={"type": "adaptive"},
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
            response = stream.get_final_message()

        print(flush=True)

        if response.stop_reason == "end_turn":
            return response

        if response.stop_reason != "tool_use":
            # refusal, pause_turn, or unexpected -- surface it and stop
            print(f"{prefix} stop_reason={response.stop_reason!r}", flush=True)
            return response

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"{prefix} -> {block.name}({_preview(block.input)})", flush=True)
            result = execute_tool(block.name, block.input, project_root)
            snippet = result[:120] + ("..." if len(result) > 120 else "")
            print(f"{prefix}    {snippet}", flush=True)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                }
            )

        messages.append({"role": "user", "content": tool_results})


def _preview(d: dict) -> str:
    parts = []
    for k, v in d.items():
        s = str(v)
        truncated = s[:40] + "..." if len(s) > 40 else s
        parts.append(f"{k}={truncated!r}")
    return ", ".join(parts)
