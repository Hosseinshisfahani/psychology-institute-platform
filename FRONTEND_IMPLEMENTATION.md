# Frontend Implementation - Workshops and Packages

## Overview
Complete React/TypeScript frontend implementation for workshops and packages features with modern UI using React Bootstrap.

## Created Components

### 1. Workshops Components

#### `frontend/src/pages/Workshops/Workshops.tsx`
**Workshop Listing Page**
- Displays all available workshops in a card grid
- Features:
  - Category and difficulty filters
  - Real-time filtering using React Query
  - Displays workshop cards with:
    - Thumbnail image
    - Category and difficulty badges
    - Instructor name
    - Start date (Persian calendar)
    - Total hours
    - Available seats
    - Payment type indicator
    - Price with discount
  - Hover effects for better UX
  - Empty state handling
  - Loading spinner

#### `frontend/src/pages/Workshops/WorkshopDetail.tsx`
**Workshop Detail Page**
- Comprehensive workshop information
- Features:
  - Hero section with thumbnail
  - Workshop metadata (instructor, participants, rating)
  - Registration status badge
  - Tabbed interface:
    - Description tab with prerequisites and learning objectives
    - Sessions tab listing all workshop sessions with schedule
  - Sticky sidebar with:
    - Price display
    - Key information (start date, duration, capacity, payment type)
    - Registration deadline countdown
    - Registration button
  - Registration modal for payment type selection:
    - Full payment option
    - Installment payment option with breakdown
  - Integration with authentication
  - Responsive design

#### `frontend/src/pages/Workshops/WorkshopSession.tsx`
**Workshop Session Access Page**
- Live session and recording access
- Features:
  - Session header with metadata
  - Attendance tracking
  - Live session section:
    - Meeting link for active sessions
    - Join button with Croom integration
    - Automatic attendance marking
  - Recording section:
    - Video player with controls
    - Download protection (`controlsList="nodownload"`)
    - Right-click prevention
    - Warning about download restrictions
  - Waiting state for upcoming sessions
  - Attendance information display
  - Auto-refresh functionality

### 2. Packages Components

#### `frontend/src/pages/Packages/Packages.tsx`
**Package Listing Page**
- Displays educational package bundles
- Features:
  - Category filter
  - Featured packages filter
  - Package cards showing:
    - Thumbnail image
    - Category and featured badges
    - Number of courses
    - Total hours
    - Duration (months)
    - Purchase count
    - Star rating
    - Savings percentage and amount
  - Price display with discounts
  - Responsive grid layout
  - Loading and empty states

#### `frontend/src/pages/Packages/PackageDetail.tsx`
**Package Detail Page**
- Complete package information
- Features:
  - Hero section with thumbnail
  - Package metadata and statistics
  - Purchase status indicator
  - Savings highlight alert
  - Tabbed interface:
    - Description tab
    - Courses tab with individual course cards
  - Sticky sidebar with:
    - Price with discount
    - Savings calculation
    - Key information (courses, hours, duration, original price)
    - Purchase button
    - Add to cart button
  - Course cards in grid:
    - Difficulty badge
    - Instructor name
    - Duration
  - Protected purchase flow
  - Responsive design

### 3. Dashboard Components

#### `frontend/src/pages/Dashboard/FinancialReport.tsx`
**Financial Report Page**
- Comprehensive financial overview
- Features:
  - Summary cards:
    - Total spent
    - Total orders
    - Pending installments
    - Overdue installments
  - Tabbed data views:
    - **Orders tab**: All orders with status
    - **Workshops tab**: Workshop registrations with payment info
    - **Packages tab**: Package purchases with progress
    - **Courses tab**: Course purchases
    - **Installments tab**: Detailed installment schedule
  - Status badges with color coding
  - Persian date display
  - Progress indicators
  - Overdue payment highlighting
  - Responsive tables
  - Data fetching with React Query

## Routes Added to App.tsx

