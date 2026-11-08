import type { ReactNode } from "react";

interface IconProps {
  name:
    | "dashboard"
    | "scan"
    | "people"
    | "home"
    | "users"
    | "access"
    | "bell"
    | "shield";
  size?: number;
}

const paths: Record<IconProps["name"], ReactNode> = {
  dashboard: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
  scan: <><path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><circle cx="12" cy="11" r="3"/><path d="M7.5 18c.8-2.2 2.3-3.5 4.5-3.5s3.7 1.3 4.5 3.5"/></>,
  people: <><circle cx="9" cy="8" r="3"/><path d="M3.5 19c.6-3.4 2.4-5 5.5-5s4.9 1.6 5.5 5M15 5.4a3 3 0 0 1 0 5.2M16.5 14.3c2.3.5 3.6 2 4 4.7"/></>,
  home: <><path d="m3 11 9-8 9 8"/><path d="M5 9.5V21h14V9.5M9 21v-7h6v7"/></>,
  users: <><circle cx="12" cy="8" r="3.5"/><path d="M5 21c.6-4.3 2.9-6.5 7-6.5s6.4 2.2 7 6.5"/></>,
  access: <><path d="M4 7h13M13 3l4 4-4 4M20 17H7M11 13l-4 4 4 4"/></>,
  bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/></>,
  shield: <><path d="M12 3 5 6v5c0 4.8 2.8 8.1 7 10 4.2-1.9 7-5.2 7-10V6l-7-3Z"/><path d="m9 12 2 2 4-4"/></>,
};

function Icon({ name, size = 20 }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {paths[name]}
    </svg>
  );
}

export default Icon;
