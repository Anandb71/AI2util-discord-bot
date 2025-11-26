# AI Agent Bot Summary

## 🤖 Core Functionality
This is a **Self-Coding AI Agent** for Discord. It allows the owner to control the bot and the server using natural language commands. The bot dynamically generates Python code using Google's Gemini AI and executes it in real-time.

### **Prefix & Commands**
*   **Prefix:** `>` 
*   **Slash Commands:** Supported (via `app_commands`)

### **Commands List**
| Command | Type | Permissions | Description |
| :--- | :--- | :--- | :--- |
| `>exec <request>` | Prefix | **Owner Only** | The core command. Sends your natural language request to Gemini, generates `discord.py` code, and executes it after confirmation. |
| `/ping` | Slash/Prefix | Public | Checks the bot's latency (ping). |
| `/help` | Slash/Prefix | Public | Displays the list of available commands. |
| `>sync` | Prefix | **Owner Only** | Syncs slash commands with Discord's servers. |

---

## ⚙️ Configuration & IDs
The bot relies on environment variables for configuration. It does **not** have hardcoded IDs in the source code, making it secure and portable.

### **Environment Variables (`.env`)**
| Variable | Description | Source |
| :--- | :--- | :--- |
| `BOT_TOKEN` | The Discord Bot Token used to login. | Loaded from `.env` |
| `GEMINI_API_KEY` | API Key for Google Gemini AI. | Loaded from `.env` |
| `OWNER_ID` | The Discord User ID of the bot owner. | Loaded from `.env` (Defaults to `0` if missing) |

### **Hardcoded Details**
*   **AI Model:** `gemini-2.0-flash-exp` (Hardcoded in `main.py`)
*   **Embed Colors:**
    *   Standard: Blue (`0x3498DB`)
    *   Thinking: Purple (`0x9B59B6`)
    *   Confirm: Orange (`0xFFA500`)
    *   Success: Green (`0x00FF00`)
    *   Error: Red (`0xFF0000`)

---

## 🧠 AI Agent Logic (`>exec`)
1.  **Context Gathering:** When you run `>exec`, the bot captures:
    *   Server Name & ID
    *   Current Channel Name & ID
    *   Author Name & ID
    *   List of first 20 Channels (Names, IDs, Types)
    *   List of first 20 Roles (Names, IDs)
2.  **Prompt Engineering:** It sends this context to Gemini with strict instructions to generate **only** executable Python code using the `discord.py` library.
3.  **Safety Checks:**
    *   **Owner Check:** Only the user with `OWNER_ID` can trigger it.
    *   **Confirmation:** You must react with ✅ to run the code.
    *   **Code Scanning:** It blocks execution if the code contains dangerous terms: `os.environ`, `open(`, `read(`, `write(`, `token`, `api_key`, `sys.modules`, `eval(`, `exec(`.
    *   **File System Lock:** The system prompt explicitly forbids file access.

## 🔒 Security
*   **Restricted Access:** The dangerous `exec` capability is strictly locked to the `OWNER_ID`.
*   **No File Access:** The bot is designed to operate *on Discord* (channels, roles, messages) and is prevented from reading/writing local files on the host machine.
