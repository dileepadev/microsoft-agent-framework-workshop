export interface NavItem {
  title: string;
  href: string;
  icon?: string;
  badge?: string;
}

export interface NavSection {
  title: string;
  icon?: string;
  items: NavItem[];
}

export type NavEntry = NavItem | NavSection;

export function isSection(entry: NavEntry): entry is NavSection {
  return "items" in entry;
}

export const navigation: NavEntry[] = [
  { title: "Introduction", href: "/introduction", icon: "📖" },
  { title: "About OpsAgent", href: "/opsagent", icon: "🤖" },
  {
    title: "Workshop Modules",
    icon: "🧪",
    items: [
      {
        title: "Environment Setup",
        href: "/getting-started/1-environment-setup",
        badge: "01",
      },
      {
        title: "GitHub Models",
        href: "/getting-started/2-github-models-connection",
        badge: "02",
      },
      {
        title: "Agent Framework",
        href: "/getting-started/3-microsoft-agent-framework-agents",
        badge: "03",
      },
      {
        title: "Tool Calling",
        href: "/getting-started/4-tool-calling",
        badge: "04",
      },
      {
        title: "MCP Integration",
        href: "/getting-started/5-mcp-integration",
        badge: "05",
      },
      {
        title: "Multi-turn Conversations",
        href: "/getting-started/6-multi-turn-conversations",
        badge: "06",
      },
      {
        title: "Memory & Persistence",
        href: "/getting-started/7-memory-and-persistence",
        badge: "07",
      },
      { title: "Workflows", href: "/getting-started/8-workflows", badge: "08" },
      {
        title: "Chat User Interface",
        href: "/getting-started/9-chat-user-interface",
        badge: "09",
      },
      {
        title: "Host Agent",
        href: "/getting-started/10-host-agent",
        badge: "10",
      },
    ],
  },
  { title: "Conclusion", href: "/conclusion", icon: "🎓" },
];

/** Flat ordered list of all doc pages for prev/next navigation */
export const flatNav: NavItem[] = navigation.flatMap((entry) =>
  isSection(entry) ? entry.items : [entry],
);
