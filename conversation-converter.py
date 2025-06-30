#!/usr/bin/env python3
"""
Claude Conversation JSONL to Markdown Converter

Transforms Claude conversation JSONL files into human-readable markdown format
with full message preservation, token analysis, and nested agent support.

Usage:
    python conversation-converter.py input.jsonl [output_dir]
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class ConversationConverter:
    def __init__(self):
        self.summaries = []
        self.messages = []
        self.current_model = None
        self.session_id = None
        self.working_dir = None
        self.start_time = None
        
    def parse_jsonl_file(self, file_path: str) -> None:
        """Parse JSONL file and extract conversation data."""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                    
                try:
                    data = json.loads(line)
                    self._process_entry(data, line_num)
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                except Exception as e:
                    print(f"Warning: Error processing line {line_num}: {e}")
    
    def _process_entry(self, data: Dict[str, Any], line_num: int) -> None:
        """Process a single JSONL entry."""
        entry_type = data.get('type')
        
        if entry_type == 'summary':
            self.summaries.append(data.get('summary', ''))
        elif entry_type in ['user', 'assistant']:
            self._process_message(data)
    
    def _process_message(self, data: Dict[str, Any]) -> None:
        """Process a user or assistant message."""
        msg = {
            'type': data.get('type'),
            'uuid': data.get('uuid'),
            'parent_uuid': data.get('parentUuid'),
            'timestamp': data.get('timestamp'),
            'is_sidechain': data.get('isSidechain', False),
            'session_id': data.get('sessionId'),
            'working_dir': data.get('cwd'),
            'version': data.get('version'),
            'message': data.get('message', {}),
            'tool_use_result': data.get('toolUseResult'),
            'request_id': data.get('requestId')
        }
        
        # Track session metadata
        if not self.session_id:
            self.session_id = msg['session_id']
        if not self.working_dir:
            self.working_dir = msg['working_dir']
        if not self.start_time and msg['timestamp']:
            self.start_time = msg['timestamp']
            
        # Track model changes
        if msg['type'] == 'assistant' and 'model' in msg['message']:
            model = msg['message']['model']
            if model != self.current_model:
                msg['model_change'] = (self.current_model, model)
                self.current_model = model
        
        self.messages.append(msg)
    
    def _format_timestamp(self, timestamp_str: str) -> str:
        """Format timestamp for display."""
        if not timestamp_str:
            return ""
        
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%I:%M:%S %p").lstrip('0')
        except:
            return timestamp_str
    
    def _format_tokens(self, usage: Dict[str, Any]) -> str:
        """Format token usage information."""
        if not usage:
            return ""
        
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        cache_creation = usage.get('cache_creation_input_tokens', 0)
        cache_read = usage.get('cache_read_input_tokens', 0)
        
        result = f"{input_tokens} in → {output_tokens} out"
        
        if cache_creation or cache_read:
            cache_parts = []
            if cache_creation:
                cache_parts.append(f"+{cache_creation} created")
            if cache_read:
                cache_parts.append(f"{cache_read} read")
            result += f" (cache: {', '.join(cache_parts)})"
        
        return result
    
    def _extract_content(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Extract different content types from a message."""
        content = message.get('content', [])
        if isinstance(content, str):
            return {'text': [content], 'thinking': [], 'tool_use': [], 'tool_result': []}
        
        result = {
            'text': [],
            'thinking': [],
            'tool_use': [],
            'tool_result': []
        }
        
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    item_type = item.get('type', '')
                    if item_type == 'text':
                        result['text'].append(item.get('text', ''))
                    elif item_type == 'thinking':
                        result['thinking'].append(item.get('thinking', ''))
                    elif item_type == 'tool_use':
                        result['tool_use'].append(item)
                    elif item_type == 'tool_result':
                        result['tool_result'].append(item)
                elif isinstance(item, str):
                    # Handle case where content list contains raw strings
                    result['text'].append(item)
        
        return result
    
    def _format_tool_use(self, tool_data: Dict[str, Any]) -> str:
        """Format tool usage information."""
        name = tool_data.get('name', 'Unknown')
        tool_input = tool_data.get('input', {})
        
        # Format input concisely
        if isinstance(tool_input, dict):
            if 'command' in tool_input:
                detail = f"`{tool_input['command']}`"
            elif 'query' in tool_input:
                detail = f'"{tool_input["query"]}"'
            elif 'prompt' in tool_input:
                detail = f'"{tool_input["prompt"][:100]}{"..." if len(tool_input["prompt"]) > 100 else ""}"'
            else:
                detail = str(tool_input)[:100]
        else:
            detail = str(tool_input)[:100]
        
        return f"**{name}:** {detail}"
    
    def _format_tool_result(self, result_data: Dict[str, Any], tool_use_result: Optional[Dict[str, Any]] = None) -> str:
        """Format tool result information."""
        content = result_data.get('content', '')
        
        # Use toolUseResult if available for more details
        if tool_use_result:
            if 'stdout' in tool_use_result:
                content = tool_use_result['stdout']
            elif 'newTodos' in tool_use_result:
                content = f"Updated todos: {len(tool_use_result['newTodos'])} items"
        
        if isinstance(content, str):
            if len(content) > 200:
                return f'→ "{content[:200]}..."'
            return f'→ "{content}"'
        
        return f"→ {str(content)[:200]}"
    
    def _group_messages_by_turn(self) -> List[List[Dict[str, Any]]]:
        """Group messages into conversation turns."""
        turns = []
        current_turn = []
        
        for msg in self.messages:
            if msg['is_sidechain']:
                # Handle sidechain (agent) messages separately
                continue
                
            if msg['type'] == 'user' and current_turn:
                # Start new turn
                turns.append(current_turn)
                current_turn = [msg]
            else:
                current_turn.append(msg)
        
        if current_turn:
            turns.append(current_turn)
        
        return turns
    
    def _find_agent_messages(self, parent_uuid: str) -> List[Dict[str, Any]]:
        """Find agent messages for a given parent UUID."""
        return [msg for msg in self.messages 
                if msg['is_sidechain'] and msg['parent_uuid'] == parent_uuid]
    
    def _format_agent_session(self, agent_messages: List[Dict[str, Any]], indent: str = "│ ") -> str:
        """Format agent session messages."""
        if not agent_messages:
            return ""
        
        result = []
        result.append("```")
        result.append("╭─ AGENT START ─────────────────────────────────────")
        
        # Agent metadata
        first_msg = agent_messages[0]
        if first_msg['timestamp']:
            result.append(f"│ Time: {self._format_timestamp(first_msg['timestamp'])}")
        if 'usage' in first_msg.get('message', {}):
            tokens = self._format_tokens(first_msg['message']['usage'])
            result.append(f"│ Tokens: {tokens}")
        if first_msg['working_dir']:
            result.append(f"│ Working Directory: {first_msg['working_dir']}")
        if first_msg['session_id']:
            result.append(f"│ Session ID: {first_msg['session_id']} (sidechain)")
        
        result.append("├─────────────────────────────────────────────────")
        result.append("")
        
        # Agent messages
        for msg in agent_messages:
            content = self._extract_content(msg['message'])
            
            if content['text']:
                result.append(f"Agent: {' '.join(content['text'])}")
                result.append("")
            
            if content['tool_use']:
                result.append("Agent Tools:")
                for tool in content['tool_use']:
                    tool_line = self._format_tool_use(tool)
                    result.append(f"- {tool_line}")
                result.append("")
        
        result.append("╰─ AGENT END ───────────────────────────────────────")
        result.append("```")
        
        return "\n".join(result)
    
    def generate_markdown(self) -> str:
        """Generate the complete markdown conversation."""
        lines = []
        
        # Header
        if self.summaries:
            main_summary = self.summaries[0] if self.summaries else "Conversation"
        else:
            main_summary = "Conversation"
        
        lines.append(f"# {main_summary}")
        lines.append("")
        
        # Thread Header
        lines.append("## Thread Header")
        if self.summaries:
            for i, summary in enumerate(self.summaries):
                lines.append(f"**Summary {i+1}:** {summary}")
        
        if self.start_time:
            dt = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
            lines.append(f"**Date:** {dt.strftime('%B %d, %Y')}")
        
        if self.current_model:
            lines.append(f"**Model:** {self.current_model}")
        
        if self.working_dir:
            lines.append(f"**Working Directory:** {self.working_dir}")
        
        if self.session_id:
            lines.append(f"**Session ID:** {self.session_id}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Message turns
        turns = self._group_messages_by_turn()
        
        for turn_num, turn in enumerate(turns, 1):
            lines.append(f"## Message Turn {turn_num}")
            
            # Turn metadata from first message
            first_msg = turn[0]
            if first_msg['timestamp']:
                lines.append(f"**Time:** {self._format_timestamp(first_msg['timestamp'])}")
            
            # Find assistant message for token info
            assistant_msg = next((msg for msg in turn if msg['type'] == 'assistant'), None)
            if assistant_msg and 'usage' in assistant_msg.get('message', {}):
                tokens = self._format_tokens(assistant_msg['message']['usage'])
                lines.append(f"**Tokens:** {tokens}")
            
            lines.append("")
            
            # Process each message in turn
            for msg in turn:
                content = self._extract_content(msg['message'])
                
                # Model changes
                if msg.get('model_change'):
                    old_model, new_model = msg['model_change']
                    lines.append(f"**Model changed:** {old_model} → {new_model}")
                    lines.append("")
                
                # User messages
                if msg['type'] == 'user':
                    if content['text']:
                        lines.append("**User:**")
                        lines.append(' '.join(content['text']))
                        lines.append("")
                
                # Assistant content
                elif msg['type'] == 'assistant':
                    # Thinking blocks
                    if content['thinking']:
                        lines.append("**Thinking:**")
                        for thinking in content['thinking']:
                            lines.append(thinking)
                        lines.append("")
                    
                    # Tool usage
                    if content['tool_use']:
                        lines.append("**Tools:**")
                        for tool in content['tool_use']:
                            tool_line = self._format_tool_use(tool)
                            
                            # Check for agent tasks
                            if tool.get('name') == 'Task':
                                # Find agent messages
                                agent_msgs = self._find_agent_messages(msg['uuid'])
                                if agent_msgs:
                                    lines.append(f"- {tool_line}")
                                    lines.append("")
                                    lines.append(self._format_agent_session(agent_msgs))
                                    lines.append("")
                                else:
                                    lines.append(f"- {tool_line}")
                            else:
                                # Regular tool with result
                                result_info = ""
                                if msg['tool_use_result']:
                                    result_info = self._format_tool_result({}, msg['tool_use_result'])
                                lines.append(f"- {tool_line} {result_info}")
                        lines.append("")
                    
                    # Assistant text response
                    if content['text']:
                        lines.append("**Assistant:**")
                        lines.append(' '.join(content['text']))
                        lines.append("")
            
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def _clean_filename(self, text: str, max_length: int = 50) -> str:
        """Clean text for use in filename."""
        # Remove or replace problematic characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)  # Remove invalid chars
        text = re.sub(r'[^\w\s-]', '', text)  # Keep only alphanumeric, spaces, hyphens
        text = re.sub(r'\s+', '-', text)  # Replace spaces with hyphens
        text = re.sub(r'-+', '-', text)  # Collapse multiple hyphens
        text = text.strip('-')  # Remove leading/trailing hyphens
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length].rstrip('-')
        
        return text or "conversation"
    
    def _generate_output_filename(self, input_path: str) -> str:
        """Generate chronological filename based on first message timestamp."""
        if not self.start_time:
            # Fallback to input filename if no timestamp
            return f"{Path(input_path).stem}-converted.md"
        
        try:
            # Parse timestamp
            dt = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H%M%S")
            
            # Get summary for filename
            summary = ""
            if self.summaries:
                summary = self.summaries[0]
            elif hasattr(self, 'messages') and self.messages:
                # Try to extract from first user message
                for msg in self.messages:
                    if msg['type'] == 'user':
                        content = self._extract_content(msg['message'])
                        if content['text']:
                            first_text = ' '.join(content['text'])[:100]
                            summary = first_text
                            break
            
            if not summary:
                summary = "conversation"
            
            cleaned_summary = self._clean_filename(summary)
            base_filename = f"{date_str}-{time_str}-{cleaned_summary}.md"
            
            return base_filename
            
        except Exception as e:
            print(f"Warning: Could not generate timestamp filename: {e}")
            return f"{Path(input_path).stem}-converted.md"
    
    def convert_file(self, input_path: str, output_dir: str = None, custom_filename: str = None) -> str:
        """Convert a JSONL file to markdown."""
        if output_dir is None:
            output_dir = os.path.dirname(input_path)
        
        # Parse input
        self.parse_jsonl_file(input_path)
        
        # Generate output filename
        if custom_filename:
            output_filename = custom_filename
        else:
            output_filename = self._generate_output_filename(input_path)
        
        # Handle filename conflicts
        output_path = os.path.join(output_dir, output_filename)
        counter = 1
        base_name, ext = os.path.splitext(output_filename)
        while os.path.exists(output_path):
            conflicted_filename = f"{base_name}-{counter:02d}{ext}"
            output_path = os.path.join(output_dir, conflicted_filename)
            counter += 1
        
        # Generate markdown
        markdown_content = self.generate_markdown()
        
        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return output_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python conversation-converter.py input.jsonl [output_dir]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    converter = ConversationConverter()
    
    try:
        output_path = converter.convert_file(input_file, output_dir)
        print(f"Conversion complete: {output_path}")
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()