'use client';
import React, { useEffect, useMemo, useState } from 'react';
import {
  Box, Stack, IconButton, Button, Typography, Paper
} from '@mui/material';
import { ChevronRight, ChevronLeft } from '@mui/icons-material';

type FetchAvailability = (isoDate: string) => Promise<{ booked: string[] }>;

const faDigits = (s: string) => s.replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[+d]);
const fmt = (date: Date, opt: Intl.DateTimeFormatOptions) =>
  new Intl.DateTimeFormat('fa-IR-u-ca-persian', opt).format(date);
const addDays = (d: Date, n: number) => {
  const x = new Date(d); x.setDate(x.getDate() + n); return x;
};

const buildSlots = (startHour=9, endHour=21, step=30) => {
  const out: { label: string; value: string }[] = [];
  for (let h = startHour; h <= endHour; h++) {
    for (let m = 0; m < 60; m += step) {
      if (h === endHour && m > 0) break;
      const hh = String(h).padStart(2, '0');
      const mm = String(m).padStart(2, '0');
      out.push({ value: `${hh}:${mm}`, label: faDigits(`${h}:${mm}`) });
    }
  }
  return out;
};

type Props = {
  visibleDays?: number;   // per page
  pageSize?: number;      // how many days to move with arrows
  startHour?: number; endHour?: number; stepMinutes?: number;
  guardMinutesForToday?: number;    // minutes ahead to block on "today"
  fetchAvailability: FetchAvailability;
  onConfirm?: (payload: { date: string; time: string }) => void;
  onTimeChange?: (time: string | null) => void; // NEW
  initialISODate?: string | null;
  initialTime?: string | null;
};

