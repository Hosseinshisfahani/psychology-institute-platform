import React from "react";
import DatePicker from "react-multi-date-picker";
import persian from "react-date-object/calendars/persian";
import persian_fa from "react-date-object/locales/persian_fa";

interface BirthdayPickerProps {
  value: Date | null;
  onChange: (date: Date | null) => void;
  label?: string;
  className?: string;
  disabled?: boolean;
}

export default function BirthdayPicker({ 
  value, 
  onChange, 
  label = "تاریخ تولد",
  className = "",
  disabled = false
}: BirthdayPickerProps) {
  const handleDateChange = (dateObject: any) => {
    if (dateObject) {
      // Convert DateObject to JavaScript Date
      const jsDate = dateObject.toDate();
      onChange(jsDate);
    } else {
      onChange(null);
    }
  };

  return (
    <div className={`mb-3 ${className}`}>
      <label className="block mb-2 text-sm font-medium text-gray-700">
        {label}
      </label>
      <DatePicker
        value={value}
        onChange={handleDateChange}
        calendar={persian}
        locale={persian_fa}
        calendarPosition="bottom-right"
        inputClass="border rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        format="YYYY/MM/DD"
        disabled={disabled}
        placeholder="تاریخ تولد خود را انتخاب کنید"
      />
    </div>
  );
}
