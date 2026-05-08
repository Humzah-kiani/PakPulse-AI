# PostgreSQL Password Tester
Write-Host "PostgreSQL Password Tester" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

$passwords = @("postgres", "pakpulse123", "password", "admin", "123456", "root")

Write-Host "Testing common passwords..." -ForegroundColor Yellow
Write-Host ""

foreach ($pwd in $passwords) {
    Write-Host "Testing password: $pwd" -NoNewline
    try {
        $env:PGPASSWORD = $pwd
        $result = & "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres -c "SELECT version();" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host " SUCCESS!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Found working password: $pwd" -ForegroundColor Green
            Write-Host "Now proceeding with database setup..." -ForegroundColor Green
            Write-Host ""

            # Set the correct password for subsequent operations
            $env:PGPASSWORD = $pwd

            # Create database schema
            Write-Host "Creating database schema..." -ForegroundColor Yellow
            & "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres -f database_schema.sql

            if ($LASTEXITCODE -eq 0) {
                Write-Host "Database schema created!" -ForegroundColor Green

                # Load sample data
                Write-Host "Loading sample data..." -ForegroundColor Yellow
                & python init_sample_data.py

                if ($LASTEXITCODE -eq 0) {
                    Write-Host "Sample data loaded!" -ForegroundColor Green

                    # Run full pipeline
                    Write-Host "Running full data pipeline..." -ForegroundColor Yellow
                    & python data_pipeline.py

                    if ($LASTEXITCODE -eq 0) {
                        Write-Host ""
                        Write-Host "COMPLETE SYSTEM TEST SUCCESSFUL!" -ForegroundColor Green
                        Write-Host "Your PakPulse system is now operational!" -ForegroundColor Green
                    } else {
                        Write-Host "Pipeline failed, but database is ready" -ForegroundColor Red
                    }
                } else {
                    Write-Host "Sample data loading failed" -ForegroundColor Red
                }
            } else {
                Write-Host "Database schema creation failed" -ForegroundColor Red
            }

            Read-Host "Press Enter to exit"
            exit 0
        } else {
            Write-Host " Failed" -ForegroundColor Red
        }
    } catch {
        Write-Host " Error" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "None of the common passwords worked." -ForegroundColor Red
Write-Host ""
Write-Host "Please enter your actual PostgreSQL password:" -ForegroundColor Yellow
$userPassword = Read-Host -AsSecureString
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($userPassword))

Write-Host ""
Write-Host "Testing your password..." -ForegroundColor Yellow
$env:PGPASSWORD = $plainPassword

try {
    $result = & "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres -c "SELECT version();" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Password correct! Proceeding with setup..." -ForegroundColor Green
        Write-Host ""

        # Create database schema
        Write-Host "Creating database schema..." -ForegroundColor Yellow
        & "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres -f database_schema.sql

        if ($LASTEXITCODE -eq 0) {
            Write-Host "Database schema created!" -ForegroundColor Green

            # Load sample data
            Write-Host "Loading sample data..." -ForegroundColor Yellow
            & python init_sample_data.py

            if ($LASTEXITCODE -eq 0) {
                Write-Host "Sample data loaded!" -ForegroundColor Green

                # Run full pipeline
                Write-Host "Running full data pipeline..." -ForegroundColor Yellow
                & python data_pipeline.py

                if ($LASTEXITCODE -eq 0) {
                    Write-Host ""
                    Write-Host "COMPLETE SYSTEM TEST SUCCESSFUL!" -ForegroundColor Green
                    Write-Host "Your PakPulse system is now operational!" -ForegroundColor Green
                } else {
                    Write-Host "Pipeline failed, but database is ready" -ForegroundColor Red
                }
            } else {
                Write-Host "Sample data loading failed" -ForegroundColor Red
            }
        } else {
            Write-Host "Database schema creation failed" -ForegroundColor Red
        }
    } else {
        Write-Host "Password still incorrect. Please restart PostgreSQL and try again." -ForegroundColor Red
        Write-Host "Or reset the postgres password using pgAdmin." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Connection failed. Please check PostgreSQL service." -ForegroundColor Red
}

Read-Host "Press Enter to exit"