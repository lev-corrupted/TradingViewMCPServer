# MCP Servers Setup Guide for Claude Code

## 🎯 Overview

This guide documents all MCP servers configured for optimal development workflow with Claude Code in VSCode.

**Configuration File**: `~/Library/Application Support/Code/User/settings.json`

---

## ✅ Configured MCP Servers (7 Total)

### 1. **Fetch MCP** 🌐
**Purpose**: Web content fetching and conversion

**What I Can Do:**
- Fetch web pages and convert to markdown
- Extract documentation from websites
- Research APIs and libraries
- Get latest package information

**Use Cases:**
```
"Fetch the latest Python documentation for asyncio"
"Get information from https://example.com"
"Research the TradingView API"
```

**Configuration:**
```json
{
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-fetch"]
}
```

---

### 2. **GitHub MCP** 🐙
**Purpose**: GitHub repository management and operations

**What I Can Do:**
- Search repositories and code
- Read files from any repo
- Create and manage issues
- List PRs and branches
- Get repository information
- Manage releases

**Use Cases:**
```
"Search GitHub for Python trading libraries"
"Get the README from anthropics/mcp-python"
"List issues in my TradingViewMCPServer repo"
"Create a new issue about X"
```

**Configuration:**
```json
{
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
    }
}
```

**Token Permissions:**
- ✅ `repo` - Full repository access
- ✅ `read:org` - Read organization data
- ✅ `gist` - Gist access

---

### 3. **Filesystem MCP** 📁
**Purpose**: Project structure tracking and file operations

**What I Can Do:**
- Navigate project directories
- Read file contents efficiently
- Track project structure
- Search files by patterns
- List directory contents
- Monitor file changes

**Allowed Directories:**
- `/Users/levtheswag/VSCodestuff` (your main projects)
- `/Users/levtheswag/Github Forking` (forked repositories)

**Use Cases:**
```
"Show me the structure of my TradingViewMCPServer project"
"Find all Python files in my project"
"List files in the scrapy directory"
"Read all config files in my project"
```

**Configuration:**
```json
{
    "command": "npx",
    "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/levtheswag/VSCodestuff",
        "/Users/levtheswag/Github Forking"
    ]
}
```

**Benefits:**
- ✅ Efficient directory traversal
- ✅ Fast file searches
- ✅ Structured project overview
- ✅ No need for manual `ls` commands

---

### 4. **Sequential Thinking MCP** 🧠
**Purpose**: Dynamic and reflective problem-solving

**What I Can Do:**
- Break down complex problems step-by-step
- Think through architecture decisions
- Plan multi-step implementations
- Reason about edge cases
- Structured debugging approach

**Use Cases:**
```
"Help me think through how to implement X feature"
"What's the best architecture for Y?"
"Break down this complex problem"
"Debug this issue step by step"
```

**Configuration:**
```json
{
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
}
```

**Benefits:**
- ✅ Structured problem-solving
- ✅ Clear step-by-step reasoning
- ✅ Better architecture decisions
- ✅ Thorough debugging process

---

### 5. **Memory MCP** 💾
**Purpose**: Knowledge graph-based persistent memory

**What I Can Do:**
- Remember context across sessions
- Store project-specific knowledge
- Track decisions and rationale
- Maintain conversation history
- Build knowledge graphs

**Use Cases:**
```
"Remember that we're using Python 3.9+ for this project"
"What did we decide about the architecture?"
"Recall our discussion about Pine Script v6"
"Store this pattern for future reference"
```

**Configuration:**
```json
{
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
}
```

**Benefits:**
- ✅ Context persistence
- ✅ No need to re-explain project structure
- ✅ Tracks decisions and patterns
- ✅ Builds project knowledge over time

---

### 6. **Git MCP** 🔀
**Purpose**: Advanced Git repository operations

**What I Can Do:**
- Read commit history
- Search through commits
- Analyze code changes
- Find when bugs were introduced
- Track file history
- Blame analysis

**Configured Repository:**
- `/Users/levtheswag/VSCodestuff/TradingViewMCPServer`

