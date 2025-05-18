# Cloud Security Dashboard - Deployment Guide

## AWS Deployment

### Backend Deployment (EC2/Lambda)

#### Option 1: EC2 Deployment

1. **Launch EC2 Instance**
   ```bash
   # Choose Amazon Linux 2 or Ubuntu
   # Instance type: t3.medium or larger
   # Security group: Allow ports 8000, 22
   ```

2. **Install Dependencies**
   ```bash
   sudo yum update -y
   sudo yum install python3 python3-pip postgresql git -y
   ```

3. **Deploy Application**
   ```bash
   git clone <your-repo-url>
   cd Cloud\ Dashboard/backend
   pip3 install -r requirements.txt
   
   # Set environment variables
   export DATABASE_URL="postgresql://..."
   export SECRET_KEY="your-secret-key"
   
   # Run with Gunicorn
   pip3 install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

4. **Setup Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/security-dashboard.service
   ```
   
   ```ini
   [Unit]
   Description=Security Dashboard API
   After=network.target
   
   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/Cloud\ Dashboard/backend
   Environment="DATABASE_URL=postgresql://..."
   Environment="SECRET_KEY=your-secret-key"
   ExecStart=/usr/local/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   
   [Install]
   WantedBy=multi-user.target
   ```

#### Option 2: Lambda Deployment

1. **Create Lambda Function**
   ```bash
   # Package the application
   pip install -r requirements.txt -t package/
   cd package && zip -r ../deployment.zip .
   cd .. && zip -g deployment.zip main.py app/*
   ```

2. **Create Lambda Function** via AWS Console
   - Runtime: Python 3.11
   - Handler: main.handler
   - Upload deployment.zip
   - Add API Gateway trigger

3. **Configure Environment Variables**
   - DATABASE_URL
   - SECRET_KEY
   - Other config variables

### Database Setup (RDS)

1. **Create RDS PostgreSQL Instance**
   ```bash
   # Via AWS Console:
   # - Database: PostgreSQL 15
   # - Instance: db.t3.micro (free tier) or larger
   # - Storage: 20 GB
   # - VPC: Same as EC2/Lambda
   ```

2. **Initialize Database**
   ```bash
   python scripts/init_db.py
   ```

### Frontend Deployment (Vercel)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy Frontend**
   ```bash
   cd frontend
   vercel --prod
   ```

3. **Configure Environment Variables** in Vercel Dashboard
   ```
   NEXT_PUBLIC_API_URL=https://your-api-domain.com
   NEXT_PUBLIC_WS_URL=wss://your-api-domain.com
   ```

### Alternative: CloudFront Distribution

1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   npm run export
   ```

2. **Upload to S3**
   ```bash
   aws s3 sync out/ s3://your-bucket-name
   ```

3. **Create CloudFront Distribution**
   - Origin: S3 bucket
   - Default Root Object: index.html
   - Custom Error Pages: 404 → /404.html

## Docker Deployment

### Build and Run

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Initialize database
docker-compose -f docker/docker-compose.yml exec backend python scripts/init_db.py

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

### Production Deployment

1. **Build Production Images**
   ```bash
   docker build -f docker/backend.Dockerfile -t security-dashboard-backend:latest backend/
   docker build -f docker/frontend.Dockerfile -t security-dashboard-frontend:latest frontend/
   ```

2. **Push to Registry**
   ```bash
   docker tag security-dashboard-backend:latest your-registry/backend:latest
   docker tag security-dashboard-frontend:latest your-registry/frontend:latest
   docker push your-registry/backend:latest
   docker push your-registry/frontend:latest
   ```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-very-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
```

## SSL/TLS Configuration

### Using Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo yum install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Monitoring & Logs

### CloudWatch Setup
1. Install CloudWatch agent on EC2
2. Configure log groups
3. Set up alarms for critical metrics

### Application Logs
```bash
# View backend logs
docker-compose logs -f backend

# View frontend logs
docker-compose logs -f frontend
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY (32+ characters)
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable CloudWatch monitoring
- [ ] Rotate access keys regularly
- [ ] Use IAM roles for EC2/Lambda
- [ ] Enable VPC security groups
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets

## Scaling Considerations

### Horizontal Scaling
- Use AWS ELB/ALB for load balancing
- Deploy multiple backend instances
- Use RDS read replicas for database

### Caching
- Implement Redis for session storage
- Use CloudFront for static assets
- Cache API responses

### Performance Optimization
- Enable gzip compression
- Optimize database queries
- Use CDN for frontend assets
- Implement connection pooling
