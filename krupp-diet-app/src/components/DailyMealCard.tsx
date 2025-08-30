"use client";
import clsx from "clsx";

export function DailyMealCard({
  slug,
  title,
  description,
  selected,
  onSelect,
}: {
  slug: string;
  title: string;
  description?: string;
  selected: boolean;
  onSelect: (slug: string) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onSelect(slug)}
      className={clsx(
        "group text-left rounded-2xl border p-4 transition",
        selected
          ? "border-uc-gold bg-uc-gold/10 shadow-md"
          : "border-slate-200 hover:border-uc-navy/50"
      )}
    >
      <div className="flex items-start gap-3">
        <div
          className={clsx(
            "mt-1 h-4 w-4 rounded-full border",
            selected ? "bg-uc-gold border-uc-gold" : "border-slate-300 group-hover:border-uc-navy"
          )}
          aria-hidden
        />
        <div>
          <div className="font-semibold">{title}</div>
          {description ? <p className="text-sm text-black-600 mt-1">{description}</p> : null}
        </div>
      </div>
    </button>
  );
}
