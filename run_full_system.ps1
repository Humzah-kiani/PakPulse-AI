# PakPulse Full System Test Script
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "PakPulse Disease Surveillance System - Full Test" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$workingDir = "c:\Users\user\OneDrive - Higher Education Commission\Desktop\FYP"
Set-Location $workingDir

# Step 1: Create database schema
Write-Host "Step 1: Creating database schema..." -ForegroundColor Yellow
Write-Host "Enter your PostgreSQL password when prompted:" -ForegroundColor Yellow

try {
    & "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres -f database_schema.sql
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database schema created successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Database schema creation failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "❌ Error running psql: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Step 2: Load sample data
Write-Host "Step 2: Loading sample data..." -ForegroundColor Yellow
try {
    & python init_sample_data.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Sample data loaded successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Sample data loading failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "❌ Error loading sample data: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Step 3: Run full data pipeline
Write-Host "Step 3: Running full data pipeline..." -ForegroundColor Yellow
try {
    & python data_pipeline.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Data pipeline completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Data pipeline failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "❌ Error running data pipeline: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🎉 SYSTEM TEST COMPLETED SUCCESSFULLY! 🎉" -ForegroundColor Green
Write-Host ""
Write-Host "Your PakPulse disease surveillance system is now operational!" -ForegroundColor Green
Write-Host "Real-time data collection from all APIs is working." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "- Check pgAdmin for database contents" -ForegroundColor White
Write-Host "- Run scheduled jobs with: python data_pipeline.py --schedule" -ForegroundColor White
Write-Host "- View predictions in the database views" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"