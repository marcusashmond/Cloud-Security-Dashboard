# Development Log

## May 2025

### May 18
Started the cloud security dashboard project. Set up basic project structure. Spent way too long deciding between FastAPI vs Flask. Going with FastAPI for async support.

### May 20
Got basic FastAPI backend running with PostgreSQL. User model and database setup complete. Authentication is next.

## June 2025

### June 2
Implemented JWT authentication. Password hashing with bcrypt working. Had to read docs 3 times to understand the token refresh flow properly.

### June 3
Struggled with SQLAlchemy imports - some deprecated warnings. Fixed after upgrading to 2.0 syntax.

### June 15
Authentication working! Spent all day on password verification bug - turns out I was encoding the hash wrong. Finally figured it out around midnight.

Frontend: Started Next.js 14 setup. App router is confusing compared to pages.

### June 28
Built logs API endpoints. Pagination was harder than expected. Took a break for a week - burnout.

## July 2025

### July 5
Back at it. Set up Next.js project properly this time. TypeScript configs are still annoying.

### July 8
Fighting with TypeScript strict mode. Types everywhere. Considering just using 'any' but that defeats the purpose.

### July 18
Dashboard layout done. Added logs table component. Real-time updates would be nice but WebSocket seems overkill right now.

### July 22
Logs table looking good. Added filtering and sorting. Performance is okay with small datasets.

### July 28
Started WebSocket for real-time logs. Connection keeps dropping. Frustrating.

### July 29
Finally got WebSocket working at 2 AM. The issue was nginx proxy config (wasn't even using nginx yet lol). Just needed proper timeout settings.

## August 2025

### Aug 5
Analytics endpoints complete. Building charts on frontend. Chart.js vs Recharts decision took too long.

### Aug 6
Code cleanup. Variable naming was all over the place. Fixed some but not all - 'meh, good enough'.

### Aug 15
Started threat detection. Simple threshold approach first - just check if failed_count > 5. Way too many false positives though.

### Aug 25
Switched to Random Forest classifier. Much better! Accuracy around 94% on test data. The synthetic data generation is hacky but works.

Took 2 weeks off to think about the ML approach. Should probably use real data but don't have any.

## September 2025

### Sep 8
Added pytest tests. Test coverage at 60%. Should probably write more tests but testing is boring.

### Sep 15
Frontend tests with Jest. Testing async components is painful. Half the tests are just mocking fetch calls.

### Sep 22
Dockerized everything. docker-compose makes it easy to run locally. Production deployment will be different though.

## October 2025

### Oct 5
Integrated Redis for caching. Connection pooling was tricky. Failover isn't perfect - if Redis dies the app should still work but sometimes crashes. TODO: fix this.

### Oct 6
Added better error handling in Redis client. Comments explain the messy parts.

### Oct 18
RBAC time. Implemented 3 roles: admin, analyst, auditor. Permission decorators are elegant. Proud of this code.

### Oct 28
Rate limiting with Redis. Used token bucket algorithm. Limits are probably too strict (10 req/min) but can tune based on real usage.

## November 2025

### Nov 10
Audit logging for compliance. Every sensitive action gets logged. Database is going to grow fast - need log rotation strategy.

### Nov 20
Documentation day. README, deployment guide, feature docs. Writing is harder than coding.

### Nov 25
More docs. Added showcase and features markdown. Portfolio ready.

## December 2025

### Dec 5
Added personal notes file and this devlog. Good to document the journey.

### Dec 10
Code review on myself lol. Added TODO comments and kept some debug statements. Code isn't perfect but it's real.

## January 2026

### Jan 8
Final documentation for enterprise features. This project has everything now.

### Jan 12
Fixed linting config. 700+ markdown errors were annoying.

### Jan 15
Last formatting fixes in README. Project complete!

## Known Issues
- Logs table query inefficient with large datasets
- Auto-refresh might be annoying
- Redis connection handling needs work
- Some TODO comments scattered around

## What Went Well
- FastAPI is actually nice to work with
- Next.js App Router is way better than Pages
- Docker setup worked first try (surprising)
- ML model accuracy better than expected

## What Was Hard
- Getting WebSocket to work properly
- Rate limiting configuration (still not perfect)
- Deciding on permission granularity for RBAC
- Making fake data look realistic
