# Notes & Ideas

## Performance Issues to Fix
- [ ] Log queries getting slow with > 10k entries - add pagination properly
- [ ] Redis caching not working on first deploy - need to handle connection failures better
- [ ] Frontend re-renders too much on dashboard - useMemo?

## Bugs Found
- Password verification had encoding issues initially (fixed in commit f10f9bd)
- Alert status updates weren't persisting - had to add db.commit() manually
- WebSocket disconnects randomly - probably need reconnection logic

## Things I Should Refactor
- The filter builder in logs.py is ugly - should be a query builder class
- Variable naming inconsistent (threats vs threats_detected)
- Too many print statements for errors - need proper logging
- Rate limits probably too strict - getting complaints from testers

## ML Model Notes
- Started with simple threshold approach (accuracy ~60%)
- Switched to Random Forest (much better ~85%)
- Synthetic data generation works but real data would be better
- Model sometimes fails to load on cold start - fallback to heuristics saves us

## Security Todos
- [ ] Add email verification on registration
- [ ] Switch from localStorage to httpOnly cookies
- [ ] Implement refresh tokens
- [ ] Add 2FA support

## Ideas for v2
- Multi-tenancy support
- Slack/Teams integration for alerts
- More granular RBAC permissions
- Dark mode (everyone wants this)
- Mobile app?

---
*Last updated: Jan 15, 2026*
