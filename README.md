# Ad Agency Budget Management System

A Django + Celery backend system for automated advertising budget management, campaign control, and dayparting enforcement.

## 🚀 Features

- **Budget Tracking**: Real-time daily and monthly ad spend monitoring
- **Automated Campaign Control**: Auto-pause/resume campaigns based on budget limits
- **Dayparting Enforcement**: Campaigns only run during scheduled hours
- **Daily/Monthly Resets**: Automatic budget resets at midnight and month start
- **Admin Dashboard**: Easy management of brands, campaigns, and schedules

## 🛠️ Tech Stack

- **Backend**: Django 5.1
- **Task Queue**: Celery 5.5.3
- **Message Broker**: Redis (Docker container)
- **Database**: SQLite (Development) / PostgreSQL (Production-ready)
- **Python**: 3.8+

## 📋 Prerequisites

- Python 3.8+
- Docker Desktop
- Git

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/razamasood1234-lang/ad_agency_budget_system.git
cd ad_agency_budget_system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
```bash
# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install django celery redis
```

### 5. Start Redis with Docker
```bash
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

### 6. Database Setup
```bash
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

## 🏃‍♂️ Running the Application

### Start Services (in separate terminals):

1. **Redis Server** (if not already running):
```bash
docker start redis-stack
```

2. **Celery Worker**:
```bash
celery -A config worker --pool=solo --loglevel=info
```

3. **Celery Beat** (after worker is ready):
```bash
celery -A config beat --loglevel=info
```

4. **Django Development Server**:
```bash
python manage.py runserver
```

## 📊 Access Points

- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Redis Insight**: http://localhost:8001/ (Redis management UI)
- **API Endpoints**: http://127.0.0.1:8000/

## 🏗️ Data Models

### Brand
- Represents advertiser companies
- Manages daily/monthly budgets and spending
- Contains financial limits and current spend totals

### Campaign
- Individual advertising campaigns under brands
- Tracks active status and budget pause reasons
- Links to dayparting schedules

### DaypartingSchedule
- Defines allowed running hours for campaigns
- Start/end time enforcement
- Optional for 24/7 campaigns

### SpendLog
- Audit trail of all spending events
- Automatic budget total updates
- Transaction history

## ⚙️ Automated Tasks

### Periodic Checks (Every 5 minutes)
- Budget compliance verification
- Schedule enforcement
- Campaign auto-pause/resume

### Daily Reset (Midnight)
- Reset daily spend counters
- Reactivate budget-paused campaigns

### Monthly Reset (1st of month)
- Reset monthly spend counters
- Comprehensive campaign reactivation

## 🧪 Testing

### Simulate Ad Spending
```bash
python manage.py simulate_spend <campaign_id> <amount>
```

### Example:
```bash
python manage.py simulate_spend 1 50.00
```

### Manual Task Execution
```bash
python manage.py shell
```
```python
from budget.tasks import check_budgets_and_schedules_task
check_budgets_and_schedules_task()
```

## 🎯 Usage Workflow

1. **Create Brand**: Add advertiser with daily/monthly budgets
2. **Create Campaign**: Set up ad campaigns under the brand
3. **Set Schedule**: Define dayparting hours (optional)
4. **Simulate Spend**: Test with simulated spending events
5. **Monitor**: System auto-manages campaign status based on rules

## 🔧 Configuration

### Timezone Settings (Asia/Karachi)
Update `config/settings.py`:
```python
TIME_ZONE = 'Asia/Karachi'
USE_TZ = True
```

### Celery Settings
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'Asia/Karachi'
```

## 🐛 Troubleshooting

### Common Issues:

1. **Celery Connection Error**: Ensure Redis Docker container is running
2. **Task Not Registered**: Restart Celery worker after code changes
3. **Timezone Issues**: Verify `TIME_ZONE` setting in settings.py
4. **Permission Errors**: Use `--pool=solo` flag for Windows

### Debug Commands:
```bash
# Check registered tasks
celery -A config inspect registered

# Check worker status
celery -A config status

# Test Redis connection
docker exec -it redis-stack redis-cli ping
```

## 📁 Project Structure
```
ad_agency_budget_system/
├── config/                 # Django project settings
├── budget/                 # Main application
│   ├── models.py          # Data models
│   ├── tasks.py           # Celery tasks
│   ├── admin.py           # Admin panel config
│   └── management/        # Custom commands
├── venv/                  # Virtual environment
├── manage.py              # Django management
└── requirements.txt       # Dependencies
```



