"use client";
import React from "react";
import DatePicker from "react-multi-date-picker";
import persian from "react-date-object/calendars/persian";
import fa from "react-date-object/locales/persian_fa";

type Props = {
  value: any;                      // DateObject | null
  onChange: (v: any) => void;
  label?: string;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  minDate?: any;
  maxDate?: any;
};

export default function BirthdayOrDatePicker({
  value,
  onChange,
  label = "تاریخ",
  placeholder = "YYYY/MM/DD",
  className = "",
  disabled = false,
  minDate,
  maxDate
}: Props) {
  return (
    <div className={className}>
      <label className="form-label">{label}</label>
      <DatePicker
        value={value}
        onChange={onChange}
        calendar={persian}
        locale={fa}
        calendarPosition="bottom-right"
        format="YYYY/MM/DD"
        inputClass="form-control"
        disabled={disabled}
        minDate={minDate}
        maxDate={maxDate}
        // IMPORTANT: ASCII digits so backend parsing is easy
        digits={["0","1","2","3","4","5","6","7","8","9"]}
        style={{
          width: '100%',
          direction: 'rtl'
        }}
      />
    </div>
  );
}
