# Deployment Guide

Step-by-step guide to deploy AirBall to production.

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Database Setup](#database-setup)
5. [SSL/HTTPS](#ssl-https)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All code reviewed and tested locally
- [ ] No hardcoded secrets or API keys
- [ ] All imports resolved
- [ ] No console.log in production code
- [ ] TypeScript compiles without errors
- [ ] Python code passes linting (flake8/pylint)

### Configuration
- [ ] Environment variables documented
- [ ] Default values for all env vars
- [ ] CORS origins configured for production domain
- [ ] API rate limits defined
- [ ] Database backup strategy in place

### Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] End-to-end video processing tested
- [ ] API tested with production data
- [ ] Frontend tested in production build
- [ ] Mobile responsiveness verified

### Documentation
- [ ] README updated
- [ ] API documentation current
- [ ] Deployment steps documented
- [ ] Rollback procedure documented

---

## Backend Deployment

### Option 1: Deploy to Heroku (Easiest)

#### 1. Install Heroku CLI
```bash
# Windows
choco install heroku-cli

# macOS
brew tap heroku/brew && brew install heroku
```

#### 2. Create Heroku App
```bash
heroku login
heroku create your-app-name
```

#### 3. Create Procfile
Create `Server/Procfile`:
```
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

#### 4. Update requirements.txt
Add:
```
gunicorn>=21.0.0
psycopg2-binary>=2.9.0
```

#### 5. Set Environment Variables
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=postgresql://...
heroku config:set CORS_ORIGINS=https://your-domain.com
heroku config:set DEBUG=False
```

#### 6. Deploy
```bash
git push heroku main
heroku logs --tail  # View logs
```

---

### Option 2: Deploy to AWS EC2

#### 1. Launch EC2 Instance
- OS: Ubuntu 22.04 LTS
- Instance type: t3.medium (minimum)
- Storage: 20GB SSD
- Security group: Allow ports 80, 443, 22

#### 2. Connect to Instance
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 3. Install Dependencies
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip \
  postgresql postgresql-contrib git nginx supervisor

# For GPU support if available:
sudo apt install nvidia-driver-545
```

#### 4. Clone Repository
```bash
git clone https://github.com/your-repo/airball.git
cd airball/Server
```

#### 5. Setup Python Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### 6. Configure PostgreSQL
```bash
sudo -u postgres psql
postgres=# CREATE DATABASE airball;
postgres=# CREATE USER airball_user WITH PASSWORD 'strong-password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE airball TO airball_user;
postgres=# \q
```

#### 7. Create .env File
```bash
cat > .env << EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
DATABASE_URL=postgresql://airball_user:strong-password@localhost/airball
CORS_ORIGINS=https://your-domain.com
DEBUG=False
OLLAMA_BASE_URL=http://localhost:11434
EOF
chmod 600 .env
```

#### 8. Configure Gunicorn with Supervisor
Create `/etc/supervisor/conf.d/airball.conf`:
```ini
[program:airball]
directory=/home/ubuntu/airball/Server
command=/home/ubuntu/airball/Server/venv/bin/gunicorn \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  app.main:app
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/airball.log
```

Start service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start airball
```

#### 9. Configure Nginx
Create `/etc/nginx/sites-available/airball`:
```nginx
upstream airball {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    client_max_body_size 500M;

    location / {
        proxy_pass http://airball;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ubuntu/airball/Server/static/;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/airball /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Option 3: Docker Deployment

#### 1. Create Dockerfile
Create `Server/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: airball
      POSTGRES_USER: airball_user
      POSTGRES_PASSWORD: strong-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - airball-network

  backend:
    build: ./Server
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://airball_user:strong-password@db:5432/airball
      SECRET_KEY: ${SECRET_KEY}
      CORS_ORIGINS: https://your-domain.com
      DEBUG: "False"
    depends_on:
      - db
    volumes:
      - ./Server/uploads:/app/uploads
      - ./Server/shots:/app/shots
    networks:
      - airball-network

  frontend:
    build: ./client
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_BASE_URL: https://api.your-domain.com
    networks:
      - airball-network

volumes:
  postgres_data:

networks:
  airball-network:
    driver: bridge
```

#### 3. Run with Docker
```bash
# Add SECRET_KEY to .env
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" > .env

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f backend
```

---

## Frontend Deployment

### Option 1: Deploy to Vercel (Easiest)

#### 1. Push to GitHub
```bash
git remote add origin https://github.com/your-repo/airball.git
git push -u origin main
```

#### 2. Import on Vercel
- Go to vercel.com
- Click "Import Project"
- Select your GitHub repository
- Configure:
  - **Root Directory**: `client`
  - **Build Command**: `npm run build`
  - **Output Directory**: `.next`

#### 3. Set Environment Variables
In Vercel project settings:
```
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
```

#### 4. Deploy
- Vercel automatically deploys on push to main

---

### Option 2: Deploy to Netlify

#### 1. Install Netlify CLI
```bash
npm install -g netlify-cli
```

#### 2. Build Locally
```bash
cd client
npm run build
```

#### 3. Deploy
```bash
netlify deploy --prod
# Select client directory
# Set build command: npm run build
# Set publish directory: .next
```

#### 4. Configure
Set environment variable in Netlify:
```
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
```

---

### Option 3: Manual Deployment to Server

#### 1. Build Frontend
```bash
cd client
npm install
npm run build
```

#### 2. Copy to Server
```bash
# Via SFTP or SCP
scp -r client/.next user@server:/var/www/airball/
scp -r client/public user@server:/var/www/airball/
scp client/package.json user@server:/var/www/airball/
```

#### 3. Run on Server
```bash
cd /var/www/airball
npm install --production
npm start
```

---

## Database Setup

### PostgreSQL on Production

#### 1. Create Database and User
```bash
sudo -u postgres psql

postgres=# CREATE DATABASE airball;
postgres=# CREATE USER airball_user WITH PASSWORD 'strong-password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE airball TO airball_user;

postgres=# \c airball
airball=# CREATE SCHEMA IF NOT EXISTS airball;
```

#### 2. Configure PostgreSQL Security
Edit `/etc/postgresql/14/main/pg_hba.conf`:
```
local   airball     airball_user     md5
host    airball     airball_user     127.0.0.1/32     md5
host    airball     airball_user     ::1/128          md5
```

Restart:
```bash
sudo systemctl restart postgresql
```

#### 3. Database Backups
Create backup script `/home/ubuntu/backup-airball.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/backups/airball"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump -U airball_user airball > $BACKUP_DIR/airball_$TIMESTAMP.sql
gzip $BACKUP_DIR/airball_$TIMESTAMP.sql

# Keep only last 30 days
find $BACKUP_DIR -name "airball_*.sql.gz" -mtime +30 -delete
```

Schedule with cron:
```bash
crontab -e
# Add: 0 2 * * * /home/ubuntu/backup-airball.sh
```

#### 4. Update DATABASE_URL
```bash
export DATABASE_URL=postgresql://airball_user:password@localhost:5432/airball
```

---

## SSL/HTTPS

### Using Let's Encrypt (Free)

#### 1. Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

#### 2. Generate Certificate
```bash
sudo certbot certonly --nginx -d your-domain.com -d api.your-domain.com
```

#### 3. Update Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Rest of configuration...
}
```

#### 4. Auto-Renewal
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Environment Configuration

### Backend Production Environment

Create `.env.production`:
```
# Security
SECRET_KEY=your-generated-secret-key
DEBUG=False

# Database
DATABASE_URL=postgresql://airball_user:password@db-host:5432/airball

# CORS
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Logging
LOG_LEVEL=INFO

# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Media
MAX_VIDEO_SIZE=524288000  # 500MB
UPLOAD_DIRECTORY=/var/airball/uploads
SHOTS_DIRECTORY=/var/airball/shots
```

### Frontend Production Environment

Create `client/.env.production`:
```
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
NEXT_PUBLIC_APP_NAME=AirBall
NEXT_PUBLIC_APP_URL=https://your-domain.com
```

---

## Monitoring & Maintenance

### Server Health Checks

```bash
# Check backend
curl https://api.your-domain.com/health

# Check frontend
curl https://your-domain.com

# Check database
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('airball'));"
```

### Log Management

View logs:
```bash
# Supervisor logs if using supervior
tail -f /var/log/airball.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# PostgreSQL logs
tail -f /var/log/postgresql/postgresql.log
```

### Storage Monitoring

```bash
# Check upload directory size
du -sh /var/airball/uploads

# Check disk usage
df -h

# Clean old videos (older than 30 days)
find /var/airball/uploads -type f -mtime +30 -delete
```

### Performance Monitoring

```bash
# CPU/Memory usage
top

# Network connections
netstat -an | grep :8000

# Database connections
sudo -u postgres psql -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

### Automated Monitoring (Optional)

Use tools like:
- **Prometheus** + **Grafana** for metrics
- **ELK Stack** (Elasticsearch, Logstash, Kibana) for logs
- **New Relic** or **DataDog** for APM

---

## Troubleshooting

### Issue: 502 Bad Gateway
**Cause**: Backend not running, connection error  
**Solution**:
```bash
# Check if backend is running
sudo supervisorctl status airball

# Check logs
tail -f /var/log/airball.log

# Restart
sudo supervisorctl restart airball
```

### Issue: High Memory Usage
**Cause**: YOLO models not released, memory leak  
**Solution**:
```bash
# Monitor memory
watch -n 1 'ps aux | grep gunicorn'

# Restart service
sudo supervisorctl restart airball

# Reduce YOLO model size in ball_detector.py
# Use yolov8n instead of yolov8m
```

### Issue: Database Connection Error
**Cause**: PostgreSQL misconfiguration, network issue  
**Solution**:
```bash
# Test connection
psql postgresql://airball_user:password@localhost/airball

# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Issue: Certificate Expired
**Cause**: Let's Encrypt certificate not renewed  
**Solution**:
```bash
# Manual renewal
sudo certbot renew

# Check renewal status
sudo certbot renew --dry-run
```

### Issue: CORS Errors
**Cause**: Frontend origin not in CORS whitelist  
**Solution**:
```bash
# Update CORS_ORIGINS environment variable
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Restart backend
sudo supervisorctl restart airball
```

---

## Rollback Procedure

If deployment fails:

### Git Rollback
```bash
# View recent commits
git log --oneline

# Rollback to previous version
git reset --hard <commit-hash>
git push origin main --force

# Or revert last commit
git revert HEAD
git push origin main
```

### Database Rollback
```bash
# List backups
ls -la /backups/airball/

# Restore from backup
gunzip /backups/airball/airball_YYYYMMDD_HHMMSS.sql.gz
psql -U airball_user airball < /backups/airball/airball_YYYYMMDD_HHMMSS.sql
```

### Docker Rollback
```bash
# Use previous image tag
docker-compose down
docker-compose -f docker-compose.yml pull
docker-compose -f docker-compose.yml up -d
```

---

## Scaling Considerations

As traffic grows:

### Horizontal Scaling
- Multiple backend instances behind load balancer
- Use Nginx reverse proxy or AWS ELB
- Shared PostgreSQL database

### Vertical Scaling
- Upgrade EC2 instance type
- Add more CPU/RAM
- Enable GPU for faster video processing

### Optimization
- Cache frequently accessed data (Redis)
- Use CDN for frontend assets (CloudFlare)
- Optimize YOLO inference (quantization, pruning)
- Implement request rate limiting

---

## Security Best Practices

- [ ] Use HTTPS/SSL everywhere
- [ ] Validate all user input
- [ ] Never store secrets in code
- [ ] Use strong database passwords
- [ ] Enable WAF (Web Application Firewall)
- [ ] Regular security updates
- [ ] Database backups encrypted
- [ ] Audit logs enabled
- [ ] API rate limiting
- [ ] Request size limits

---

## Post-Deployment

1. **Verify Services**
   ```bash
   curl https://api.your-domain.com/health
   curl https://your-domain.com
   ```

2. **Test Full Workflow**
   - Upload test video
   - Verify processing completes
   - Check API responses
   - Validate database records

3. **Monitor**
   - Watch logs for errors
   - Monitor resource usage
   - Check backup completion

4. **Communicate**
   - Update status page
   - Notify users
   - Document configuration

---

**Last Updated**: February 2026  
**Version**: 1.0.0
