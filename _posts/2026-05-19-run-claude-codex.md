---
layout: post
title: "Run Claude Code / Codex on a Remote Server via SSH Proxy"
date: 2026-05-19
description: "Use SSH RemoteForward to tunnel your local proxy to an HPC cluster, so Claude Code and Codex can reach the internet without direct outbound access."
tags: tools hpc ssh
categories:
related_posts: false
---

HPC clusters can't reach `openai.com` or `claude.ai`, and without `sudo` we can't install a VPN on the cluster. The workaround: tunnel your **local** proxy (e.g. Clash) to the remote server over SSH with `RemoteForward`, so Claude Code and Codex can phone home with no firewall changes on either side.

## Prerequisites

| Item | Details |
|------|---------|
| **Local proxy** | Running on your local machine (e.g. Clash); note the port (default: `7890`) |
| **VS Code + Remote SSH** | Connected to the remote server — see the [VS Code Remote SSH Guide](https://doc.sta.cuhk.edu.hk/vs-code-remote-ssh-guide) if not yet set up |
| **Claude Code / Codex** | Installed on the remote server — see [Install Claude Code & Codex on ITSC Cluster]({% post_url 2026-05-19-install-claude-codex %}) |

## 1. Add RemoteForward to Your SSH Config

Open `~/.ssh/config` on your **local** machine. In VS Code you can reach it via **Remote Explorer → gear icon**.

Add `RemoteForward 7890 127.0.0.1:7890` to every `Host` block where you want the proxy:

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

> **Note:** `7890` must match your local proxy's mixed port. In Clash, check **Settings → Mixed Port**.

`RemoteForward` makes port `7890` on the remote machine forward traffic back to `127.0.0.1:7890` on your laptop. Combined with `ProxyJump`, this works transparently even when you connect directly to a compute node (`chpc-gpu010`, `chpc-cn101`, etc.) — the forward is re-established along the jump chain, so the proxy is reachable on every hop.

## 2. Export Proxy Variables on the Remote Server

For **bash** or **zsh**, append to `~/.bashrc` / `~/.zshrc`:

```bash
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
export ALL_PROXY="socks5://127.0.0.1:7890"
```

Reload the config (`source ~/.bashrc`, etc.) or open a fresh terminal.

## 3. Verify

Reconnect to the server via VS Code Remote SSH, then run:

```bash
curl -x http://127.0.0.1:7890 https://api.anthropic.com
```

Any response — even an HTTP error body — means the tunnel is alive. Claude Code and Codex can now reach the internet.

## FAQ

| Question | Answer |
|----------|--------|
| **Connection refused on port 7890** | Check that your local proxy is running and the port matches. Also confirm `RemoteForward` is under the correct `Host` block. |
| **Proxy variables set but tools still fail** | Reload your shell config or open a new terminal — the variables only take effect in new shells. |
| **Using a different port** | Replace every `7890` with your actual proxy port in both the SSH config and the shell config. |
