# Docker Setup for Canvas API Server

## Why Docker?

Docker provides:
- ✅ **Automatic restarts** - Server restarts if it crashes
- ✅ **Process isolation** - Won't interfere with other processes
- ✅ **Consistent environment** - Same setup everywhere
- ✅ **Easy management** - Simple start/stop commands
- ✅ **Health checks** - Automatic monitoring

## Quick Start

### 1. Install Docker

**macOS:**
```bash
# Install Docker Desktop from:
# https://www.docker.com/products/docker-desktop
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Or use Docker's official repository
```

### 2. Start the Server

```bash
cd /Users/a00288946/Projects/canvas_2879
chmod +x run-docker-server.sh
./run-docker-server.sh
```

That's it! The server will:
- Build the Docker image (first time only)
- Start the container
- Automatically restart if it crashes
- Run in the background

### 3. Verify It's Running

```bash
curl http://localhost:5000/health
```

Should return: `{"status": "ok"}`

## Docker Commands

### View Logs
```bash
docker-compose logs -f
# or
docker compose logs -f
```

### Stop Server
```bash
docker-compose down
# or
docker compose down
```

### Restart Server
```bash
docker-compose restart
# or
docker compose restart
```

### Rebuild (after code changes)
```bash
docker-compose up -d --build
# or
docker compose up -d --build
```

### Check Status
```bash
docker-compose ps
# or
docker compose ps
```

## Configuration

The Docker setup automatically:
- ✅ Mounts `.box-api-config.json` (Box OAuth credentials)
- ✅ Mounts `config.toml` (Canvas configuration)
- ✅ Mounts `WINTER 25-26 COURSE UPDATES/` (HTML files for updates)
- ✅ Exposes port 5000 for API access

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs
```

**Common issues:**
1. **Port 5000 already in use:**
   ```bash
   # Kill existing process
   lsof -ti:5000 | xargs kill -9
   # Or change port in docker-compose.yml
   ```

2. **Missing config files:**
   - Make sure `.box-api-config.json` exists
   - Make sure `config.toml` exists

3. **Permission errors:**
   ```bash
   # Make sure Docker has access to files
   chmod 644 .box-api-config.json config.toml
   ```

### Container Keeps Restarting

**Check health status:**
```bash
docker-compose ps
```

**View detailed logs:**
```bash
docker-compose logs --tail=100
```

**Common causes:**
- Missing or invalid OAuth token
- Missing or invalid Canvas config
- Python import errors

### Update Code

After making code changes:

```bash
# Rebuild and restart
docker-compose up -d --build
```

## Comparison: Docker vs Direct Python

| Feature | Docker | Direct Python |
|---------|--------|---------------|
| Auto-restart | ✅ Yes | ❌ No |
| Process isolation | ✅ Yes | ❌ No |
| Easy management | ✅ Yes | ⚠️ Manual |
| Resource usage | ⚠️ Slightly higher | ✅ Lower |
| Setup complexity | ⚠️ One-time setup | ✅ Simple |

## Production Deployment

For production, you can:
1. Push the Docker image to a registry
2. Deploy to cloud services (AWS, Google Cloud, etc.)
3. Use orchestration (Kubernetes, Docker Swarm)

The `docker-compose.yml` is already configured for production with:
- Health checks
- Automatic restarts
- Proper volume mounts

## Next Steps

1. **Start the Docker server:**
   ```bash
   ./run-docker-server.sh
   ```

2. **Start the web server** (in a separate terminal):
   ```bash
   cd docs
   python3 -m http.server 8000
   ```

3. **Access your site:**
   ```
   http://localhost:8000
   ```

The API server will now be stable and automatically restart if it crashes!

