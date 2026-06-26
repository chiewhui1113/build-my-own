# Build Your Own Container (Go) — Learning Summary

A container is basically a normal Linux process running with isolated namespaces, 
a swapped root filesystem, and resource limits.

**Difficulty:** ⭐⭐ — simple and concise code implementation of namespaces/cgroups.

## How it works

The program re-runs itself to set up isolation before launching your command:

- `run` (parent) — forks a copy of itself (`/proc/self/exe child ...`) and asks
  the kernel for new namespaces via `Cloneflags`
- `child` — runs inside the new namespaces, sets up the container environment,
  then `exec`s the command you asked for

Key building blocks:

- **Namespaces** — `CLONE_NEWUTS` (own hostname), `CLONE_NEWPID` (own process IDs,
  so the container sees its process as PID 1), `CLONE_NEWNS` (own mount table)
- **`Sethostname`** — gives the container its own hostname without touching the host
- **`Chroot` + `Chdir`** — swaps the root filesystem to an extracted image
  (`/vagrant/ubuntu-fs`) so the container only sees its own files
- **Mount `proc`** — gives the container a working `/proc` (so tools like `ps` work)
- **cgroups** (`cg`) — limits resources by writing to `/sys/fs/cgroup`, e.g. capping
  the container to 20 processes via `pids.max`

## Key things I learned

- A container is just a process the kernel isolates with namespaces
- How `chroot` + namespaces + cgroups combine to give the "looks like its own
  machine" illusion
- The parent/child re-exec trick for applying namespaces before running a command

## Run it

```bash
# On a Linux host, as root:
go run main.go run /bin/bash
```

Source tutorial: [Liz Rice, *Containers From Scratch* (GOTO / YouTube)](https://www.youtube.com/watch?v=8fi7uSYlOdc)
