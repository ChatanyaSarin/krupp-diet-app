"use client";
import { useState } from "react";
import clsx from "clsx";

export function MealCard({
  title,
  description,
  onChoose,
}: {
  title: string;
  description?: string;
  onChoose: (liked: boolean) => void;
}) {
  const [choice, setChoice] = useState<null | boolean>(null);

  return (
    <article className={clsx(
      "card p-4 flex flex-col gap-3",
      choice === true && "ring-2 ring-uc-gold",
      choice === false && "ring-2 ring-red-500/60"
    )}>
      <header className="flex items-start justify-between gap-3">
        <h3 className="font-semibold text-white">{title}</h3>
        <span className="text-xs px-2 py-1 rounded-md bg-uc-gold text-uc-blue">
          Suggested
        </span>
      </header>
      {description && (
        <p className="text-sm text-slate-200/90 line-clamp-3">{description}</p>
      )}
      <div className="mt-auto grid grid-cols-2 gap-2">
        <button
          type="button"
          className={clsx(
            "btn w-full",
            choice === true ? "btn-primary" : "btn-outline"
          )}
          onClick={() => { setChoice(true); onChoose(true); }}
        >
          Like
        </button>
        <button
          type="button"
          className={clsx(
            "btn w-full",
            choice === false ? "bg-red-500 text-white hover:bg-red-500/90" : "btn-outline"
          )}
          onClick={() => { setChoice(false); onChoose(false); }}
        >
          Skip
        </button>
      </div>
    </article>
  );
}
