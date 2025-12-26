import { PropsWithChildren } from "react";
import { motion } from "framer-motion";
import clsx from "clsx";

interface Props extends PropsWithChildren {
  title: string;
  subtitle?: string;
  right?: React.ReactNode;
  className?: string;
}

export default function Section({
  title,
  subtitle,
  right,
  className,
  children,
}: Props) {
  return (
    <motion.section
      className={clsx(
        "glass rounded-2xl p-5 md:p-6 border border-slate-700/40",
        className
      )}
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <h2 className="text-lg font-semibold text-sky-100">{title}</h2>
          {subtitle && (
            <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
          )}
        </div>
        {right}
      </div>
      {children}
    </motion.section>
  );
}
