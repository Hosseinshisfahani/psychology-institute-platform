"use client";
import React, { useMemo } from "react";

type Slot = {
  label: string;       // e.g. "۱۰:۳۰"
  value: string;       // "10:30"
  disabled?: boolean;
};

type Props = {
  /** ISO date from your form (YYYY-MM-DD). If null, whole picker is disabled */
  isoDate: string | null;
  /** currently selected time, e.g. "10:30" */
  value: string | null;
  /** called when user selects a time */
  onChange: (value: string | null) => void;

  /** business hours & cadence */
  startHour?: number;     // default 9
  endHour?: number;       // default 18
  stepMinutes?: number;   // default 30

  /** already booked times (ISO time "HH:MM") returned by API for the selected date */
  booked?: string[];

  /** minutes to block for "now" if selected date is today (e.g., 60 => next hour) */
  guardMinutesForToday?: number;
};

/** Convert "10:30" -> Persian "۱۰:۳۰" for display only */
const toFaDigits = (s: string) =>
  s.replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[+d]);

/** Build time slots between startHour..endHour with stepMinutes */
function buildSlots(startHour: number, endHour: number, step: number): Slot[] {
  const slots: Slot[] = [];
  for (let h = startHour; h < endHour; h++) {
    for (let m = 0; m < 60; m += step) {
      const hh = String(h).padStart(2, "0");
      const mm = String(m).padStart(2, "0");
      const value = `${hh}:${mm}`;
      const label = toFaDigits(`${h}:${mm === "00" ? "00" : mm}`);
      slots.push({ label, value });
    }
  }
  return slots;
}

export default function TimeSlotPicker({
  isoDate,
  value,
  onChange,
  startHour = 9,
  endHour = 18,
  stepMinutes = 30,
  booked = [],
  guardMinutesForToday = 60,
}: Props) {
  const allSlots = useMemo(
    () => buildSlots(startHour, endHour, stepMinutes),
    [startHour, endHour, stepMinutes]
  );

  // split to morning/afternoon (for tabs)
  const morning = allSlots.filter((s) => +s.value.split(":")[0] < 12);
  const afternoon = allSlots.filter((s) => +s.value.split(":")[0] >= 12);

  // compute disabled states (booked + "past" if today)
  const now = new Date();
  const isToday =
    isoDate &&
    new Date(isoDate).toDateString() ===
      new Date(now.getFullYear(), now.getMonth(), now.getDate()).toDateString();

  const cutoff = new Date(now.getTime() + guardMinutesForToday * 60000);
  const disabledSet = new Set(booked); // e.g. ["10:30","11:00"]

  function isDisabled(slot: Slot) {
    if (!isoDate) return true;
    if (disabledSet.has(slot.value)) return true;
    if (!isToday) return false;
    // compare with cutoff if today
    const [hh, mm] = slot.value.split(":").map(Number);
    const slotDate = new Date(
      cutoff.getFullYear(),
      cutoff.getMonth(),
      cutoff.getDate(),
      hh,
      mm,
      0
    );
    return slotDate < cutoff;
  }

  // simple local tab state
  const [tab, setTab] = React.useState<"am" | "pm">("am");

  return (
    <fieldset
      className="w-full time-slot-picker"
      aria-labelledby="timeslot-label"
      dir="rtl"
      disabled={!isoDate}
    >
      <div id="timeslot-label" className="mb-2 text-sm text-gray-700">
        انتخاب زمان
      </div>

      {/* Tabs */}
      <div className="mb-3 inline-flex rounded-xl bg-gray-100 p-1">
        <button
          type="button"
          className={`px-3 py-1.5 text-sm rounded-lg ${
            tab === "am" ? "bg-white shadow" : "text-gray-600"
          }`}
          onClick={() => setTab("am")}
          aria-pressed={tab === "am"}
        >
          صبح
        </button>
        <button
          type="button"
          className={`px-3 py-1.5 text-sm rounded-lg ${
            tab === "pm" ? "bg-white shadow" : "text-gray-600"
          }`}
          onClick={() => setTab("pm")}
          aria-pressed={tab === "pm"}
        >
          عصر
        </button>
      </div>

      {/* Slots grid */}
      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
        {(tab === "am" ? morning : afternoon).map((slot) => {
          const disabled = isDisabled(slot);
          const selected = value === slot.value;
          return (
            <button
              key={slot.value}
              type="button"
              className={[
                "px-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition",
                selected
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-800 border-gray-300 hover:border-blue-400",
                disabled ? "opacity-40 cursor-not-allowed hover:border-gray-300" : "",
              ].join(" ")}
              aria-pressed={selected}
              aria-disabled={disabled}
              disabled={disabled}
              onClick={() => onChange(disabled ? null : slot.value)}
            >
              {slot.label}
            </button>
          );
        })}
      </div>

      {/* helper text */}
      {!isoDate && (
        <p className="mt-2 text-xs text-amber-600">
          ابتدا تاریخ را انتخاب کنید، سپس زمان‌های آزاد نمایش داده می‌شود.
        </p>
      )}
    </fieldset>
  );
}