export default function BookingTimeSelectorMUI({
  visibleDays = 7,
  pageSize = 7,
  startHour = 9,
  endHour = 21,
  stepMinutes = 30,
  guardMinutesForToday = 60,
  fetchAvailability,
  onConfirm,
  onTimeChange,
  initialISODate = null,
  initialTime = null,
}: Props) {
  const [cursor, setCursor] = useState(0);
  const [selectedISODate, setSelectedISODate] = useState<string | null>(initialISODate);
  const [selectedTime, setSelectedTime] = useState<string | null>(initialTime);
  const [booked, setBooked] = useState<string[]>([]);
  const slots = useMemo(() => buildSlots(startHour, endHour, stepMinutes), [startHour, endHour, stepMinutes]);

  const days = useMemo(() => {
    const base = new Date();
    return Array.from({ length: visibleDays }, (_, i) => addDays(base, i + cursor));
  }, [visibleDays, cursor]);

  // (A) Fetch availability when selected date changes - with cleanup to prevent race conditions
  useEffect(() => {
    if (!selectedISODate) return;
    console.log('availability fetch for', selectedISODate); // Debug: should log once per date change
    let mounted = true;
    fetchAvailability(selectedISODate)
      .then((r) => {
        if (mounted) {
          const bookedTimes = r.booked ?? [];
          console.log('Setting booked times:', bookedTimes);
          setBooked(bookedTimes);
        }
      })
      .catch((error) => {
        console.error('Error in availability fetch:', error);
        if (mounted) setBooked([]);
      });
    return () => { mounted = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedISODate, fetchAvailability]); // Include fetchAvailability to refetch when dependencies change

  // (B) Pick first visible day once when no date is selected
  useEffect(() => {
    if (!selectedISODate && days[0]) {
      setSelectedISODate(days[0].toISOString().slice(0,10));
    }
  }, [days, selectedISODate]);

  // (C) Sync with parent-provided initialISODate without bouncing
  useEffect(() => {
    if (initialISODate && initialISODate !== selectedISODate) {
      setSelectedISODate(initialISODate);
      setSelectedTime(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialISODate]);

  const now = new Date();
  const isToday = selectedISODate
    ? new Date(selectedISODate).toDateString() === new Date(now.getFullYear(), now.getMonth(), now.getDate()).toDateString()
    : false;
  const cutoff = new Date(now.getTime() + guardMinutesForToday * 60000);

  const isDisabledSlot = (value: string) => {
    if (!selectedISODate) return true;
    // Check if this time slot is in the booked/unavailable list
    // Normalize the value to ensure format matches (HH:MM with 2-digit hours)
    const normalizeTime = (timeStr: string): string => {
      const [h, m] = timeStr.split(':').map(Number);
      return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
    };
    const normalizedValue = normalizeTime(value);
    const normalizedBooked = booked.map(normalizeTime);
    const isBooked = normalizedBooked.includes(normalizedValue);
    if (isBooked) {
      console.log('Time slot', value, 'normalized to', normalizedValue, 'is disabled (booked/unavailable). Booked times:', normalizedBooked);
      return true;
    }
    // For today, also check if time is too soon
    if (!isToday) return false;
    const [hh, mm] = value.split(':').map(Number);
    const candidate = new Date(cutoff.getFullYear(), cutoff.getMonth(), cutoff.getDate(), hh, mm, 0);
    return candidate < cutoff;
  };

  return (
    <Box>
      {/* Day carousel header - matching image design */}
      <Stack direction="row" alignItems="center" gap={1} mb={3}>
        <IconButton 
          aria-label="Previous days" 
          onClick={() => setCursor(Math.max(0, cursor - pageSize))}
          sx={{ 
            bgcolor: 'grey.100', 
            '&:hover': { bgcolor: 'grey.200' },
            borderRadius: 2
          }}
        >
          <ChevronRight />
        </IconButton>

        <Stack direction="row" gap={1.5} sx={{ overflowX: 'auto', py: 1, flex: 1 }}>
          {days.map((d) => {
            const iso = d.toISOString().slice(0,10);
            const selected = selectedISODate === iso;
            const weekday = fmt(d, { weekday: 'long' });
            const dayNum = fmt(d, { day: 'numeric' });
            const month = fmt(d, { month: 'long' });

            // Calculate available count for this specific date
            const availableCount = slots.filter(s => {
              if (!selectedISODate) return false;
              const isTodayForThisDate = new Date(iso).toDateString() === new Date(now.getFullYear(), now.getMonth(), now.getDate()).toDateString();
              if (isTodayForThisDate) {
                const [hh, mm] = s.value.split(':').map(Number);
                const candidate = new Date(cutoff.getFullYear(), cutoff.getMonth(), cutoff.getDate(), hh, mm, 0);
                return candidate >= cutoff && !booked.includes(s.value);
              }
              return !booked.includes(s.value);
            }).length;

            return (
              <Paper
                key={iso}
                variant="outlined"
                onClick={() => { setSelectedISODate(iso); setSelectedTime(null); }}
                sx={{
                  minWidth: 120, 
                  px: 2, 
                  py: 1.5, 
                  cursor: 'pointer',
                  borderRadius: 3,
                  border: selected ? '2px solid' : '1px solid',
                  borderColor: selected ? '#4caf50' : 'divider',
                  bgcolor: selected ? '#4caf50' : 'white',
                  color: selected ? 'white' : 'text.primary',
                  boxShadow: selected ? '0 0 0 3px rgba(76, 175, 80, 0.12)' : 'none',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: '#4caf50',
                    boxShadow: '0 2px 8px rgba(76, 175, 80, 0.2)'
                  }
                }}
              >
                <Typography variant="body2" sx={{ fontSize: '0.75rem', opacity: 0.8 }}>
                  {weekday}
                </Typography>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, fontSize: '0.9rem' }}>
                  {dayNum} <Typography component="span" variant="subtitle2" sx={{ fontSize: '0.8rem', opacity: 0.8 }}>{month}</Typography>
                </Typography>
                <Typography variant="caption" sx={{ 
                  color: selected ? 'white' : '#4caf50',
                  fontSize: '0.7rem',
                  fontWeight: 500
                }}>
                  {faDigits(String(availableCount))} نوبت
                </Typography>
              </Paper>
            );
          })}
        </Stack>

        <IconButton 
          aria-label="Next days" 
          onClick={() => setCursor(cursor + pageSize)}
          sx={{ 
            bgcolor: 'grey.100', 
            '&:hover': { bgcolor: 'grey.200' },
            borderRadius: 2
          }}
        >
          <ChevronLeft />
        </IconButton>
      </Stack>

      {/* Time grid - matching image design */}
      <Box display="grid" gridTemplateColumns={{ xs: 'repeat(3, 1fr)', sm: 'repeat(4, 1fr)', md: 'repeat(6, 1fr)', lg: 'repeat(8, 1fr)' }} gap={1.5}>
        {slots.map((slot) => {
          const disabled = isDisabledSlot(slot.value);
          const selected = selectedTime === slot.value;
          return (
            <Button
              key={slot.value}
              fullWidth
              variant="outlined"
              color="success"
              disabled={disabled}
              onClick={() => {
                if (disabled) return;
                setSelectedTime(slot.value);
                onTimeChange?.(slot.value); // lift to parent
              }}
              sx={{
                borderRadius: 3,
                textTransform: 'none',
                fontSize: 14,
                py: 1,
                borderColor: selected ? '#4caf50' : '#4caf50',
                bgcolor: selected ? '#4caf50' : 'white',
                color: selected ? 'white' : '#4caf50',
                '&:hover': {
                  borderColor: '#4caf50',
                  bgcolor: selected ? '#4caf50' : 'rgba(76, 175, 80, 0.1)'
                },
                '&:disabled': {
                  borderColor: 'grey.300',
                  color: 'grey.400',
                  bgcolor: 'grey.50'
                }
              }}
            >
              {slot.label}
            </Button>
          );
        })}
      </Box>

      {/* Action */}
      <Stack direction="row" gap={2} mt={3}>
        <Button
          fullWidth
          variant="contained"
          disabled={!selectedISODate || !selectedTime}
          onClick={() => selectedISODate && selectedTime && onConfirm?.({ date: selectedISODate, time: selectedTime })}
          sx={{ 
            py: 1.25, 
            borderRadius: 2,
            bgcolor: '#4caf50',
            '&:hover': { bgcolor: '#45a049' },
            '&:disabled': { bgcolor: 'grey.300' }
          }}
        >
          تایید نوبت
        </Button>
      </Stack>
    </Box>
  );
}
