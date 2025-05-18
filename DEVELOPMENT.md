# Local Development Setup

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Git

## Backend Development

### 1. Set up Python Environment
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database
```bash
# Install PostgreSQL if not already installed
brew install postgresql@15  # macOS
# or follow instructions for your OS

# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb security_dashboard

# Update .env file
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Initialize Database
```bash
python scripts/init_db.py
```

### 4. Run Development Server
```bash
# With auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# View logs
tail -f logs/app.log
```

### 5. Run Tests (Optional)
```bash
pytest tests/ -v
```

## Frontend Development

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
```bash
cp .env.local.example .env.local
# Edit .env.local with your API URL
```

### 3. Run Development Server
```bash
npm run dev
```

### 4. Build for Production
```bash
npm run build
npm run start
```

### 5. Lint and Format
```bash
npm run lint
npm run format
```

## Common Development Tasks

### Add New API Endpoint

1. Create endpoint in `backend/app/api/`
2. Add schema in `backend/app/schemas/`
3. Update router in `backend/main.py`
4. Test with curl or Swagger UI

### Add New Frontend Component

1. Create component in `frontend/src/components/`
2. Import and use in pages
3. Update types in `frontend/src/types/`
4. Test in browser

### Database Migrations (Optional)

```bash
cd backend

# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

### Backend Issues

**Database connection error:**
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string in .env
echo $DATABASE_URL
```

**Import errors:**
```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Module not found:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Build errors:**
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

## Environment Variables

### Backend (.env)
```env
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/security_dashboard
SECRET_KEY=your-secret-key-min-32-characters

# Optional
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### Frontend (.env.local)
```env
# Required
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## VS Code Setup

Recommended extensions:
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense

`.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add your feature"

# Push to remote
git push origin feature/your-feature-name

# Create pull request
```

## Performance Tips

### Backend
- Use database indexes for frequently queried fields
- Implement caching for expensive operations
- Use connection pooling
- Profile slow endpoints with `cProfile`

### Frontend
- Use React.memo for expensive components
- Implement virtual scrolling for large lists
- Lazy load images and components
- Use Next.js Image component

## Security Best Practices

- Never commit `.env` files
- Use strong secrets (32+ characters)
- Keep dependencies updated
- Sanitize user inputs
- Use HTTPS in production
- Implement rate limiting
- Enable CORS properly
- Rotate JWT secrets regularly
