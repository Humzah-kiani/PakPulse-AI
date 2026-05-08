# Setting Up Weekly Data Updates (Cron Job)

## For Windows (Task Scheduler)

### Step 1: Create Batch File
Create `update_data.bat` in project root:
```batch
@echo off
cd /d "C:\Users\MK\Desktop\FYP\Pak-Pulse-AI-Outbreak-Disease-Early-Warning-System"
python utils\weekly_data_update.py
```

### Step 2: Schedule in Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Name: "PakPulse Weekly Data Update"
4. Trigger: Weekly (choose day/time)
5. Action: Start a program
6. Program: `update_data.bat`
7. Save

---

## For Linux/Mac (Cron)

### Step 1: Make Script Executable
```bash
chmod +x utils/weekly_data_update.py
```

### Step 2: Edit Crontab
```bash
crontab -e
```

### Step 3: Add Cron Job
```cron
# Run every Monday at 2 AM
0 2 * * 1 cd /path/to/project && python utils/weekly_data_update.py >> logs/update.log 2>&1
```

---

## Manual Run
```bash
python utils/weekly_data_update.py
```

---

*Last Updated: Today*



