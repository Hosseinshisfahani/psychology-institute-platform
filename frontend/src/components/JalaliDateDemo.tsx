import React, { useState } from "react";
import BirthdayPicker from "./BirthdayPicker";

/**
 * Demo component to showcase Jalali date picker functionality
 * This component demonstrates the conversion between Jalali and Gregorian dates
 */
export default function JalaliDateDemo() {
  const [birthday, setBirthday] = useState<Date | null>(null);
  const [conversionInfo, setConversionInfo] = useState<string>("");

  const handleDateChange = (date: Date | null) => {
    setBirthday(date);
    
    if (date) {
      // Convert Jalali to Gregorian ISO format
      const gregorianDate = date.toISOString().slice(0, 10);
      
      // Show conversion information
      const jalaliDate = date.toLocaleDateString('fa-IR');
      setConversionInfo(`
        تاریخ شمسی: ${jalaliDate}
        تاریخ میلادی: ${gregorianDate}
        فرمت ارسالی به سرور: ${gregorianDate}
      `);
    } else {
      setConversionInfo("");
    }
  };

  const handleSubmit = () => {
    if (birthday) {
      const gregorianDate = birthday.toISOString().slice(0, 10);
      alert(`تاریخ انتخاب شده: ${gregorianDate}\nاین تاریخ به سرور ارسال خواهد شد.`);
    } else {
      alert("لطفاً تاریخ تولد را انتخاب کنید.");
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
        نمایشگر تاریخ شمسی
      </h2>
      
      <div className="space-y-4">
        <BirthdayPicker 
          value={birthday} 
          onChange={handleDateChange}
          label="تاریخ تولد"
        />
        
        {conversionInfo && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <h3 className="text-sm font-medium text-blue-800 mb-2">
              اطلاعات تبدیل تاریخ:
            </h3>
            <pre className="text-xs text-blue-700 whitespace-pre-wrap">
              {conversionInfo}
            </pre>
          </div>
        )}
        
        <div className="flex justify-center">
          <button
            onClick={handleSubmit}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            تست ارسال تاریخ
          </button>
        </div>
        
        <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
          <h3 className="text-sm font-medium text-gray-800 mb-2">
            نکات مهم:
          </h3>
          <ul className="text-xs text-gray-600 space-y-1">
            <li>• کاربر تاریخ شمسی را انتخاب می‌کند</li>
            <li>• سیستم خودکار آن را به میلادی تبدیل می‌کند</li>
            <li>• تاریخ میلادی در دیتابیس ذخیره می‌شود</li>
            <li>• هنگام نمایش، تاریخ شمسی نمایش داده می‌شود</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
