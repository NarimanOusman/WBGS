# 🏛 Western Bahr el Ghazal State Portal — Project Guide

## 📂 Project Structure

```
wau_state/
│
├── manage.py                    # Django management script
│
├── wau_state/                   # Project configuration
│   ├── __init__.py
│   ├── settings.py              # Project settings
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI entry point
│   └── asgi.py                  # ASGI entry point
│
├── wau/                         # Main application
│   ├── __init__.py
│   ├── admin.py                 # Admin site registration
│   ├── apps.py                  # App configuration
│   ├── models.py                # Database models
│   ├── views.py                 # View functions
│   ├── urls.py                  # App URL patterns (create this)
│   ├── forms.py                 # Form classes (create this)
│   ├── tests.py                 # Unit tests
│   └── migrations/              # Database migrations
│       └── __init__.py
│
├── templates/                   # HTML Templates (9 pages)
│   ├── home.html                # 🏠 Home Page
│   ├── projects.html            # 📋 Projects Page
│   ├── archive.html             # ✅ Archive Page
│   ├── news.html                # 📰 News Page
│   ├── about.html               # 🏛 About Page
│   ├── investment.html          # 💰 Investment Page
│   ├── contact.html             # 📞 Contact Page
│   ├── feedback.html            # 💬 Feedback Page
│   └── admin.html               # 🔒 Admin Dashboard Page
│
├── static/                      # Static assets
│   ├── css/
│   │   └── style.css            # Main stylesheet
│   ├── js/
│   │   └── main.js              # Main JavaScript
│   └── images/                  # Images & icons
│
├── media/                       # User-uploaded files (auto-created)
│
├── db.sqlite3                   # SQLite database (auto-created)
│
├── venv/                        # Python virtual environment
│
└── GUIDE.md                     # ← You are here
```

---

## 📄 Page Descriptions & Features

### 🏠 1. HOME PAGE — `home.html`
- Welcome message from the Governor
- Big icons to navigate to each page (like a phone menu)
- Latest news preview (2–3 items)
- Quick stats (e.g. "12 projects complete, 5 in progress")

### 📋 2. PROJECTS PAGE — `projects.html`
- List of all current/ongoing projects
- Each project shows: Name, Location, Status (🔴 Not Complete / 🟢 Complete)
- Click any project to see more details (description, photos, start date)

### ✅ 3. ARCHIVE PAGE — `archive.html`
- Only shows completed projects
- Acts as a record of achievements
- Each entry: Project name, location, completion date, photos, short summary

### 📰 4. NEWS PAGE — `news.html`
- Governor's announcements and updates
- Each news item: Title, date, photo, short text
- Sorted newest first

### 🏛 5. ABOUT PAGE — `about.html`
- About the Governor and his vision
- About Western Bahr el Ghazal State
- Team members / leadership structure

### 💰 6. INVESTMENT PAGE — `investment.html`
- Sectors open for investment (Agriculture, Infrastructure, Health, etc.)
- Each sector: description, why invest, contact info
- "I am interested" button → sends inquiry to admin

### 📞 7. CONTACT PAGE — `contact.html`
- Phone number, email, office address
- Simple contact form (Name, Message, Send)
- Social media links

### 💬 8. FEEDBACK PAGE — `feedback.html`
- Citizens type their name (optional), select a topic (dropdown), write their comment
- Submit button sends feedback to admin
- Simple "Thank you" message after submitting

### 🔒 9. ADMIN PAGE — `admin.html` (protected with login)
- **Dashboard:** Overview of projects, feedback count, news count
- **Manage Projects:** Add / Edit / Mark as Complete (moves to Archive)
- **Manage News:** Add / Edit / Delete news posts
- **View Feedback:** Read all citizen feedback, mark as read
- **Manage Investments:** Add / Edit investment opportunities
- **View Inquiries:** See investor interest messages

---

## 🗄 Database Models (to build in `wau/models.py`)

### Project
| Field               | Type         | Notes                              |
|---------------------|--------------|------------------------------------|
| title               | CharField    | Project name                       |
| description         | TextField    | Full description                   |
| location            | CharField    | Where the project is located       |
| status              | CharField    | planned / ongoing / completed      |
| start_date          | DateField    | When project started               |
| completion_date     | DateField    | When completed (nullable)          |
| featured_image      | ImageField   | Main project photo                 |
| progress_percentage | IntegerField | 0–100                              |
| created_at          | DateTimeField| Auto timestamp                     |

