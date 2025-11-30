<!-- d02a2088-07dd-4423-980b-356504a956c4 40f70a59-9c42-45ca-bcad-428d2bd60f9f -->
# Blog Management Module Implementation

## Overview

Add a complete blog management system to the admin panel with posts management, categories, tags, and comment moderation capabilities.

## Features to Implement

### 1. Blog Posts Management

**Route**: `/admin-panel/blog`

**Features**:

- List all blog posts with pagination
- Filter by status (draft, published, scheduled)
- Filter by category and tags
- Search by title and content
- Create new post with rich text editor
- Edit existing posts
- Delete posts
- Bulk actions (publish, unpublish, delete)
- Preview post
- Schedule publishing

**Components**:

- `BlogList.tsx` - Main posts listing page
- `BlogForm.tsx` - Create/Edit post form (multi-step)
- `BlogPreview.tsx` - Preview modal

### 2. Categories Management

**Route**: `/admin-panel/blog/categories`

**Features**:

- List all categories
- Create/Edit/Delete categories
- Category slug management
- Order categories

**Component**:

- `CategoriesManager.tsx`

### 3. Tags Management  

**Route**: `/admin-panel/blog/tags`

**Features**:

- List all tags
- Create/Edit/Delete tags
- Tag slug management
- Tag usage statistics

**Component**:

- `TagsManager.tsx`

### 4. Comments Moderation

**Route**: `/admin-panel/blog/comments`

**Features**:

- List all comments
- Filter by status (pending, approved, spam)
- Approve/Reject comments
- Delete comments
- Bulk moderation
- Reply to comments

**Component**:

- `CommentsModeration.tsx`

## Implementation Steps

### Step 1: Backend API Enhancement

1. Check existing blog API endpoints in `app/blog/api_views.py`
2. Add missing endpoints:

   - Post CRUD operations
   - Category management
   - Tag management
   - Comment moderation
   - Bulk operations

### Step 2: Blog Posts List

1. Create `BlogList.tsx` with:

   - Data table showing posts
   - Status badges (draft, published, scheduled)
   - Category and tags display
   - Author information
   - Actions (edit, delete, preview)
   - Advanced filters
   - Search functionality

### Step 3: Blog Post Form

1. Create `BlogForm.tsx` with multi-step wizard:

   - **Step 1**: Basic Info (title, slug, excerpt)
   - **Step 2**: Content (rich text editor)
   - **Step 3**: Media (featured image, gallery)
   - **Step 4**: Settings (category, tags, status, publish date)
   - **Step 5**: SEO (meta title, description, keywords)

2. Integrate rich text editor (TinyMCE or Quill)

### Step 4: Categories Management

1. Create `CategoriesManager.tsx`:

   - Table view with categories
   - Inline editing
   - Add new category dialog
   - Delete confirmation
   - Drag & drop ordering

### Step 5: Tags Management

1. Create `TagsManager.tsx`:

   - Tag cloud view or table
   - Add/Edit/Delete dialogs
   - Usage count display
   - Color coding

### Step 6: Comments Moderation

1. Create `CommentsModeration.tsx`:

   - Comments list with post context
   - Status filters
   - Approve/Reject buttons
   - Bulk moderation toolbar
   - Reply functionality
   - User information

### Step 7: Integration

1. Add routes to `App.tsx`
2. Add menu items to `AdminLayout.tsx`
3. Update navigation

### Step 8: Backend APIs

1. Enhance or create API endpoints:
   ```python
   # Posts
   GET /api/admin/blog/posts/
   POST /api/admin/blog/posts/
   GET /api/admin/blog/posts/{id}/
   PUT /api/admin/blog/posts/{id}/
   DELETE /api/admin/blog/posts/{id}/
   POST /api/admin/blog/posts/bulk-action/
   
   # Categories
   GET /api/admin/blog/categories/
   POST /api/admin/blog/categories/
   PUT /api/admin/blog/categories/{id}/
   DELETE /api/admin/blog/categories/{id}/
   
   # Tags
   GET /api/admin/blog/tags/
   POST /api/admin/blog/tags/
   PUT /api/admin/blog/tags/{id}/
   DELETE /api/admin/blog/tags/{id}/
   
   # Comments
   GET /api/admin/blog/comments/
   PUT /api/admin/blog/comments/{id}/
   POST /api/admin/blog/comments/bulk-action/
   ```


