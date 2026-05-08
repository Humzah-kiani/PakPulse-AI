# PostgreSQL Installation - Package Selection Guide

## 📦 When PostgreSQL Asks "Select Components"

During PostgreSQL installation, you'll see a "Select Components" screen. **Select these packages:**

### ✅ **REQUIRED COMPONENTS** (Check these):
- ☑️ **PostgreSQL Server** - The main database server
- ☑️ **pgAdmin 4** - Database administration tool (recommended)
- ☑️ **Command Line Tools** - psql, pg_dump, etc. (REQUIRED for our scripts)

### ❌ **OPTIONAL COMPONENTS** (You can uncheck these):
- ☐ Stack Builder - Additional tools (not needed)
- ☐ PostgreSQL Documentation - Help files (optional)

---

## 🔧 Installation Settings

When prompted for these settings:

### **Password:**
- Set a strong password you'll remember
- Example: `PakPulse2024!` or `pakpulse123`
- **⚠️ IMPORTANT:** Write this down - you'll need it later!

### **Port:**
- Keep default: `5432`
- Don't change unless you have conflicts

### **Locale:**
- Select: `English, United States`

---

## ✅ After Installation Completes:

1. **PostgreSQL service should start automatically**
2. **Open PowerShell** and test:
   ```powershell
   psql --version
   ```
   Should show: `psql (PostgreSQL) xx.x`

3. **Create the database:**
   ```powershell
   cd "c:\Users\user\OneDrive - Higher Education Commission\Desktop\FYP"
   psql -U postgres -f database_schema.sql
   ```

4. **Load sample data:**
   ```powershell
   python init_sample_data.py
   ```

5. **Run the full system:**
   ```powershell
   python data_pipeline.py
   ```

---

## 🛠️ If Installation Fails:

**"Installation directory not writable"**
- Run installer as Administrator

**"Port 5432 already in use"**
- Change port to 5433 during installation

**"psql command not found"**
- Add to PATH: `$env:Path += ";C:\Program Files\PostgreSQL\16\bin"`

---

## 🎯 Quick Verification:

After installation, run this to confirm everything works:
```powershell
# Test PostgreSQL
psql --version

# Test database creation
psql -U postgres -c "SELECT version();"
```

**Then proceed with the system test!** 🚀