### NewsPost
| Field          | Type          | Notes                         |
|----------------|---------------|-------------------------------|
| title          | CharField     | Headline                      |
| content        | TextField     | Full article text             |
| excerpt        | TextField     | Short preview text            |
| featured_image | ImageField    | News photo                    |
| published      | BooleanField  | Show/hide                     |
| created_at     | DateTimeField | Auto timestamp, sorted by     |

### TeamMember
| Field  | Type       | Notes                  |
|--------|------------|------------------------|
| name   | CharField  | Person's name          |
| title  | CharField  | Position / role        |
| bio    | TextField  | Short biography        |
| photo  | ImageField | Profile photo          |
| order  | IntegerField | Display order        |

### InvestmentSector
| Field        | Type       | Notes                         |
|--------------|------------|-------------------------------|
| name         | CharField  | Sector name                   |
| description  | TextField  | Full description              |
| why_invest   | TextField  | Reasons to invest             |
| contact_info | TextField  | Contact for this sector       |
| icon         | CharField  | Icon class (Font Awesome)     |
| is_active    | BooleanField | Show/hide                   |

### InvestmentInquiry
| Field        | Type          | Notes                      |
|--------------|---------------|----------------------------|
| sector       | ForeignKey    | Links to InvestmentSector  |
| name         | CharField     | Investor name              |
| email        | EmailField    | Investor email             |
| message      | TextField     | Interest message           |
| is_read      | BooleanField  | Admin read status          |
| created_at   | DateTimeField | Auto timestamp             |

### ContactMessage
| Field      | Type          | Notes                   |
|------------|---------------|-------------------------|
| name       | CharField     | Sender name             |
| email      | EmailField    | Optional                |
| message    | TextField     | The message             |
| is_read    | BooleanField  | Admin read status       |
| created_at | DateTimeField | Auto timestamp          |

### Feedback
| Field      | Type          | Notes                        |
|------------|---------------|------------------------------|
| name       | CharField     | Optional (anonymous allowed) |
| topic      | CharField     | Dropdown choices             |
| message    | TextField     | Citizen's comment            |
| is_read    | BooleanField  | Admin read status            |
| created_at | DateTimeField | Auto timestamp               |

---

## 🚀 Additional Features to Consider

### Security & Authentication
- Admin login required for admin.html
- CSRF protection on all forms
- Input validation and sanitization

### UI/UX Enhancements
- Responsive design (mobile-friendly)
- Dark mode toggle
- Loading animations
- Toast notifications for form submissions
- Search bar (filter projects, news)

### Data Features
- Pagination for projects, news, archive lists
- Image gallery for project photos (before/after)
- Export data to PDF/CSV from admin
- Print-friendly pages

### Communication
- Email notifications when new feedback/inquiry arrives
- SMS integration for urgent updates
- Newsletter subscription

### Analytics
- Visitor counter on homepage
- Most viewed projects tracking
- Feedback topic trends chart in admin

---

## 🛠 How to Run

```bash
# 1. Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# 2. Install dependencies
pip install django pillow

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create admin superuser
python manage.py createsuperuser

# 5. Run development server
python manage.py runserver

# 6. Open in browser
# http://127.0.0.1:8000/
```

---

## 📌 URL Patterns (to build in `wau/urls.py`)

| URL Path           | View             | Template         |
|--------------------|------------------|------------------|
| `/`                | home_view        | home.html        |
| `/projects/`       | projects_view    | projects.html    |
| `/archive/`        | archive_view     | archive.html     |
| `/news/`           | news_view        | news.html        |
| `/about/`          | about_view       | about.html       |
| `/investment/`     | investment_view  | investment.html  |
| `/contact/`        | contact_view     | contact.html     |
| `/feedback/`       | feedback_view    | feedback.html    |
| `/admin-dashboard/`| admin_view       | admin.html       |

---

*Built with Django 5.2 for the people of Western Bahr el Ghazal State* 🇸🇸
