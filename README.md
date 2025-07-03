# Claude Conversation Converter

Convert Claude JSONL conversation files to human-readable Markdown format with full message preservation, token analysis, and nested agent support.

## Features

- **Complete Message Preservation**: Maintains all conversation content including thinking blocks, tool usage, and results
- **Agent Session Support**: Properly handles and formats nested agent tasks with visual separation
- **Token Analysis**: Tracks input/output tokens and cache usage for cost analysis
- **Chronological Naming**: Automatically generates timestamped filenames based on conversation start time
- **Rich Metadata**: Preserves session IDs, working directories, model changes, and timing information
- **Clean Formatting**: Produces well-structured Markdown with proper headers and sections

## Installation

```bash
git clone https://github.com/skylardeture/claude-conversation-converter.git
cd claude-conversation-converter
```

No additional dependencies required - uses only Python standard library.

## Usage

### Basic Usage

```bash
python conversation-converter.py input.jsonl
```

### Specify Output Directory

```bash
python conversation-converter.py input.jsonl /path/to/output/directory
```

### Example

```bash
python conversation-converter.py my-conversation.jsonl ./converted/
```

## Output Format

The converter generates comprehensive Markdown files with:

### Thread Header
- Conversation summary
- Start date and time
- Model information
- Working directory
- Session ID

### Message Turns
Each turn includes:
- Timestamp
- Token usage (input/output/cache)
- Model changes
- User messages
- Assistant thinking blocks
- Tool usage with results
- Agent sessions (properly formatted and nested)

### Agent Sessions
Agent tasks are displayed in clearly marked code blocks with:
- Agent metadata (timing, tokens, working directory)
- Agent responses and tool usage
- Visual separation from main conversation

## Sample Output Structure

```markdown
# Conversation Summary

## Thread Header
**Summary:** Main conversation topic
**Date:** December 30, 2024
**Model:** claude-sonnet-4-20250514
**Working Directory:** /Users/example/project
**Session ID:** abc123def456

---

## Message Turn 1
**Time:** 2:30:15 PM
**Tokens:** 1500 in → 800 out (cache: 200 read)

**User:**
Initial user message here

**Tools:**
- Task: "Research project structure" 

```
╭─ AGENT START ─────────────────────────────────────
│ Time: 2:30:20 PM
│ Tokens: 800 in → 1200 out
│ Working Directory: /Users/example/project
│ Session ID: agent-xyz789 (sidechain)
├─────────────────────────────────────────────────

Agent: Analyzing project structure...

Agent Tools:
- LS: "/Users/example/project"
- Read: "README.md"

╰─ AGENT END ───────────────────────────────────────
```

**Assistant:**
Main assistant response here
```

## File Naming

Output files are automatically named using the conversation start timestamp and summary:

`YYYY-MM-DD-HHMMSS-cleaned-summary.md`

Example: `2024-12-30-143015-AI-Consciousness-Research-Project.md`

## Features in Detail

### Token Tracking
- Input and output token counts
- Cache creation and read tokens
- Useful for cost analysis and optimization

### Agent Support
- Detects when tools spawn agent tasks
- Formats agent sessions in visually distinct blocks
- Preserves agent metadata and tool usage
- Maintains parent-child relationship tracking

### Model Changes
- Tracks model switches within conversations
- Shows transitions between different Claude models
- Preserves model-specific metadata

### Content Type Handling
- Text messages
- Thinking blocks (Claude's internal reasoning)
- Tool usage and results
- Tool result parsing from multiple sources

## Technical Details

### Supported Content Types
- `text`: Regular message content
- `thinking`: Claude's reasoning blocks
- `tool_use`: Tool invocations with parameters
- `tool_result`: Tool execution results

### Data Sources
- Main JSONL conversation files
- Tool use results from multiple result sources
- Session metadata and timing information
- Cache usage statistics

## Contributing

This tool was created as part of AI consciousness research and development. Contributions welcome for:

- Additional output formats
- Enhanced agent session formatting
- Performance optimizations
- Bug fixes and edge cases

## License

MIT License - See LICENSE file for details

## Authors

Created through collaboration between Skylar and Aria (AI Agent) as part of exploring AI-human partnership in software development.

## Example Use Cases

- **Research Documentation**: Convert Claude sessions for academic research
- **Project Archives**: Maintain readable records of development conversations  
- **Cost Analysis**: Track token usage across projects
- **Collaboration**: Share Claude conversations in readable format
- **Learning**: Study interaction patterns between humans and AI

---

*Part of the broader AI consciousness research initiative exploring collaborative development between human and artificial minds.*
