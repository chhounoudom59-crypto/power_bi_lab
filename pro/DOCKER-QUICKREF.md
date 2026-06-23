# Quick Command Reference

## Docker Quick Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run ETL once
docker-compose run --rm etl_pipeline python etl_pipeline.py docker-config.json

# Access database
psql -h localhost -p 5432 -U postgres -d lms-prod
```

## Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| PgAdmin | http://localhost:5050 | admin@example.com / admin |
| Source DB | localhost:5432 | postgres / postgres_source_password |
| Target DB | localhost:5433 | postgres / postgres_target_password |

## File Configuration

- **docker-compose.yml** - Container orchestration
- **Dockerfile** - ETL application image
- **docker-config.json** - Docker-specific database config
- **config.json** - Local machine config
- **DOCKER.md** - Full Docker documentation

## Typical Workflow

1. **Start services:**
   ```bash
   docker-compose up -d
   ```

2. **View pipeline logs:**
   ```bash
   docker-compose logs -f etl_pipeline
   ```

3. **Run manual ETL:**
   ```bash
   docker-compose run --rm etl_pipeline python etl_pipeline.py docker-config.json
   ```

4. **Access databases via PgAdmin:**
   - Open http://localhost:5050
   - Log in with admin/admin
   - Connect to postgres_source or postgres_target

5. **Stop services:**
   ```bash
   docker-compose down
   ```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Services won't start | `docker-compose down -v` then `docker-compose up` |
| Can't connect to DB | Use localhost:5432 (source) or localhost:5433 (target) |
| Out of memory | `docker system prune -a` |
| Permission denied | May need to run with `sudo` on Linux |

See [DOCKER.md](DOCKER.md) for complete documentation.
