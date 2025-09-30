# Font Guide - مرکز مشاوره و خدمات روانشناسی سرمد

## Font Selection Rationale

For the Psychology Institute website, we have carefully selected Persian fonts that provide excellent readability, professional appearance, and optimal user experience for Persian/Farsi content.

## Primary Fonts

### 1. **Vazir** (Primary Font)
- **Usage**: Main body text, headings, navigation, buttons
- **Characteristics**: 
  - Modern, clean design
  - Excellent readability in both small and large sizes
  - Professional appearance suitable for academic content
  - Optimized for web use
  - Supports all Persian characters and numerals

### 2. **Samim** (Secondary Font)
- **Usage**: Fallback for Vazir, alternative text elements
- **Characteristics**:
  - Slightly more traditional appearance
  - Good readability
  - Reliable fallback option

### 3. **Shabnam** (Tertiary Font)
- **Usage**: Final fallback option
- **Characteristics**:
  - Clean, modern design
  - Good for both body text and headings
  - Widely supported

## Font Hierarchy

### Display Fonts (Headings)
```css
font-family: 'Vazir', 'Samim', 'Shabnam', 'Tahoma', 'Arial', sans-serif;
font-weight: 700-800;
```

### Body Text
```css
font-family: 'Vazir', 'Samim', 'Shabnam', 'Tahoma', 'Arial', sans-serif;
font-weight: 400-500;
```

### Navigation & UI Elements
```css
font-family: 'Vazir', 'Samim', 'Shabnam', 'Tahoma', 'Arial', sans-serif;
font-weight: 500-600;
```

## Typography Scale

### Headings
- **H1**: 2.5rem (40px) - Page titles
- **H2**: 2rem (32px) - Section titles
- **H3**: 1.75rem (28px) - Subsection titles
- **H4**: 1.5rem (24px) - Card titles
- **H5**: 1.25rem (20px) - Small headings
- **H6**: 1rem (16px) - Labels

### Body Text
- **Base**: 16px - Main content
- **Lead**: 1.1rem (17.6px) - Introductory text
- **Small**: 0.875rem (14px) - Secondary information

### UI Elements
- **Buttons**: 1rem (16px) - Standard buttons
- **Large Buttons**: 1.125rem (18px) - Call-to-action buttons
- **Small Buttons**: 0.875rem (14px) - Compact buttons

## Font Weights

- **400 (Normal)**: Body text, descriptions
- **500 (Medium)**: Navigation links, form labels
- **600 (Semi-bold)**: Card titles, important text
- **700 (Bold)**: Headings, emphasis
- **800 (Extra-bold)**: Brand name, display text

## Line Heights

- **Headings**: 1.4 - Tight spacing for impact
- **Body Text**: 1.8 - Comfortable reading
- **UI Elements**: 1.5 - Balanced spacing
- **Lead Text**: 1.6 - Slightly tighter for emphasis

## Responsive Typography

### Mobile (≤768px)
- Base font size: 15px
- Headings reduced by 0.25rem
- Navigation font: 1.25rem

### Small Mobile (≤576px)
- Base font size: 14px
- Headings reduced by 0.5rem
- Lead text: 1rem

## Special Considerations

### Psychology Content
- **Test Questions**: 1.1rem, weight 500 - Clear and readable
- **Test Choices**: 1rem, weight 400 - Easy to scan
- **Results**: 1.1rem, weight 400 - Professional presentation
- **Interpretations**: 1.1rem, line-height 1.8 - Comfortable reading

### Academic Content
- **Blog Posts**: 1.1rem, line-height 1.8 - Extended reading comfort
- **Course Content**: 1rem, line-height 1.7 - Educational clarity
- **Citations**: 0.9rem, italic - Academic standards

## Browser Support

### Modern Browsers
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

### Fallback Strategy
1. Vazir (primary)
2. Samim (secondary)
3. Shabnam (tertiary)
4. Tahoma (system fallback)
5. Arial (final fallback)
6. sans-serif (generic fallback)

## Performance Optimization

### Font Loading
- Fonts loaded from CDN for better performance
- Font-display: swap for better loading experience
- Preload critical fonts for faster rendering

### File Sizes
- Vazir: ~200KB (all weights)
- Samim: ~150KB (all weights)
- Shabnam: ~100KB (all weights)

## Accessibility

### Screen Readers
- Proper font-family declarations
- Semantic HTML structure
- Adequate contrast ratios

### Visual Accessibility
- Minimum 16px base font size
- 1.8 line height for comfortable reading
- Clear font weight distinctions
- High contrast text colors

## Implementation

### CSS Variables
```css
:root {
    --font-primary: 'Vazir', 'Samim', 'Shabnam', 'Tahoma', 'Arial', sans-serif;
    --font-secondary: 'Samim', 'Vazir', 'Shabnam', 'Tahoma', 'Arial', sans-serif;
    --font-display: 'Vazir', 'Samim', 'Shabnam', 'Tahoma', 'Arial', sans-serif;
}
```

### Usage Examples
```css
/* Body text */
body {
    font-family: var(--font-primary);
    font-size: 16px;
    line-height: 1.8;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-display);
    font-weight: 700;
    line-height: 1.4;
}

/* Buttons */
.btn {
    font-family: var(--font-primary);
    font-weight: 500;
}
```

## Maintenance

### Regular Updates
- Monitor font performance
- Update CDN links when new versions are available
- Test across different devices and browsers
- Ensure accessibility standards are maintained

### Customization
- Font weights can be adjusted based on design needs
- Line heights can be modified for specific content types
- Additional fonts can be added for special use cases

## Best Practices

1. **Consistency**: Use the same font family across similar elements
2. **Hierarchy**: Maintain clear visual hierarchy with font sizes and weights
3. **Readability**: Ensure adequate contrast and spacing
4. **Performance**: Monitor font loading times
5. **Accessibility**: Test with screen readers and assistive technologies
6. **Responsive**: Ensure fonts work well on all device sizes

This font system provides a professional, readable, and accessible typography foundation for the Psychology Institute website, ensuring optimal user experience across all devices and browsers.
