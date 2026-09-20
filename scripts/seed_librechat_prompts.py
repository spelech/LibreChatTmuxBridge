#!/usr/bin/env python3
"""
Seed LibreChat MongoDB Prompt Library with Tmux Bridge Slash Commands.

This script populates LibreChat's Prompt Library with interactive one-touch
tmux commands, allowing users to type '/' or browse the Prompt Library in LibreChat
to quickly trigger terminal actions (Approve, Reject, Cancel, Tail, Peek, etc.).
"""

import argparse
import json
import subprocess
import sys

TMUX_PROMPTS = [
    {
        "command": "approve",
        "name": "Approve / Confirm",
        "oneliner": "Confirm pending CLI prompt in tmux (sends 'y' + Enter)",
        "prompt": "/approve",
    },
    {
        "command": "reject",
        "name": "Reject / Decline",
        "oneliner": "Decline pending CLI prompt in tmux (sends 'n' + Enter)",
        "prompt": "/reject",
    },
    {
        "command": "cancel",
        "name": "Cancel / Interrupt (SIGINT)",
        "oneliner": "Interrupt running process in tmux (sends Ctrl+C)",
        "prompt": "/cancel",
    },
    {
        "command": "tail",
        "name": "Tail Terminal Output",
        "oneliner": "View latest terminal lines without sending keystrokes",
        "prompt": "/tail 25",
    },
    {
        "command": "peek",
        "name": "Peek Another Session",
        "oneliner": "Inspect another tmux session without switching tabs",
        "prompt": "/peek {{session}} 25",
    },
    {
        "command": "status",
        "name": "Bridge Status",
        "oneliner": "Check LibreChatTmuxBridge daemon health and active sessions",
        "prompt": "/status",
    },
    {
        "command": "list",
        "name": "List Tmux Sessions",
        "oneliner": "List all active host tmux sessions and active windows",
        "prompt": "/list",
    },
    {
        "command": "new",
        "name": "New Session (Bare Shell)",
        "oneliner": "Spawn a bare interactive shell session (no command)",
        "prompt": "/new {{session_name}} {{start_dir}}",
    },
    {
        "command": "agy",
        "name": "Launch Antigravity Agent",
        "oneliner": "Launch Antigravity CLI with --dangerously-skip-permissions",
        "prompt": "/agy {{session_name}} {{start_dir}}",
    },
    {
        "command": "opencode",
        "name": "Launch OpenCode Agent",
        "oneliner": "Launch OpenCode CLI with --dangerously-skip-permissions",
        "prompt": "/opencode {{session_name}} {{start_dir}}",
    },
    {
        "command": "kill",
        "name": "Kill Tmux Session",
        "oneliner": "Terminate an active tmux session",
        "prompt": "/kill {{session_name}}",
    },
    {
        "command": "keys",
        "name": "Send Special Keys",
        "oneliner": "Send special key sequences (e.g. C-c, Escape, Up, Down, Tab)",
        "prompt": "/keys {{key_sequence}}",
    },
    {
        "command": "clear",
        "name": "Clear Terminal Buffer",
        "oneliner": "Send clear command to terminal",
        "prompt": "/clear",
    },
    {
        "command": "up",
        "name": "Repeat Previous Command",
        "oneliner": "Repeat previous shell command (Up arrow + Enter)",
        "prompt": "/up",
    },
    {
        "command": "help",
        "name": "Tmux Help & Commands Guide",
        "oneliner": "Display interactive command cheatsheet",
        "prompt": "/help",
    },
]


def run_mongosh_script(script_str: str) -> str:
    """Execute JavaScript against LibreChat MongoDB container."""
    cmd = ["docker", "exec", "-i", "libre-mongodb", "mongosh", "LibreChat", "--quiet", "--norc"]
    result = subprocess.run(
        cmd,
        input=script_str,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"mongosh failed (code {result.returncode}):\n{result.stderr}")
    return result.stdout.strip()


