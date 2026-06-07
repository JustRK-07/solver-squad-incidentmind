import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const alertVariants = cva(
  "rounded-lg border-hairline px-2.5 py-2 text-[13px] mb-2.5",
  {
    variants: {
      variant: {
        default: "bg-surface text-text border-border",
        warning: "bg-warning-bg text-warning-fg border-warning-fg",
        danger:  "bg-danger-bg text-danger-fg border-danger-fg",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface AlertProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> {}

export function Alert({ className, variant, ...props }: AlertProps) {
  return (
    <div
      role="alert"
      className={cn(alertVariants({ variant }), className)}
      {...props}
    />
  );
}
