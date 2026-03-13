import { WorkspaceShell } from "@/components/layout/workspace-shell";

type WorkspaceLayoutProps = Readonly<{
  children: React.ReactNode;
}>;

export default function WorkspaceLayout({ children }: WorkspaceLayoutProps) {
  return <WorkspaceShell>{children}</WorkspaceShell>;
}
