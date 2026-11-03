# VentureVault – Entrepreneur Stories & Business Ideas

**Assigned Project Topic:**
> *"An Online Video Directory for Entrepreneurs – Creation of a video directory showcasing entrepreneurial journeys and business ideas."*

**VentureVault** is a professional, full-stack Django web application designed as a comprehensive video directory for aspiring founders, business students, and innovators. Taking design inspiration from platforms like **Netflix** (video browsing & thumbnail layouts), **YouTube** (directory & player experience), **Startups.com** (entrepreneurial journey timelines & founder profiles), and **Medium** (clean typography and editorial readability), it provides an immersive, responsive learning repository.

---

## 🎨 Design System & Palette

The user interface follows a clean, realistic, and consistent design language across all pages:

| Element | Color Name | Hex Code | Description |
| :--- | :--- | :--- | :--- |
| **Primary Navy** | Deep Navy | `#14213D` | Navbar, Footer, Headings, Primary brand elements |
| **Accent Orange** | Vibrant Amber | `#FCA311` | Primary CTA buttons, Badges, Play overlays, Highlights |
| **Background** | Clean Slate | `#F8FAFC` | Page backgrounds with optimal visual contrast |
| **Cards** | Pure White | `#FFFFFF` | Content cards, Form containers, Video cards |
| **Main Text** | Charcoal Slate | `#1E293B` | High-contrast readable body text and titles |
| **Secondary Text**| Slate Gray | `#64748B` | Subtitles, metadata, dates, view counters |
| **Borders** | Light Border | `#E2E8F0` | Subtle, clean separation borders |

---

## 🚀 Key Features & Pages

### 1. Home Page (`/`)
- **Hero Section**: High-impact navy headline with accent orange highlights, clear mission tagline, call-to-action buttons, live metrics strip (20+ Videos, 19 Founders, 10+ Categories), and featured masterclass player preview.
- **Quick Topic Chips**: YouTube-style horizontal domain tags for fast filtering.
- **Featured Stories**: 3-column video cards with 16:9 thumbnails, duration pills, founder metadata, and interactive bookmark buttons.
- **Trending Videos**: 4-column compact cards highlighting the most-watched founder case studies.
- **Business Domains**: Interactive category cards with FontAwesome icons and real-time video counts.
- **Founder Spotlight**: Highlighting prominent innovators with their startup name, industry, and quote.
- **Value Proposition Grid**: 4-column breakdown of why video-based entrepreneur learning matters.
- **Submit Story CTA**: Highlighting community participation.

### 2. Explore / Video Directory (`/explore/`)
- Advanced filter bar with keyword search, domain dropdown, and multi-option sorting (Newest First, Most Popular, Oldest, Title A-Z).
- Dynamic active filter tags with one-click removal.
- Responsive 3-column video card grid.
- Full pagination controls with query parameter preservation.
- Clear empty-state with reset filter action.

### 3. Video Details & Player Experience (`/video/<id>/`)
- Responsive **16:9 Theater Player** embedding YouTube videos with privacy-enhanced mode (`youtube-nocookie.com`).
- **Graceful Fallback Handling**: Detects restricted or offline YouTube embeds and provides an instant external playback banner with direct link.
- Real-time view count tracking.
- Interactive **Save to Vault** button with instant AJAX response and toast notification.
- One-click **Share Link** button copying URL to clipboard.
- Structured **Key Entrepreneurial Takeaways** annotated with accent gold badges.
- **Founder Profile Sidebar**: Founder avatar, company, industry, location, founded year, and full profile link.
- **Related Stories Sidebar**: 4 related videos in the same domain or featuring the same founder.

### 4. Entrepreneur Profiles (`/entrepreneurs/` & `/entrepreneur/<id>/`)
- **Founders Directory**: Grid of founder cards with verified company badge, location, and total video counts.
- **Founder Detail Page**:
  - Profile header with photo, company badge, industry, location, founded year, and official website link.
  - Interactive **Entrepreneurial Journey Timeline** detailing 5 core phases: Foundation -> Validation -> Founding -> Scaling -> Present Day.
  - Video catalog featuring all masterclasses by this founder.
  - Aggregated key lessons distilled from their interviews.

