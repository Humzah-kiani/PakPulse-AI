# PostgreSQL Setup - QUICK START

## Step 1: Download & Install PostgreSQL

1. Go to: https://www.postgresql.org/download/windows/
2. Click **Download the installer**
3. Run the installer and follow these settings:
   - **Installation Directory**: Keep default (C:\Program Files\PostgreSQL\xx)
   - **Password**: Set a strong password (you'll need this!)
   - **Port**: Keep default (5432)
   - **Locale**: English, United States
   - When asked to install Stack Builder: **Skip it** (uncheck)

4. Click **Finish**

## Step 2: Start PostgreSQL Service (Windows)

Open PowerShell as Administrator and run:
```powershell
Start-Service -Name postgresql-x64-*
```

Or use Windows Services:
- Press `Win + R`, type `services.msc`
- Find **postgresql-x64-xx** service
- Right-click → Start

## Step 3: Create Database & Schema

Open PowerShell and run:
```powershell
cd "c:\Users\user\OneDrive - Higher Education Commission\Desktop\FYP"
psql -U postgres -f database_schema.sql
```

When prompted for password, enter the password you set during installation.

## Step 4: Initialize Sample Data (Optional but Recommended)

```powershell
python init_sample_data.py
```

## Step 5: Run the Full Pipeline

```powershell
python data_pipeline.py
```

---

## Troubleshooting

**"psql: command not found"**
- Add PostgreSQL to PATH:
  1. `$env:Path += ";C:\Program Files\PostgreSQL\16\bin"` (adjust version number)
  2. Try again

**"Connection refused"**
- PostgreSQL service not running
- Start it: `Start-Service -Name postgresql-x64-16` (adjust version)

**"password authentication failed"**
- Make sure you're using the password set during PostgreSQL installation
- Or edit `.env` and update `DB_PASSWORD` value

---

## Once PostgreSQL is Installed & Running:

The system will automatically:
✓ Fetch live weather data from OpenWeather API
✓ Fetch health indicators from WHO Global Health Observatory
✓ Sync disease cases from AWS Athena (if configured)
✓ Store everything in PostgreSQL
✓ Generate outbreak risk predictions
✓ Log all activities to the database

Estimated setup time: **5-10 minutes**