def seed_prompts(clean: bool = False) -> None:
    """Seed tmux prompt templates into LibreChat MongoDB collections."""
    js_prompts = json.dumps(TMUX_PROMPTS)

    script = f"""
    const promptsData = {js_prompts};
    const cleanOnly = {str(clean).lower()};

    // Find primary user (prefer spelech, fallback to first user)
    let user = db.users.findOne({{ username: 'spelech' }});
    if (!user) {{
        user = db.users.findOne();
    }}
    if (!user) {{
        print(JSON.stringify({{ error: "No user found in LibreChat database." }}));
        quit(1);
    }}

    const userId = user._id;
    const authorName = user.name || user.username || "Admin";

    // Clean up existing Tmux Terminal prompts if cleaning or re-seeding
    const existingGroups = db.promptgroups.find({{ category: 'Tmux Terminal' }}).toArray();
    for (const grp of existingGroups) {{
        db.prompts.deleteMany({{ groupId: grp._id }});
        db.aclentries.deleteMany({{ resourceId: grp._id }});
        db.promptgroups.deleteOne({{ _id: grp._id }});
    }}

    if (cleanOnly) {{
        print(JSON.stringify({{ status: "cleaned", removed: existingGroups.length }}));
        quit(0);
    }}

    let insertedCount = 0;
    for (const item of promptsData) {{
        const groupId = new ObjectId();
        const promptId = new ObjectId();
        const now = new Date();

        const promptDoc = {{
            _id: promptId,
            groupId: groupId,
            author: userId,
            prompt: item.prompt,
            type: 'chat',
            createdAt: now,
            updatedAt: now,
        }};

        const groupDoc = {{
            _id: groupId,
            name: item.name,
            numberOfGenerations: 0,
            oneliner: item.oneliner,
            category: 'Tmux Terminal',
            productionId: promptId,
            author: userId,
            authorName: authorName,
            command: item.command,
            createdAt: now,
            updatedAt: now,
        }};

        const aclOwner = {{
            resourceType: 'promptGroup',
            resourceId: groupId,
            principalType: 'user',
            principalId: userId,
            permBits: 15,
            createdAt: now,
            updatedAt: now,
        }};

        const aclPublic = {{
            resourceType: 'promptGroup',
            resourceId: groupId,
            principalType: 'public',
            permBits: 1,
            createdAt: now,
            updatedAt: now,
        }};

        db.prompts.insertOne(promptDoc);
        db.promptgroups.insertOne(groupDoc);
        db.aclentries.insertOne(aclOwner);
        db.aclentries.insertOne(aclPublic);
        insertedCount++;
    }}

    print("RESULT_JSON:" + JSON.stringify({{
        status: "success",
        inserted: insertedCount,
        user: authorName,
        userId: userId.toString()
    }}));
    """

    output = run_mongosh_script(script)
    json_line = None
    for line in output.splitlines():
        if "RESULT_JSON:" in line:
            json_line = line.split("RESULT_JSON:", 1)[1].strip()
            break
        elif line.strip().startswith("{") and line.strip().endswith("}"):
            json_line = line.strip()

    if not json_line:
        print("Raw output:", output)
        return

    try:
        data = json.loads(json_line)
        if "error" in data:
            print(f"❌ Error: {data['error']}", file=sys.stderr)
            sys.exit(1)
        if clean:
            print(f"🧹 Removed {data.get('removed', 0)} previously seeded Tmux prompts.")
        else:
            print(
                f"✅ Successfully seeded {data.get('inserted', 0)} Tmux slash commands into "
                f"LibreChat Prompt Library for user '{data.get('user')}'."
            )
            print(
                "💡 In LibreChat, click 'Prompt Library' or type '/' to view interactive commands!"
            )
    except json.JSONDecodeError:
        print("Could not parse JSON:", json_line)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed LibreChat Prompt Library with Tmux commands."
    )
    parser.add_argument(
        "--clean", action="store_true", help="Remove seeded tmux prompts without re-adding"
    )
    args = parser.parse_args()
    seed_prompts(clean=args.clean)


if __name__ == "__main__":
    main()