### 5. Categories & Domain Hubs (`/categories/` & `/category/<slug>/`)
- Domain showcase featuring 10+ sectors: Startup Stories, Technology, FinTech, E-Commerce, Social Impact, Women Entrepreneurs, Innovation, Leadership, Marketing, Small Business.
- Dedicated category pages with sortable and paginated video lists.

### 6. Unified Multi-Entity Search (`/search/`)
- Searches across `Video` (titles, descriptions, takeaways), `Entrepreneur` (names, startups, bios), and `Category` (names, overviews).
- Categorized result sections with match counts and suggested search keywords.

### 7. User Authentication & Dashboard (`/login/`, `/register/`, `/profile/`)
- User Registration with email uniqueness check and auto-login on success.
- Secure Login & Logout supporting GET and POST. Public demo credentials have been completely removed from the login screen for production security.
- **User Dashboard (`/profile/`)**:
  - Personal account info & editable profile details (First Name, Last Name, Email).
  - **Saved Videos Vault**: Grid of bookmarked videos with one-click remove and watch actions.
  - **Story Submissions Tracker**: Table tracking status of submitted stories (Pending Review, Approved, Rejected) with direct links to approved videos.

### 8. Story Submission & Editorial Review (`/submit-story/`)
- Community submission form with category datalist, YouTube URL validation, and optional founder photo.
- Automatic association with authenticated users.
- Submissions are reviewable and approvable directly in the Django Admin.

### 9. Contact Support (`/contact/`)
- Inquiry form with validation, success notifications, and pre-filled data for logged-in users.

### 10. Customized Django Admin (`/admin/`)
- Branded administration panel (*"VentureVault Administration"*).
- Pre-configured `list_display`, `search_fields`, `list_filter`, and prepopulated slugs.
- Custom Admin actions to bulk **Approve** (which automatically instantiates a published `Video` record and linked `Entrepreneur`) or **Reject** submissions.

---

## 🛠️ Technology Stack

- **Backend Framework**: Django 6.1 (Python 3.10+)
- **Frontend Architecture**: HTML5, Semantic CSS3 (CSS Variables / Design System), Bootstrap 5.3, FontAwesome 6
- **Asynchronous Layer**: JavaScript (ES6 Fetch API, CSRF Token Header, Toast UI)
- **Database**: SQLite 3 (Pre-seeded with 20 real-world masterclasses, 19 genuine world-famous entrepreneurs, 11 categories)
- **Security**: Django CSRF Protection, Password Hashing, Session Authentication, Sanitized Redirections

---

## 📁 Project Directory Structure

```text
django_project/
├── .venv/                        # Python virtual environment (located in root)
├── requirements.txt              # Production/development dependencies
├── .env.example                  # Template for environment variables
├── .gitignore                    # Git ignore file excluding cache, venv, backups
├── README.md                     # Project documentation & viva guide
└── django_project/               # Django project root (contains manage.py)
    ├── manage.py                 # Django management script
    ├── db.sqlite3                # SQLite database with genuine sample data
    ├── venturevault/             # Main project configuration
    │   ├── settings.py           # Django settings, security, and context processors
    │   ├── urls.py               # Root URL dispatcher
    │   ├── wsgi.py               # WSGI server entrypoint
    │   └── asgi.py               # ASGI server entrypoint
    └── directory/                # Core application package
        ├── models.py             # Category, Entrepreneur, Video, SavedVideo, StorySubmission, ContactMessage
        ├── views.py              # All view controllers & business logic
        ├── forms.py              # User registration, login, contact & submission forms
        ├── urls.py               # App URL routing
        ├── admin.py              # Customized Django admin interfaces
        ├── context_processors.py # Global category list & saved video counter
        ├── tests.py              # Automated test suite (19 comprehensive test cases)
        ├── management/
        │   └── commands/
        │       └── seed_data.py  # Data seed script with 20 verified real-world founder masterclasses
        ├── static/
        │   └── directory/
        │       ├── css/
        │       │   └── style.css # Master CSS Design System (Navy & Orange)
        │       ├── images/
        │       │   ├── entrepreneurs/        # Authentic portraits & neutral initials SVG avatars for all founders
        │       │   ├── placeholder-video.svg # 16:9 local fallback video thumbnail
        │       │   └── avatar-founder.svg    # Local fallback founder avatar
        │       └── js/
        │           └── main.js   # AJAX bookmarking, toast alerts, share helper
        └── templates/
            └── directory/        # HTML templates with base.html inheritance
                ├── base.html
                ├── home.html
                ├── explore.html
                ├── video_detail.html
                ├── entrepreneurs.html
                ├── entrepreneur_detail.html
                ├── categories.html
                ├── category_videos.html
                ├── search_results.html
                ├── about.html
                ├── contact.html
                ├── submit_story.html
                ├── login.html
                ├── register.html
                └── profile.html
```

