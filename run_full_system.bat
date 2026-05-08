@echo off
echo ================================================
echo PakPulse Database Setup Script
echo ================================================
echo.

cd /d "c:\Users\user\OneDrive - Higher Education Commission\Desktop\FYP"

echo Step 1: Creating database schema...
echo Enter your PostgreSQL password when prompted:
"C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres -f database_schema.sql

if %errorlevel% neq 0 (
    echo.
    echo ❌ Database schema creation failed!
    echo Please check your password and try again.
    pause
    exit /b 1
)

echo.
echo ✅ Database schema created successfully!
echo.

echo Step 2: Loading sample data...
python init_sample_data.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Sample data loading failed!
    pause
    exit /b 1
)

echo.
echo ✅ Sample data loaded successfully!
echo.

echo Step 3: Running full data pipeline...
python data_pipeline.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Data pipeline failed!
    pause
    exit /b 1
)

echo.
echo 🎉 SYSTEM TEST COMPLETED SUCCESSFULLY! 🎉
echo.
echo Your PakPulse disease surveillance system is now running!
echo Check the database for real-time weather, health, and disease data.
echo.
pause