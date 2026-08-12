// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/JishuaiMIAO/";
    },
  },{id: "nav-blog",
          title: "blog",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/JishuaiMIAO/blog/";
          },
        },{id: "nav-paper-atlas",
          title: "paper atlas",
          description: "A searchable public index of concise computational biology paper summaries.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/JishuaiMIAO/paper-atlas/";
          },
        },{id: "post-capture-tmux-output-for-debugging",
        
          title: "Capture tmux Output for Debugging",
        
        description: "Save tmux scrollback to a file so you can review logs or feed them to an AI tool for debugging.",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/JishuaiMIAO/blog/2026/tmux-debug/";
          
        },
      },{id: "post-run-claude-code-codex-on-a-remote-server-via-ssh-proxy",
        
          title: "Run Claude Code / Codex on a Remote Server via SSH Proxy",
        
        description: "Use SSH RemoteForward to tunnel your local proxy to an HPC cluster, so Claude Code and Codex can reach the internet without direct outbound access.",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/JishuaiMIAO/blog/2026/run-claude-codex/";
          
        },
      },{id: "post-install-claude-code-and-codex-on-itsc-cluster-no-sudo",
        
          title: "Install Claude Code and Codex on ITSC Cluster (No sudo)",
        
        description: "How to install npm via conda and set up Claude Code and Codex on a shared HPC cluster without root access.",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/JishuaiMIAO/blog/2026/install-claude-codex/";
          
        },
      },{id: "post-hello-world",
        
          title: "Hello World",
        
        description: "First post — tools and workflows for machine learning and bioinformatics",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/JishuaiMIAO/blog/2026/hello-world/";
          
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/aqlkzf", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=", "_blank");
        },
      },{
        id: 'social-rss',
        title: 'RSS Feed',
        section: 'Socials',
        handler: () => {
          window.open("/JishuaiMIAO/feed.xml", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
