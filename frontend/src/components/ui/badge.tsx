import { cn } from "@/lib/utils";
import { cva, type VariantProps } from "class-variance-authority";

const badgeVariants = cva(
  "inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-semibold tracking-wide uppercase transition-colors",
  {
    variants: {
      variant: {
        default: "border border-border bg-secondary text-secondary-foreground",
        success: "border-success/20 bg-success/10 text-success",
        warning: "border-warning/20 bg-warning/10 text-warning",
        destructive: "border-destructive/20 bg-destructive/10 text-destructive",
        info: "border-info/20 bg-info/10 text-info",
        star: "border-amber-500/20 bg-amber-500/10 text-amber-400",
        cashcow: "border-emerald-500/20 bg-emerald-500/10 text-emerald-400",
        puzzle: "border-violet-500/20 bg-violet-500/10 text-violet-400",
        dog: "border-zinc-500/20 bg-zinc-500/10 text-zinc-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export type BadgeProps = {
  children: React.ReactNode;
  className?: string;
} & VariantProps<typeof badgeVariants>;

export function Badge({ children, variant, className }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant, className }))}>
      {children}
    </span>
  );
}

const menuClassMap: Record<string, BadgeProps["variant"]> = {
  STAR: "star",
  "CASH COW": "cashcow",
  CASH_COW: "cashcow",
  PUZZLE: "puzzle",
  DOG: "dog",
};

export function MenuClassBadge({ value }: { value: string }) {
  return <Badge variant={menuClassMap[value] ?? "default"}>{value}</Badge>;
}

const statusMap: Record<string, BadgeProps["variant"]> = {
  confirmed: "success",
  pending: "warning",
  pending_confirmation: "warning",
  failed: "destructive",
  queued: "info",
  resolved: "success",
  success: "success",
  error: "destructive",
};

export function StatusBadge({ value }: { value: string }) {
  return (
    <Badge variant={statusMap[value.toLowerCase()] ?? "default"}>
      {value.replace(/_/g, " ")}
    </Badge>
  );
}