**Use Cases:**
```
"Show me recent commits"
"When was this function changed?"
"Find the commit that introduced this bug"
"Show me who changed this file"
"Search commits for 'Pine Script'"
```

**Configuration:**
```json
{
    "command": "npx",
    "args": [
        "-y",
        "@modelcontextprotocol/server-git",
        "--repository",
        "/Users/levtheswag/VSCodestuff/TradingViewMCPServer"
    ]
}
```

**Benefits:**
- ✅ Deep git history analysis
- ✅ Code archaeology
- ✅ Bug tracking
- ✅ Understanding code evolution

---

### 7. **SQLite MCP** 🗄️
**Purpose**: Local database operations and queries

**What I Can Do:**
- Query SQLite databases
- Create and manage tables
- Run SQL queries
- Analyze database structure
- Data migrations

**Allowed Directory:**
- `/Users/levtheswag/VSCodestuff` (can access any .db files here)

**Use Cases:**
```
"Query the database at path/to/db.sqlite"
"Show me the schema of this database"
"Run this SQL query: SELECT * FROM..."
"Create a new table for X"
```

**Configuration:**
```json
{
    "command": "npx",
    "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "/Users/levtheswag/VSCodestuff"
    ]
}
```

**Benefits:**
- ✅ Local data analysis
- ✅ Database debugging
- ✅ Quick queries
- ✅ Schema inspection

---

## 🔄 How to Reload Configuration

After updating MCP configuration:

### Option 1: Reload VSCode Window (Recommended)
1. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Reload Window"
3. Press Enter

### Option 2: Restart VSCode
Close and reopen VSCode completely.

---

## 🧪 Testing MCP Servers

After reload, test each server:

### Test All Servers
```
"What MCP servers do you have access to?"
```

Expected response should list:
- `mcp__fetch` (web fetching)
- `mcp__github` (GitHub operations)
- `mcp__filesystem` (file operations)
- `mcp__sequential_thinking` (problem solving)
- `mcp__memory` (persistent memory)
- `mcp__git` (git operations)
- `mcp__sqlite` (database operations)

### Individual Tests

**Fetch:**
```
"Fetch content from https://example.com"
```

**GitHub:**
```
"List my GitHub repositories"
```

**Filesystem:**
```
"Show me the structure of my TradingViewMCPServer"
```

**Sequential Thinking:**
```
"Think through how to implement a new feature step by step"
```

**Memory:**
```
"Remember that this project uses Python 3.9+"
```

**Git:**
```
"Show me recent commits in TradingViewMCPServer"
```

**SQLite:**
```
"List databases in my VSCodestuff folder"
```

---

## 🎯 Development Workflow Benefits

### **Python Development**
- ✅ Fetch Python documentation instantly
- ✅ Search GitHub for Python libraries
- ✅ Track project structure with Filesystem
- ✅ Remember Python patterns with Memory
- ✅ Query local databases with SQLite

### **C# Development**
- ✅ Fetch C# documentation
- ✅ Search GitHub for .NET libraries
- ✅ Track .NET project structure
- ✅ Remember C# patterns

### **General Coding**
- ✅ Sequential Thinking for complex problems
- ✅ Git for code history analysis
- ✅ GitHub for research and collaboration
- ✅ Memory for project-specific knowledge

### **Project Management**
- ✅ Filesystem for structure overview
- ✅ Git for commit tracking
- ✅ GitHub for issue management
- ✅ Memory for decisions and rationale

---

## 🚀 Recommended Usage Patterns

### **Starting a New Feature**
1. **Sequential Thinking**: Plan the feature
2. **Filesystem**: Check current structure
3. **Git**: Review related commits
4. **Memory**: Recall similar patterns
5. **Fetch**: Research if needed
6. **GitHub**: Check for existing solutions

### **Debugging**
1. **Sequential Thinking**: Break down the problem
2. **Git**: Find when bug was introduced
3. **Filesystem**: Navigate to relevant files
4. **Memory**: Recall similar bugs
5. **Fetch**: Research error messages

