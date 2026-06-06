# Learnings

This document captures the key technical lessons and debugging moments from building TaskFlow. It is written for myself, as a reference, and as preparation for explaining the work in interviews.

## What I Set Out To Build

A two-tier web application deployed end-to-end with a working CI/CD pipeline, using the tools real DevOps teams use: Docker, Jenkins, AWS, and pytest. The application itself (a task management tool) is the thing being deployed; my work focused on the infrastructure and automation around it.

## Concepts I Internalized

### The "12-Factor App" mindset

Storing configuration in environment variables, not code, is not just a convention - it's what makes the same image deployable to dev, staging, and production with zero code changes. My `.env` file is gitignored and never lives in source control; the `.env.example` is the contract that documents what the app expects.

### Container networking is its own discipline

The pipeline's first health check failed because `curl http://localhost:5000/health` inside the Jenkins container couldn't reach the Flask container - "localhost" referred to Jenkins itself, not the host or the Flask container. Switching to `docker inspect --format='{{.State.Health.Status}}' taskflow-web` worked because it uses Docker's own health tracking rather than network calls. This is a small example of a broader principle: when you containerize, the meaning of "local" changes.

### Layer caching is performance

The Dockerfile copies `requirements.txt` before copying the rest of the code, then installs dependencies. When the application code changes but dependencies don't, Docker reuses the cached dependency layer and rebuilds in seconds instead of minutes. The build log shows `CACHED` next to each unchanged layer - that's the optimization paying off.

### Pipeline as code

The `Jenkinsfile` lives in the repo. Changing the pipeline is a commit. Reviewing pipeline changes is a code review. Rolling back a bad pipeline change is a `git revert`. The pipeline is treated as software - because it is.

### Tests before deploys, not after

Adding the Test stage to the pipeline taught me what CI actually means. Without the gate, you have continuous deployment of whatever code you push - including bugs. With the gate, a failing test stops the line. The container build never runs, the deploy never happens, the live app stays clean.

## Problems I Solved

These are not theoretical. They were genuine blockers I worked through.

### Expired GPG signing key on apt

The Jenkins apt repository's signing key had expired (key `7198F4B714ABFC68`). Multiple attempts to re-import via keyserver failed because `dirmngr` wasn't installed. I pivoted to running Jenkins as a Docker container, which sidestepped the entire apt path. The lesson: when an installation path keeps fighting you, ask whether there's a fundamentally different approach.

### Docker socket permission inside Jenkins container

Mounting `/var/run/docker.sock` into Jenkins gave it visibility, but the `jenkins` user inside the container didn't belong to a group with permission to use the socket. The fix was to find the host's `docker` group GID (`getent group docker` → `986`) and pass `--group-add 986` to the Jenkins `docker run` command. Now I understand: container users live in their own namespace, but socket permissions are evaluated against the host kernel's group IDs.

### Docker CLI keeps disappearing on container recreate

Three times I installed the Docker CLI inside the running Jenkins container, and three times it vanished on recreation. That tedium taught me what Docker images actually are: a recreated container starts from the image's contents, not the previous container's state. The fix was to build a custom image (`taskflow-jenkins:latest`) with the CLI baked into a `RUN` instruction in the Dockerfile. Now the CLI is part of the image itself and survives any number of recreations.

### Network port blocked between browser and Jenkins

After confirming Jenkins was healthy locally (`curl localhost:8080` returned 200), the browser still couldn't reach it on the public IP. Port 8080 was likely blocked by my ISP or local network. I used an SSH tunnel (`ssh -L 8080:localhost:8080`) to forward Jenkins through the SSH connection. This is now my permanent access method - and a security best practice. Jenkins admin is never exposed to the public internet.

### Python version incompatibility for tests

My local Python was 3.9, but the code used `str | None` syntax which was introduced in 3.10. Tests failed to import. I changed the signatures to `Optional[str]` from the `typing` module, which works in 3.9 and 3.10+. The fix didn't compromise the production environment (which runs 3.11) and made the code more broadly compatible.

### `mysqlclient` won't compile on macOS

