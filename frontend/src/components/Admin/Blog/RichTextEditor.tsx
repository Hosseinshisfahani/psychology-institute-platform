import React, { useMemo } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { Box, FormHelperText } from '@mui/material';

interface RichTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error?: boolean;
  helperText?: string;
  height?: number;
}

const RichTextEditor: React.FC<RichTextEditorProps> = ({
  value,
  onChange,
  placeholder = 'محتوای پست را بنویسید...',
  error = false,
  helperText,
  height = 300,
}) => {
  const modules = useMemo(() => ({
    toolbar: [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      [{ 'align': [] }],
      ['blockquote', 'code-block'],
      ['link', 'image', 'video'],
      ['clean']
    ],
    clipboard: {
      matchVisual: false,
    },
  }), []);

  const formats = [
    'header', 'font', 'size',
    'bold', 'italic', 'underline', 'strike', 'blockquote',
    'list', 'bullet', 'indent',
    'link', 'image', 'video',
    'color', 'background',
    'align', 'code-block'
  ];

  return (
    <Box>
      <Box
        sx={{
          '& .ql-editor': {
            direction: 'rtl',
            textAlign: 'right',
            minHeight: height,
            fontSize: '14px',
            fontFamily: 'Vazir, Arial, sans-serif',
          },
          '& .ql-toolbar': {
            direction: 'rtl',
            borderTop: '1px solid #ccc',
            borderLeft: '1px solid #ccc',
            borderRight: '1px solid #ccc',
            borderTopLeftRadius: '4px',
            borderTopRightRadius: '4px',
          },
          '& .ql-container': {
            borderBottom: '1px solid #ccc',
            borderLeft: '1px solid #ccc',
            borderRight: '1px solid #ccc',
            borderBottomLeftRadius: '4px',
            borderBottomRightRadius: '4px',
          },
          '& .ql-editor.ql-blank::before': {
            content: `"${placeholder}"`,
            fontStyle: 'normal',
            color: '#999',
            direction: 'rtl',
            textAlign: 'right',
          },
        }}
      >
        <ReactQuill
          theme="snow"
          value={value}
          onChange={onChange}
          modules={modules}
          formats={formats}
          placeholder={placeholder}
        />
      </Box>
      {error && helperText && (
        <FormHelperText error={error}>
          {helperText}
        </FormHelperText>
      )}
    </Box>
  );
};

export default RichTextEditor;
