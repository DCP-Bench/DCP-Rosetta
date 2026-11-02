/* Preloaded during builds by tools/podman/docker. In a single-uid rootless namespace a
 * chown to any other owner fails with EINVAL, which breaks tar and some dpkg scripts.
 * Ownership is squashed to root anyway, so every chown variant succeeds as a no-op.
 * Built without libc (-nostdlib) so the same file loads in any glibc image. */
int chown(const char *path, unsigned uid, unsigned gid) { return 0; }
int lchown(const char *path, unsigned uid, unsigned gid) { return 0; }
int fchown(int fd, unsigned uid, unsigned gid) { return 0; }
int fchownat(int fd, const char *path, unsigned uid, unsigned gid, int flags) { return 0; }
