"use client";

import { clsx } from "clsx";
import { motion } from "framer-motion";
import { forwardRef } from "react";
import type { ButtonHTMLAttributes, ForwardedRef } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>((props: ButtonProps, ref: ForwardedRef<HTMLButtonElement>) => {
  const { className, variant = "primary", children, ...rest } = props;
    const base =
      "rounded-full px-5 py-2 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/80";
    const variants: Record<ButtonVariant, string> = {
      primary: "bg-brand text-white shadow-glow",
      secondary: "bg-slate-800 text-slate-100 border border-slate-700",
      ghost: "text-slate-200 hover:bg-slate-800/60"
    } as const;
    const variantClass = variants[variant];

    return (
      <motion.button
        ref={ref}
        whileTap={{ scale: 0.97 }}
        className={clsx(base, variantClass, className)}
        {...rest}
      >
        {children}
      </motion.button>
    );
});

Button.displayName = "Button";
