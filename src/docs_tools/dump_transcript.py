#!/usr/bin/env python3
"""Print a readable digest of one Claude Code subagent transcript (JSON lines).

Usage:
    python3 -I dump_transcript.py TRANSCRIPT.jsonl [--text N] [--tool N]
                                  [--results N] [--grep REGEX] [--section S]

Prints, in order:
  1. the first user message (the task) in full;
  2. every later user message that is not a tool result (course corrections) in full;
  3. the text of each assistant message (truncated to --text characters, default 1500)
     and a one-line summary of each tool call (truncated to --tool characters, default 200);
     with --results N > 0 also the first N characters of each tool result;
  4. the final report in full: the input of a SubagentHandback call if there is one,
     otherwise the last assistant text.

--grep REGEX   print only tool results / assistant texts that match REGEX (case-insensitive),
               with 300 characters of context around each match, instead of the digest.
--results-for REGEX  print every tool call whose input matches REGEX (case-insensitive) and
               its result (first --results N characters, default 3000), instead of the digest.
--section S    one of: task, middle, final, all (default all), or rawfinal (the final
               report alone, verbatim, with no header; used for saved copies of reports).

Thinking blocks are skipped. The script only reads the file it is given.
"""
import json
import re
import sys


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def content_items(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return [{"type": "text", "text": c}]
    if isinstance(c, list):
        return c
    return []


def result_text(item):
    c = item.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        out = []
        for x in c:
            if isinstance(x, dict) and x.get("type") == "text":
                out.append(x.get("text", ""))
        return "\n".join(out)
    return ""


def short(s, n):
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[:n] + " [...]"


def tool_summary(item, n):
    name = item.get("name", "?")
    inp = item.get("input", {}) or {}
    if name == "Bash":
        body = inp.get("command", "")
    elif name in ("Read", "Write", "Edit"):
        body = inp.get("file_path", "")
        if name == "Read" and inp.get("offset"):
            body += f" offset={inp.get('offset')} limit={inp.get('limit')}"
    elif name in ("Grep", "Glob"):
        body = f"{inp.get('pattern', '')} in {inp.get('path', '')}"
    elif name == "WebSearch":
        body = inp.get("query", "")
    elif name == "WebFetch":
        body = f"{inp.get('url', '')} :: {inp.get('prompt', '')}"
    elif name in ("Agent", "Task"):
        body = f"{inp.get('description', '')} :: {inp.get('prompt', '')}"
    else:
        body = json.dumps(inp, ensure_ascii=False)
    return f"[TOOL {name}] {short(body, n)}"


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    path = args[0]
    text_n, tool_n, res_n, grep, section = 1500, 200, 0, None, "all"
    results_for = None
    i = 1
    while i < len(args):
        a = args[i]
        if a == "--text":
            text_n = int(args[i + 1]); i += 2
        elif a == "--tool":
            tool_n = int(args[i + 1]); i += 2
        elif a == "--results":
            res_n = int(args[i + 1]); i += 2
        elif a == "--grep":
            grep = re.compile(args[i + 1], re.I); i += 2
        elif a == "--section":
            section = args[i + 1]; i += 2
        elif a == "--results-for":
            results_for = re.compile(args[i + 1], re.I); i += 2
        else:
            i += 1

    rows = load(path)
    msgs = [r for r in rows if r.get("type") in ("user", "assistant") and isinstance(r.get("message"), dict)]

    if results_for is not None:
        # print each tool call whose input matches the pattern, followed by its result
        calls, outs = [], {}
        for r in msgs:
            for x in content_items(r["message"]):
                if x.get("type") == "tool_use":
                    calls.append(x)
                elif x.get("type") == "tool_result":
                    outs[x.get("tool_use_id")] = result_text(x)
        lim = res_n if res_n > 0 else 3000
        for x in calls:
            s = json.dumps(x.get("input", {}), ensure_ascii=False)
            if results_for.search(s):
                print("=" * 10, tool_summary(x, 300))
                out = outs.get(x.get("id"), "(no result)")
                print(out if len(out) <= lim else out[:lim] + " [...]")
                print()
        return

    first_user = None
    final_report = None
    last_text = None
    digest = []
    for r in msgs:
        m = r["message"]
        role = m.get("role") or r.get("type")
        items = content_items(m)
        if role == "user":
            texts = [x.get("text", "") for x in items if x.get("type") == "text"]
            results = [x for x in items if x.get("type") == "tool_result"]
            if texts and not results and not r.get("isMeta"):
                t = "\n".join(texts)
                if first_user is None:
                    first_user = t
                else:
                    digest.append(("USER", t))
            for x in results:
                digest.append(("RESULT", result_text(x)))
        elif role == "assistant":
            for x in items:
                if x.get("type") == "text" and x.get("text", "").strip():
                    digest.append(("TEXT", x["text"]))
                    last_text = x["text"]
                elif x.get("type") == "tool_use":
                    digest.append(("TOOL", x))
                    if x.get("name") == "SubagentHandback":
                        final_report = (x.get("input") or {}).get("message")

    if grep is not None:
        for kind, payload in digest:
            if kind == "TOOL":
                s = json.dumps(payload.get("input", {}), ensure_ascii=False)
            else:
                s = payload
            for mt in grep.finditer(s):
                a, b = max(0, mt.start() - 300), min(len(s), mt.end() + 300)
                print(f"--- {kind}: ...{s[a:b]}...\n")
        return

    if section in ("task", "all"):
        print("=" * 30, "TASK (first user message)", "=" * 30)
        print(first_user or "(none found)")
    if section in ("middle", "all"):
        print("\n" + "=" * 30, "MIDDLE", "=" * 30)
        for kind, payload in digest:
            if kind == "USER":
                print("\n[USER MESSAGE]\n" + payload)
            elif kind == "TEXT":
                print("\n[ASSISTANT] " + (payload if len(payload) <= text_n else payload[:text_n] + " [...]"))
            elif kind == "TOOL":
                if payload.get("name") == "SubagentHandback":
                    print("[TOOL SubagentHandback] (final report, printed below)")
                else:
                    print(tool_summary(payload, tool_n))
            elif kind == "RESULT" and res_n > 0:
                print("    [RESULT] " + short(payload, res_n))
    if section == "rawfinal":
        # final report only, byte for byte, no header (for verbatim copies)
        sys.stdout.write(final_report if final_report else (last_text or ""))
        return
    if section in ("final", "all"):
        print("\n" + "=" * 30, "FINAL REPORT", "=" * 30)
        print(final_report if final_report else (last_text or "(none found)"))


if __name__ == "__main__":
    main()