### **Research**
1. **Fetch**: Get official documentation
2. **GitHub**: Search for examples
3. **Memory**: Store findings
4. **Sequential Thinking**: Evaluate options

---

## 📦 Adding More MCP Servers

### Available Official Servers

To add more servers, edit `settings.json` and add to `claude-code.mcpServers`:

**Brave Search** (Web Search):
```json
"brave-search": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": {
        "BRAVE_API_KEY": "your_key_here"
    }
}
```

**PostgreSQL** (Database):
```json
"postgres": {
    "command": "npx",
    "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user:pass@localhost/db"
    ]
}
```

**Slack** (Team Communication):
```json
"slack": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-slack"],
    "env": {
        "SLACK_BOT_TOKEN": "xoxb-...",
        "SLACK_TEAM_ID": "T..."
    }
}
```

**Google Drive**:
```json
"gdrive": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-gdrive"]
}
```

---

## 🔒 Security Considerations

### API Keys
- ✅ Stored locally in settings.json
- ✅ Only accessible by your user account
- ⚠️ Don't commit settings.json to git
- ⚠️ Disable Settings Sync for sensitive data

### File Access
- ✅ Filesystem MCP restricted to specified directories
- ✅ SQLite MCP restricted to specified directories
- ✅ Git MCP restricted to specified repository

### Best Practices
1. **Use minimal permissions** for API tokens
2. **Restrict directories** to only what's needed
3. **Review token scopes** regularly
4. **Rotate tokens** periodically

---

## 🛠️ Troubleshooting

### MCP Server Not Working

**Problem**: Server doesn't appear after reload

**Solutions:**
1. Check JSON syntax in settings.json (no trailing commas!)
2. Ensure `npx` is installed (`npm install -g npm`)
3. Check VSCode Developer Console (Help → Toggle Developer Tools)
4. Try restarting VSCode completely

### Permission Errors

**Problem**: "Access denied" or permission errors

**Solutions:**
1. Check directory paths are correct
2. Ensure you have read/write permissions
3. For Git MCP, ensure repository path is correct
4. For GitHub MCP, verify token has correct scopes

### Slow Performance

**Problem**: MCP tools are slow to respond

**Solutions:**
1. Reduce number of directories in Filesystem MCP
2. Use more specific Git repository paths
3. Check network connection for Fetch/GitHub MCP
4. Clear npm cache: `npm cache clean --force`

---

## 📊 Current Configuration Summary

```
Total MCP Servers: 7

✅ Fetch         - Web content retrieval
✅ GitHub        - Repository management (with token)
✅ Filesystem    - Project structure (2 directories)
✅ Sequential    - Problem-solving framework
✅ Memory        - Persistent context
✅ Git           - Repository analysis (TradingViewMCPServer)
✅ SQLite        - Local database queries

Allowed Directories:
- /Users/levtheswag/VSCodestuff
- /Users/levtheswag/Github Forking

Git Repository:
- /Users/levtheswag/VSCodestuff/TradingViewMCPServer
```

---

## 🎓 Next Steps

1. **Reload VSCode Window** (Cmd+Shift+P → "Reload Window")
2. **Test All Servers** - Ask: "What MCP servers do you have?"
3. **Try Each Server** - Test with the examples above
4. **Start Using!** - Integrate into your workflow

---

## 📚 Resources

- **Official MCP Servers**: https://github.com/modelcontextprotocol/servers
- **MCP Documentation**: https://modelcontextprotocol.io
- **Claude Code Docs**: https://docs.claude.com/claude-code

---

**Configuration Date**: 2025-01-XX
**Status**: ✅ Ready to Use
**Action Required**: Reload VSCode Window

---

**Happy Coding!** 🚀

With these MCP servers, I can now:
- 🌐 Research anything instantly
- 📁 Navigate your projects efficiently
- 🧠 Think through complex problems systematically
- 💾 Remember context across sessions
- 🔀 Analyze code history deeply
- 🗄️ Query databases on the fly
- 🐙 Manage GitHub seamlessly

You're all set for the ultimate development experience! 🎉