### Public Routes
```typescript
<Route path="/workshops" element={<Workshops />} />
<Route path="/workshops/:slug" element={<WorkshopDetail />} />
<Route path="/packages" element={<Packages />} />
<Route path="/packages/:slug" element={<PackageDetail />} />
```

### Protected Routes
```typescript
<Route path="/dashboard/financial-report" element={<FinancialReport />} />
<Route path="/workshops/session/:sessionId" element={<WorkshopSession />} />
```

## Backend API Endpoints Created

### Dashboard API
- `GET /api/dashboard/financial-report/` - Get complete financial data

File: `dashboard/api_views.py`
- Returns all orders, workshop registrations, package purchases, course purchases
- Includes installment payment schedules
- Calculates summary statistics
- Handles missing workshops/packages apps gracefully

File: `dashboard/api_urls.py`
- Maps API endpoint to view function

## Technical Features

### State Management
- **React Query** for server state management
- Automatic caching and refetching
- Loading and error states
- Optimistic updates

### Authentication
- Integration with `AuthContext`
- Protected routes redirect to login
- User-specific data fetching
- Conditional rendering based on auth status

### UI/UX Features
- **Responsive Design**: Mobile-first with Bootstrap grid
- **Loading States**: Spinners for async operations
- **Empty States**: Helpful messages when no data
- **Error Handling**: User-friendly error messages
- **Persian Calendar**: Dates displayed in Persian format
- **Number Formatting**: Currency with thousand separators
- **Status Badges**: Color-coded status indicators
- **Modal Dialogs**: For confirmations and selections
- **Hover Effects**: Better interactivity
- **Sticky Sidebars**: Important info always visible

### Video Protection
```typescript
<video
  controls
  controlsList="nodownload"
  onContextMenu={(e) => e.preventDefault()}
>
```
- Prevents download button in video controls
- Disables right-click context menu
- Browser-level protection

### Accessibility
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support
- Color contrast for readability
- Focus states for interactive elements

## Component Architecture

### Shared Patterns
All components follow consistent patterns:
1. **TypeScript interfaces** for type safety
2. **React Helmet** for SEO (title, meta tags)
3. **React Bootstrap** for UI components
4. **Axios** for API calls
5. **React Query** for data fetching
6. **React Router** for navigation
7. **I18n Context** for translations (prepared)

### File Structure
```
frontend/src/pages/
├── Workshops/
│   ├── Workshops.tsx           # List view
│   ├── WorkshopDetail.tsx      # Detail view
│   └── WorkshopSession.tsx     # Session access
├── Packages/
│   ├── Packages.tsx            # List view
│   └── PackageDetail.tsx       # Detail view
└── Dashboard/
    └── FinancialReport.tsx     # Financial report
```

## Styling

### Bootstrap Classes Used
- Container/Row/Col for layout
- Card/Card.Body for content blocks
- Button variants (primary, success, outline)
- Badge for status indicators
- Alert for notifications
- Table for data display
- Form controls for filters
- Tab/Tabs for tabbed content
- Spinner for loading
- Modal for dialogs

### Custom Styles
- Hover effects using `.hover-shadow` class
- Sticky positioning for sidebars
- Image object-fit for thumbnails
- Custom colors for status badges
- RTL support (Bootstrap RTL)

## Data Flow

### Workshop Registration Flow
1. User browses workshops (`/workshops`)
2. Clicks on workshop to see details (`/workshops/:slug`)
3. Clicks "Register" button
4. Modal opens for payment type selection
5. Submits registration via API
6. Redirected to dashboard
7. Can access sessions via `/workshops/session/:sessionId`

### Package Purchase Flow
1. User browses packages (`/packages`)
2. Clicks on package to see details (`/packages/:slug`)
3. Views included courses
4. Clicks "Purchase" button
5. Confirmation dialog
6. Purchase API call
7. Redirected to dashboard
8. Courses automatically enrolled

