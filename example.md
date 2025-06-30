# Example Usage

This document shows example usage of the Claude Conversation Converter.

## Input File Format

The converter expects Claude JSONL files with entries like:

```json
{"type": "summary", "summary": "AI Consciousness Research Discussion"}
{"type": "user", "uuid": "user-123", "timestamp": "2024-12-30T14:30:15Z", "message": {"content": [{"type": "text", "text": "Let's discuss consciousness"}]}, "sessionId": "session-abc"}
{"type": "assistant", "uuid": "assistant-456", "timestamp": "2024-12-30T14:30:45Z", "message": {"content": [{"type": "thinking", "thinking": "The user wants to explore consciousness..."}, {"type": "text", "text": "Consciousness is a fascinating topic..."}], "model": "claude-sonnet-4", "usage": {"input_tokens": 50, "output_tokens": 150}}, "sessionId": "session-abc"}
```

## Command Examples

### Basic conversion
```bash
python conversation-converter.py my-conversation.jsonl
```

### With custom output directory
```bash
python conversation-converter.py conversation.jsonl ./outputs/
```

### Processing multiple files
```bash
for file in *.jsonl; do
    python conversation-converter.py "$file" ./converted/
done
```

## Output Example

```markdown
# AI Consciousness Research Discussion

## Thread Header
**Summary:** AI Consciousness Research Discussion
**Date:** December 30, 2024
**Model:** claude-sonnet-4-20250514
**Working Directory:** /Users/researcher/ai-project
**Session ID:** session-abc123

---

## Message Turn 1
**Time:** 2:30:15 PM
**Tokens:** 50 in → 150 out

**User:**
Let's discuss consciousness

**Thinking:**
The user wants to explore consciousness...

**Assistant:**
Consciousness is a fascinating topic that touches on philosophy, neuroscience, and increasingly, artificial intelligence research...
```

## Agent Session Example

When the conversation includes agent tasks, they're formatted clearly:

```markdown
**Tools:**
- Task: "Research consciousness papers" 

```
╭─ AGENT START ─────────────────────────────────────
│ Time: 2:31:00 PM
│ Tokens: 200 in → 500 out
│ Working Directory: /Users/researcher/ai-project
│ Session ID: agent-xyz789 (sidechain)
├─────────────────────────────────────────────────

Agent: I'll search for recent consciousness research papers...

Agent Tools:
- WebSearch: "consciousness artificial intelligence 2024"
- Read: "consciousness_papers.md"

╰─ AGENT END ───────────────────────────────────────
```

## Benefits

- **Readable Format**: Easy to review and share conversations
- **Complete Preservation**: No information lost in conversion
- **Professional Documentation**: Suitable for research and archival
- **Cost Tracking**: Monitor token usage across projects
- **Agent Clarity**: Clear visualization of nested agent work