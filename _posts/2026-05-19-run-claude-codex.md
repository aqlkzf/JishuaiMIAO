---
layout: post
title: "Run Claude Code / Codex on Remote Server via SSH Proxy"
date: 2026-05-19
description: "Use SSH RemoteForward to share your local proxy with an HPC cluster so Claude Code and Codex can reach the internet."
tags: tools hpc ssh
categories:
related_posts: false
---

> Use SSH RemoteForward to share your local proxy with the remote server, so Claude Code and Codex can access the internet through VS Code Remote SSH.

## Prerequisites

| Item | Details |
|------|---------|
| **Local proxy** | A proxy running on your local machine (e.g. Clash), note down the port (default: `7890`) |
| **VS Code + Remote SSH** | Already connected to the remote server |
| **Claude Code / Codex installed** | Installed on the remote server (see [Install Guide]({% post_url 2026-05-19-install-claude-codex %})) |

## 1. Add RemoteForward to SSH Config

Open your local SSH config file (`~/.ssh/config`). In VS Code you can open it via **Remote Explorer → gear icon**.

Add `RemoteForward 7890 127.0.0.1:7890` to every `Host` block you want proxy on:

```
Host chpc-login
    HostName chpc-login.itsc.cuhk.edu.hk
    User YOUR_COMPUTING_ID
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ControlMaster auto
    ControlPersist 10m
    RemoteForward 7890 127.0.0.1:7890   # ← add this line

Host chpc-gpu0?? chpc-gpu0??.rc.cuhk.edu.hk
    HostName %h.rc.cuhk.edu.hk
    User YOUR_COMPUTING_ID
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ProxyJump chpc-login
    RemoteForward 7890 127.0.0.1:7890   # ← add this line

Host chpc-cn??? chpc-cn???.rc.cuhk.edu.hk
    HostName %h.rc.cuhk.edu.hk
    User YOUR_COMPUTING_ID
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ProxyJump chpc-login
    RemoteForward 7890 127.0.0.1:7890   # ← add this line
```

> **Note:** The port `7890` should match your local proxy port. Check in Clash → Settings → Mixed Port.

With `ProxyJump`, you can connect directly to a compute node (e.g. `chpc-gpu010`, `chpc-cn101`) from VS Code and the proxy works end-to-end.

## 2. Set Proxy Environment Variables

Add the following to your remote server's shell config:

**Bash / Zsh** (`~/.bashrc` or `~/.zshrc`):

```bash
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
export ALL_PROXY="socks5://127.0.0.1:7890"
```

Reload the config or open a new terminal for the changes to take effect.

## 3. Verify

After reconnecting via VS Code Remote SSH:

```bash
curl -x http://127.0.0.1:7890 https://api.anthropic.com
```

If you get a response (not a timeout), the proxy is working. Claude Code and Codex should now function normally on the remote server.

## FAQ

| Question | Answer |
|----------|--------|
| **Connection refused on port 7890** | Make sure your local proxy (Clash) is running and the port matches. Verify the `RemoteForward` line is under the correct `Host` block. |
| **Proxy set but CLI tools don't use it** | Reload your shell config (`source ~/.bashrc`) or open a new terminal. |
| **Need a different port** | Replace all `7890` with your actual proxy port in both SSH config and shell config. |