### Financial Report Access
1. User navigates to `/dashboard/financial-report`
2. Component fetches all financial data
3. Displays in organized tabs
4. User can view:
   - All orders
   - Workshop registrations with installments
   - Package purchases with progress
   - Course purchases
   - Installment payment schedule

## API Integration

### Endpoints Used

#### Workshops
- `GET /api/workshops/` - List workshops
- `GET /api/workshops/:slug/` - Workshop detail
- `POST /api/workshops/:slug/register/` - Register
- `GET /api/workshops/sessions/:id/access/` - Session access
- `POST /api/workshops/sessions/:id/attendance/` - Mark attendance

#### Packages
- `GET /api/packages/` - List packages
- `GET /api/packages/:slug/` - Package detail
- `POST /api/packages/:slug/purchase/` - Purchase

#### Dashboard
- `GET /api/dashboard/financial-report/` - Financial data

### Request/Response Examples

#### Register for Workshop
```typescript
POST /api/workshops/:slug/register/
{
  "payment_type": "installment" | "full_payment"
}

Response:
{
  "message": "ثبت‌نام شما با موفقیت انجام شد",
  "registration": { ... }
}
```

#### Get Financial Report
```typescript
GET /api/dashboard/financial-report/

Response:
{
  "orders": [...],
  "workshop_registrations": [...],
  "package_purchases": [...],
  "course_purchases": [...],
  "installment_payments": [...],
  "total_spent": "1500000",
  "pending_installments_count": 2,
  "overdue_installments_count": 0,
  "total_orders": 5
}
```

## Dependencies

### Existing (Already in project)
- React 18
- TypeScript
- React Router v6
- React Bootstrap
- React Query (@tanstack/react-query)
- Axios
- React Helmet Async
- Bootstrap RTL

### No Additional Dependencies Required
All components use existing dependencies from the project.

## Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive
- Touch-friendly interactions
- RTL (Right-to-Left) support for Persian

## Performance Optimizations
- React Query caching
- Lazy loading images
- Debounced filters (can be added)
- Memoized components (can be added)
- Code splitting by route (already done via React Router)

## Next Steps

### Recommended Enhancements
1. **Add pagination** for large lists
2. **Add search functionality** to workshops/packages
3. **Implement cart integration** for packages
4. **Add review submission forms**
5. **Create progress tracking** dashboard widgets
6. **Add email notifications** for installment reminders
7. **Implement coupon validation** UI
8. **Add file upload** for workshop materials
9. **Create admin dashboard** for workshop management
10. **Add analytics** for user behavior

### Testing
Create test files:
- `Workshops.test.tsx`
- `WorkshopDetail.test.tsx`
- `Packages.test.tsx`
- `PackageDetail.test.tsx`
- `FinancialReport.test.tsx`

### Internationalization
- Add translation keys to I18n context
- Support English locale
- Dynamic language switching

## Files Modified/Created

### Created (7 files)
1. `frontend/src/pages/Workshops/Workshops.tsx`
2. `frontend/src/pages/Workshops/WorkshopDetail.tsx`
3. `frontend/src/pages/Workshops/WorkshopSession.tsx`
4. `frontend/src/pages/Packages/Packages.tsx`
5. `frontend/src/pages/Packages/PackageDetail.tsx`
6. `frontend/src/pages/Dashboard/FinancialReport.tsx`
7. `dashboard/api_views.py`

### Modified (3 files)
1. `frontend/src/App.tsx` - Added routes and imports
2. `dashboard/api_urls.py` - Created with financial report endpoint
3. `dashboard/urls.py` - Already updated in backend implementation

## Success Metrics

✅ All components created
✅ Routes configured
✅ API integration complete
✅ Type safety with TypeScript
✅ Responsive design
✅ Error handling
✅ Loading states
✅ Empty states
✅ Video protection implemented
✅ Persian calendar support
✅ Financial report dashboard
✅ Installment payment UI
✅ Session access control

The frontend is complete and ready for integration with the backend API!

