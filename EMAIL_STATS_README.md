# Email Statistics Feature 📧📊

This document describes the email statistics functionality added to the CheckPoint project.

## Overview

The email statistics feature allows automatic sending of daily file statistics to email addresses. This includes:
- Number of new files processed
- Number of duplicate files found  
- Detailed file lists with paths
- Automatic hourly monitoring with email reports
- Support for custom email recipients

## Configuration

Before using email statistics, ensure the following are configured in `config.py`:

```python
# Email sender configuration (Gmail recommended)
EMAIL_FROM = "your-email@gmail.com"
EMAIL_APP_PASSWORD = "your-app-password"  # 16-character Gmail App Password

# Default notification recipient
NOTIFY_EMAIL = "recipient@email.com"
```

### Getting Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable two-factor authentication
3. Go to "App passwords" section
4. Create a new password for "Mail" 
5. Use the generated 16-character password in `EMAIL_APP_PASSWORD`

## Usage Examples

### 1. Basic Setup

```python
from pathlib import Path
from checkpoint.objects.stats import PhotoStatsManager

# Basic stats manager (no email)
stats_manager = PhotoStatsManager(photo_path, stats_logs_path)

# Stats manager with automatic email sending
stats_manager = PhotoStatsManager(photo_path, stats_logs_path, send_email=True)

# Stats manager with custom email recipient
stats_manager = PhotoStatsManager(photo_path, stats_logs_path, send_email=True, email_to="custom@email.com")
```

### 2. Manual Statistics Sending

```python
# Initialize without automatic email
stats_manager = PhotoStatsManager(photo_path, stats_logs_path)

# Send current statistics to default email
stats_manager.send_current_stats_email()

# Send to custom email
stats_manager.send_current_stats_email("custom@email.com")
```

### 3. Automatic Email Collection

```python
# Initialize with automatic email enabled
stats_manager = PhotoStatsManager(photo_path, stats_logs_path, send_email=True)

# Collect stats - email will be sent automatically
stats_manager.collect_and_log_stats()

# Or use the convenience method (temporarily enables email)
stats_manager = PhotoStatsManager(photo_path, stats_logs_path)  # No email by default
stats_manager.collect_and_email_stats()  # Temporarily enables email for this call
```

### 4. Automatic Monitoring

```python
# Setup monitoring with automatic hourly email reports
stats_manager = PhotoStatsManager(photo_path, stats_logs_path, send_email=True)
stats_manager.start_monitor()

# Setup monitoring with custom email
stats_manager = PhotoStatsManager(photo_path, stats_logs_path, send_email=True, email_to="admin@company.com")
stats_manager.start_monitor()

# Stop monitoring
stats_manager.stop_monitor()
```

## Email Content Format

The email statistics include:

**Subject:** `CheckPoint: Статистика файлов за DD.MM.YYYY`

**Content:**
- Date and time of report
- Monitoring folder path
- Statistics summary (new files, duplicates, total)
- Detailed file lists with full paths
- Log file location information

**Example Email:**
```
Ежедневная статистика файлов CheckPoint

Дата: 09.10.2025
Время отчета: 09.10.2025 14:30:15
Папка мониторинга: C:\Photos\PHOTO

📊 СТАТИСТИКА:
🆕 Новых файлов: 15
♻️ Дублированных файлов: 3
📁 Всего обработано: 18

🆕 НОВЫЕ ФАЙЛЫ:

  1. C:\Photos\PHOTO\photo1.jpg
  2. C:\Photos\PHOTO\photo2.jpg
  ...

♻️ ДУБЛИРОВАННЫЕ ФАЙЛЫ:

  1. C:\Photos\PHOTO\photo1_2.jpg
  2. C:\Photos\PHOTO\photo2_2.jpg
  ...

---
Это автоматический отчет от CheckPoint
Логи сохранены в: C:\Logs\stats_logs
```

## API Reference

### PhotoStatsManager Constructor

```python
PhotoStatsManager(photo_path, stats_logs_path, send_email=False, email_to=None)
```

**Parameters:**
- `photo_path` (Path) - Path to the PHOTO directory to monitor
- `stats_logs_path` (Path) - Path to directory for statistics logs
- `send_email` (bool, optional) - Enable automatic email sending (default: False)
- `email_to` (str, optional) - Custom email recipient (default: uses config.NOTIFY_EMAIL)

### PhotoStatsManager Methods

#### `send_current_stats_email(email_to=None)`
- Sends current day statistics via email
- **Parameters:** `email_to` (optional) - recipient email address (overrides constructor setting)
- **Returns:** `bool` - True if successful

#### `collect_and_email_stats()`
- Temporarily enables email and collects statistics with email sending
- Uses constructor email settings or temporarily enables email for this call

#### `collect_and_log_stats()`
- Collects and logs statistics
- Email sending depends on constructor `send_email` parameter

#### `start_monitor()`
- Starts hourly monitoring thread
- Email sending behavior determined by constructor parameters

#### `demo_email_stats(email_to=None)`
- Demonstration method for testing email functionality
- **Parameters:** `email_to` (optional) - recipient email address

### Helper Functions

#### `send_stats_notification(to_email, new_files, duplicates, photo_path, stats_logs_path)`
- Sends formatted statistics notification email
- Located in `checkpoint.helpers.email`

## Error Handling

The email functionality includes comprehensive error handling:

- **Email configuration errors:** Missing credentials, invalid SMTP settings
- **Network errors:** Connection failures, authentication errors  
- **File system errors:** Missing directories, permission issues
- **Email delivery errors:** Invalid recipients, rejected messages

All errors are logged to console with descriptive messages.

## Security Notes

- Use Gmail App Passwords instead of regular passwords
- Keep email credentials secure and don't commit to version control
- Consider using environment variables for sensitive configuration
- Email content includes file paths - ensure appropriate access controls

## Testing

Use the provided example script `example_email_stats.py` to test functionality:

```bash
python example_email_stats.py
```

This will demonstrate all email statistics features and verify your configuration.

## Integration with Existing Code

The email functionality integrates seamlessly with existing statistics monitoring:

```python
# Existing usage (no changes needed)
stats_manager.collect_and_log_stats()

# New usage with email
stats_manager.collect_and_log_stats(send_email=True)

# Monitoring with email
stats_manager.start_monitor(send_email=True)
```

No breaking changes to existing functionality.