The `flask-mysqldb` package requires MySQL client libraries and `pkg-config` to compile, which my Mac didn't have. Rather than install MySQL on the Mac just for testing, I created a `requirements-test.txt` that excludes the MySQL driver and mocked `flask_mysqldb` in `conftest.py` before any tests import the application package. Tests now run on any machine with Python and pytest installed, including Jenkins's ephemeral test containers.

### Git history attributed to the wrong author

For the first 51 commits, my git config had a name set but no email, so git auto-generated `zohaib@Zohaibs-MacBook-Air.local` as the author email. GitHub couldn't link these commits to my account - they didn't appear on my contribution graph or show my profile when clicked. I used `git filter-branch` to rewrite the author and committer fields across all commits to my GitHub-recognized email, then force-pushed. All 52 commits are now properly attributed. The lesson: verify your git identity before your first commit, not after fifty of them.

## Mistakes I Made (And What They Taught Me)

- **Skipping verifications.** Early on I'd say "all good" and move forward, then discover a problem three steps later. The fix is the same one real engineers use: never trust, always verify. Run the check command, read the output, then proceed.

- **Pasting tool output as a command.** Multiple times I copied something I was supposed to see (like a list of files) and pasted it into the terminal, triggering "command not found" errors. Now I read prompts carefully and distinguish "things to type" from "things to expect to see."

- **Committing before verifying the diff.** I once force-pushed a bad change because I didn't read `git diff --cached` first. The habit now: always inspect the diff before committing, every time, even for trivial changes.

## What I Would Do Differently

If I started over:

1. **Provision the EC2 with Terraform from day one.** Configuration through the AWS console is fast initially but becomes a "what did I click again?" black box. IaC turns it into reviewable code.

2. **Build the custom Jenkins image earlier.** I wasted time re-installing the Docker CLI three times before realizing the actual fix was to bake it into an image.

3. **Set up the SSH tunnel from the start.** I tried to make Jenkins publicly accessible via security group rules and fought network blocking. The tunnel approach is both simpler and more secure - it should have been the default from the start.

4. **Write `LEARNINGS.md` continuously.** This document was written at the end, partly from memory. Some debugging stories are sharper than others because I happened to capture more detail. I'd keep notes during the work next time.

## What This Project Doesn't Cover (Honest Scope)

To be straightforward about the boundaries of what I built:

- **I am not the author of the application logic.** Flask, the routes, the models - I understand them and can explain how they fit together, but I treated the application as the thing being deployed, not the thing being designed from product principles. My contribution is the infrastructure and automation around it.

- **The DevOps and AWS work is mine end to end.** The Dockerfile, the docker-compose.yml, the Jenkinsfile, the EC2 setup, the security group decisions, the test suite, the custom Jenkins image, the debugging - all of that I built, understood, and can explain in detail.

- **Production-grade features are intentionally out of scope.** No HTTPS, no autoscaling, no secrets manager, no real monitoring. The architecture document lists these as known limitations. A portfolio project demonstrates understanding; a production system requires investment I haven't put in here.

## Skills I'd Now Claim On A Resume

After building this, I can honestly say I have working experience with:

- Docker and Docker Compose for multi-container application deployment
- Building custom Docker images via Dockerfiles
- Jenkins pipeline development using declarative `Jenkinsfile` syntax
- CI/CD pipeline design (gating deploys on test results, health checks before traffic)
- AWS EC2: provisioning, security groups, key pair management, SSH access
- Linux administration: swap configuration, systemd-managed services, user/group permissions
- Git: feature branching, atomic commits, history rewriting with `filter-branch`, force-push with care
- Pytest: unit tests, fixtures, mocking external dependencies (`conftest.py` with `sys.modules` injection)
- Bash scripting in pipeline steps (loops, exit codes, conditionals)
- Debugging containerized systems (logs, `docker exec`, `docker inspect`, network isolation issues)

## The Single Most Valuable Lesson

In a real team, the difference between "it works on my machine" and "it works in production" is not skill - it's discipline. Verify each step. Read the actual output. Commit small, atomic changes. Document as you go. The flashy parts of DevOps (the CI/CD pipeline, the green checkmarks) are downstream of those habits, not a substitute for them.
