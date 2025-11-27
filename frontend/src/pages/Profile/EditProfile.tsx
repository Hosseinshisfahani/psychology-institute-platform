import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import BirthdayPicker from "../../components/BirthdayPicker";
import { useSnackbar } from "notistack";

interface UserProfile {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  birth_date: string | null;
  phone_number: string;
  gender: string;
  address: string;
  city: string;
  postal_code: string;
}

interface EditProfileFormData {
  first_name: string;
  last_name: string;
  phone_number: string;
  gender: string;
  address: string;
  city: string;
  postal_code: string;
}

export default function EditProfile() {
  const [birthday, setBirthday] = useState<Date | null>(null);
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const { enqueueSnackbar } = useSnackbar();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch
  } = useForm<EditProfileFormData>();

  // Load user profile data
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await fetch("/api/dashboard/user/profile/", {
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
            "Content-Type": "application/json",
          },
        });

        if (response.ok) {
          const data = await response.json();
          setProfile(data);
          
          // Set form values
          setValue("first_name", data.first_name || "");
          setValue("last_name", data.last_name || "");
          setValue("phone_number", data.phone_number || "");
          setValue("gender", data.gender || "");
          setValue("address", data.address || "");
          setValue("city", data.city || "");
          setValue("postal_code", data.postal_code || "");

          // Set birthday if exists
          if (data.birth_date) {
            setBirthday(new Date(data.birth_date));
          }
        }
      } catch (error) {
        console.error("Error loading profile:", error);
        enqueueSnackbar("خطا در بارگذاری اطلاعات پروفایل", { variant: "error" });
      }
    };

    loadProfile();
  }, [setValue, enqueueSnackbar]);

  const onSubmit = async (data: EditProfileFormData) => {
    setLoading(true);
    
    try {
      // Convert Jalali → Gregorian ISO
      const gregorianDate = birthday ? birthday.toISOString().slice(0, 10) : null;

      const response = await fetch("/api/dashboard/user/profile/", {
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...data,
          birth_date: gregorianDate,
        }),
      });

      if (response.ok) {
        enqueueSnackbar("پروفایل با موفقیت بروزرسانی شد", { variant: "success" });
      } else {
        const errorData = await response.json();
        enqueueSnackbar("خطا در بروزرسانی پروفایل", { variant: "error" });
        console.error("Profile update error:", errorData);
      }
    } catch (error) {
      console.error("Error updating profile:", error);
      enqueueSnackbar("خطا در بروزرسانی پروفایل", { variant: "error" });
    } finally {
      setLoading(false);
    }
  };

  if (!profile) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
        ویرایش پروفایل
      </h2>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              نام
            </label>
            <input
              {...register("first_name", { required: "نام الزامی است" })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="نام خود را وارد کنید"
            />
            {errors.first_name && (
              <p className="text-red-500 text-sm mt-1">{errors.first_name.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              نام خانوادگی
            </label>
            <input
              {...register("last_name", { required: "نام خانوادگی الزامی است" })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="نام خانوادگی خود را وارد کنید"
            />
            {errors.last_name && (
              <p className="text-red-500 text-sm mt-1">{errors.last_name.message}</p>
            )}
          </div>
        </div>

        <BirthdayPicker 
          value={birthday} 
          onChange={setBirthday}
          label="تاریخ تولد"
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              شماره تلفن
            </label>
            <input
              {...register("phone_number")}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="شماره تلفن خود را وارد کنید"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              جنسیت
            </label>
            <select
              {...register("gender")}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">انتخاب کنید</option>
              <option value="M">مرد</option>
              <option value="F">زن</option>
              <option value="O">سایر</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            آدرس
          </label>
          <textarea
            {...register("address")}
            rows={3}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="آدرس خود را وارد کنید"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              شهر
            </label>
            <input
              {...register("city")}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="شهر خود را وارد کنید"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              کد پستی
            </label>
            <input
              {...register("postal_code")}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="کد پستی خود را وارد کنید"
            />
          </div>
        </div>

        <div className="flex justify-end space-x-4 pt-4">
          <button
            type="button"
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
            onClick={() => window.history.back()}
          >
            انصراف
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "در حال ذخیره..." : "ذخیره تغییرات"}
          </button>
        </div>
      </form>
    </div>
  );
}