---

## 💻 Exact Windows PowerShell Run Commands

Run these exact commands from your terminal:

### Option A: Running from the root directory (`Downloads\django_project`)

```powershell
# 1. Navigate to the root directory
cd "c:\Users\Gagan Shankar Verma\Downloads\django_project"

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Verify Django system checks
python .\django_project\manage.py check

# 4. (Optional) Run the automated unit test suite
python .\django_project\manage.py test directory

# 5. Start the Django development server
python .\django_project\manage.py runserver
```

### Option B: Running from the inner project directory (where `manage.py` is located)

```powershell
# 1. Navigate to the inner project directory
cd "c:\Users\Gagan Shankar Verma\Downloads\django_project\django_project"

# 2. Activate root virtual environment
..\.venv\Scripts\Activate.ps1

# 3. Verify system check
python manage.py check

# 4. Start the Django development server
python manage.py runserver
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:8000/`**

---

## 🔑 Demo & Admin Credentials

*(For evaluator demonstration and grading; kept secure and not displayed publicly on login UI)*

| Role | Username | Password | Access |
| :--- | :--- | :--- | :--- |
| **Superuser / Admin** | `admin` | `admin123` | Full access to `/admin/` portal and user dashboard |
| **Standard Demo User** | `demo` | `demo123` | Access to user vault, profile, and story submissions |

---

## 🎓 College Viva & Presentation Q&A Guide

When presenting this project for your college viva, review these key technical answers:

### Q1: What is the primary purpose and scope of VentureVault?
> **Answer:** VentureVault is an online video directory designed to bridge theoretical business education with practical startup reality. It curates real-world entrepreneurial journeys, business models, and startup lessons through video masterclasses and structured key takeaways, organized across 10+ business categories.

### Q2: How does the YouTube video embedding work and how are invalid/restricted links handled?
> **Answer:** In `directory/models.py`, the `Video` model implements `get_youtube_video_id()` using regular expressions to extract the 11-character video ID from standard watch URLs, short links (`youtu.be`), embed links, shorts, or direct IDs. The `get_youtube_embed_url()` method generates a privacy-enhanced embed URL (`https://www.youtube-nocookie.com/embed/<id>`). In `video_detail.html`, the YouTube IFrame API listens for error codes (e.g. 101/150/153 for embedding restrictions) and gracefully reveals an interactive fallback card with a direct link to YouTube.

### Q3: How does the Save/Bookmark functionality work?
> **Answer:** Saved videos are managed by the `SavedVideo` model with a unique constraint on `('user', 'video')` to prevent duplicates. Bookmarking is powered asynchronously via an AJAX POST endpoint (`/video/<id>/toggle-save/`) with Django CSRF verification. When clicked, it toggles the saved record in the database and returns a JSON response updating the bookmark icon and the global saved counter in the navigation bar without a full page reload.

### Q4: How is security handled in this Django project?
> **Answer:** 
> 1. **CSRF Protection**: All POST forms include `{% csrf_token %}` and AJAX fetch requests send the `X-CSRFToken` header.
> 2. **Authentication & Password Hashing**: Utilizes Django's PBKDF2 with SHA256 password hashing.
> 3. **Environment Security**: Sensitive keys (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`) are read from environment variables via `python-dotenv` with sensible development defaults.
> 4. **Safe Redirects**: Login and logout views sanitize the `next` redirect parameter to avoid open-redirect vulnerabilities.
> 5. **Access Control**: The `@login_required` decorator protects private dashboard endpoints like `/profile/`.

---

**Project Developed & Maintained by Gagan Shankar Verma**