## Technical Details

### Rich Text Editor

Use **React Quill** or **TinyMCE**:

```bash
npm install react-quill quill
```

### Form Structure

```typescript
interface BlogPost {
  id?: number;
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  featured_image?: File | string;
  category_id: number;
  tags: number[];
  status: 'draft' | 'published' | 'scheduled';
  publish_date?: string;
  meta_title?: string;
  meta_description?: string;
  author_id: number;
}
```

### Filters

- Status: Draft, Published, Scheduled, All
- Category: All categories dropdown
- Tags: Multi-select tags
- Author: All authors dropdown
- Date range: From/To date picker

## Files to Create

### Frontend

```
frontend/src/pages/AdminPanel/Blog/
├── BlogList.tsx
├── BlogForm.tsx
├── BlogPreview.tsx
├── CategoriesManager.tsx
├── TagsManager.tsx
└── CommentsModeration.tsx

frontend/src/components/Admin/Blog/
├── PostCard.tsx
├── CategoryChip.tsx
├── TagChip.tsx
└── CommentCard.tsx
```

### Backend (if needed)

```
app/admin_panel/blog_views.py
```

## UI Components

### BlogList Features

- Card/Table toggle view
- Status badges with colors
- Category badges
- Tag pills
- Featured image thumbnails
- Author avatar
- Publish date
- Edit/Delete/Preview actions

### BlogForm Features

- Stepper navigation
- Auto-save draft
- Slug auto-generation
- Image upload with preview
- Tag autocomplete
- Category dropdown
- Date/time picker for scheduling
- Preview button
- Save as draft button
- Publish button

### CategoriesManager Features

- Hierarchical display (parent/child)
- Color picker for category
- Icon selector
- Description field
- Post count

### CommentsModeration Features

- Comment content preview
- Post title link
- Commenter info (name, email)
- Comment date
- Status toggle
- Quick reply box
- Spam marking

## Success Criteria

- ✅ All CRUD operations working
- ✅ Rich text editor integrated
- ✅ Image upload functional
- ✅ Filters and search working
- ✅ Bulk operations implemented
- ✅ Responsive design
- ✅ Loading states
- ✅ Error handling
- ✅ Persian language support

## Timeline Estimate

- Backend APIs: 1-2 hours
- BlogList: 1 hour
- BlogForm: 2-3 hours
- Categories: 1 hour
- Tags: 1 hour  
- Comments: 1-2 hours
- Testing: 1 hour

**Total**: ~8-11 hours of work

### To-dos

- [ ] Install Material-UI and dependencies, configure theme with RTL support
- [ ] Create AdminLayout with sidebar, AppBar, breadcrumbs, and navigation structure
- [ ] Build shared components: AdminDataTable, FormComponents, Chart components
- [ ] Implement Dashboard with statistics cards, charts, and recent activities
- [ ] Build Users management with CRUD, filters, bulk actions, and export
- [ ] Build Courses management with multi-step form, media upload, and lesson management
- [ ] Build Blog management with rich text editor, categories, and comment moderation
- [ ] Build Therapy Sessions management with calendar view and status tracking
- [ ] Build Workshops management with registration and attendance tracking
- [ ] Build Tests management with question manager and results analytics
- [ ] Build Payments management with orders, revenue tracking, and refunds
- [ ] Build Analytics dashboard with charts for users, revenue, and engagement
- [ ] Implement real-time notifications system with bulk send and templates
- [ ] Add export/import functionality for all modules (CSV, Excel, PDF)
- [ ] Implement role-based access control for different admin permission levels
- [ ] Enhance backend APIs with new endpoints for statistics, export, and bulk actions
- [ ] Add loading states, error handling, animations, and final testing