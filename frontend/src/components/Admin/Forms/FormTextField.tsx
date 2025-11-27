import React from 'react';
import { TextField, TextFieldProps } from '@mui/material';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';

interface FormTextFieldProps<T extends FieldValues> extends Omit<TextFieldProps, 'name'> {
  name: Path<T>;
  control: Control<T>;
  label: string;
}

function FormTextField<T extends FieldValues>({
  name,
  control,
  label,
  ...textFieldProps
}: FormTextFieldProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState: { error } }) => (
        <TextField
          {...field}
          {...textFieldProps}
          label={label}
          error={!!error}
          helperText={error?.message}
          fullWidth
          variant="outlined"
        />
      )}
    />
  );
}

export default FormTextField;

