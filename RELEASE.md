# Release Process

This document describes how to release a new version of django-testcontainers-plus to PyPI.

## Prerequisites

### 1. Set up PyPI API Token

Before you can publish to PyPI, you need to configure a PyPI API token as a GitHub secret.

#### Generate PyPI Token

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Scroll down to "API tokens"
3. Click "Add API token"
4. Give it a name (e.g., "django-testcontainers-plus-github-actions")
5. Set the scope:
   - **For first release**: Select "Entire account" scope
   - **For subsequent releases**: After first publish, create a project-scoped token for `django-testcontainers-plus`
6. Click "Add token"
7. **IMPORTANT**: Copy the token immediately (it starts with `pypi-`)
   - You won't be able to see it again!

#### Add Token to GitHub Secrets

1. Go to your GitHub repository
2. Click "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Name: `PYPI_API_TOKEN`
5. Value: Paste the token you copied from PyPI (including the `pypi-` prefix)
6. Click "Add secret"

### 2. Verify Version Numbers

Before releasing, ensure the version number is consistent across:

- `pyproject.toml` (line 3)
- `src/django_testcontainers_plus/__init__.py` (line 7)

The version should follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., `0.1.2`)
- `MAJOR.MINOR.PATCH-alpha.N` for alpha releases
- `MAJOR.MINOR.PATCH-beta.N` for beta releases
- `MAJOR.MINOR.PATCH-rc.N` for release candidates

## Release Process

### 1. Update Version Numbers

Update the version in both files:

```bash
# Example: updating to version 0.2.0
# Edit pyproject.toml
sed -i 's/version = ".*"/version = "0.2.0"/' pyproject.toml

# Edit __init__.py
sed -i 's/__version__ = ".*"/__version__ = "0.2.0"/' src/django_testcontainers_plus/__init__.py
```

### 2. Commit Version Changes

```bash
git add pyproject.toml src/django_testcontainers_plus/__init__.py
git commit -m "chore: bump version to 0.2.0"
git push origin main
```

### 3. Create and Push Tag

```bash
# Create annotated tag
git tag -a v0.2.0 -m "Release version 0.2.0"

# Push tag to GitHub
git push origin v0.2.0
```

### 4. Monitor GitHub Actions

Once you push the tag:

1. Go to the "Actions" tab in your GitHub repository
2. You should see the "Publish to PyPI" workflow running
3. The workflow will:
   - ✅ Verify the tag version matches `pyproject.toml`
   - ✅ Build the package
   - ✅ Test the built package
   - ✅ Publish to PyPI
   - ✅ Create a GitHub Release with changelog

### 5. Verify Publication

After the workflow completes:

1. Check PyPI: https://pypi.org/project/django-testcontainers-plus/
2. Check GitHub Releases: https://github.com/woodywoodster/django-testcontainers-plus/releases
3. Test installation:
   ```bash
   pip install django-testcontainers-plus==0.2.0
   ```

## Troubleshooting

### "403 Forbidden" Error on PyPI Upload

**Cause**: Invalid or missing PyPI token.

**Solution**:
1. Verify the `PYPI_API_TOKEN` secret exists in GitHub Settings
2. Ensure the token starts with `pypi-`
3. Generate a new token if needed and update the secret

### "Version already exists" Error

**Cause**: The version has already been published to PyPI.

**Solution**:
1. You cannot overwrite a published version
2. Increment the version number
3. Commit changes and create a new tag

### Tag and Version Mismatch Error

**Cause**: The git tag version doesn't match the version in `pyproject.toml`.

**Solution**:
1. Delete the incorrect tag: `git tag -d v0.2.0 && git push origin :refs/tags/v0.2.0`
2. Update version in both files
3. Commit and create the tag again

### CI Tests Failing

**Cause**: The CI workflow must pass before publishing.

**Solution**:
1. Fix the failing tests
2. Push fixes to main
3. Delete and recreate the tag after tests pass

## Pre-release Versions

For alpha, beta, or release candidate versions:

```bash
# Alpha release
git tag -a v0.2.0-alpha.1 -m "Release version 0.2.0-alpha.1"

# Beta release
git tag -a v0.2.0-beta.1 -m "Release version 0.2.0-beta.1"

# Release candidate
git tag -a v0.2.0-rc.1 -m "Release version 0.2.0-rc.1"
```

These will be marked as "pre-release" on GitHub automatically.

## Rollback

If you need to rollback a release:

1. **PyPI**: You cannot delete versions, but you can "yank" them:
   ```bash
   # Install twine if not already installed
   pip install twine

   # Yank the version (makes it unavailable for new installations)
   twine yank django-testcontainers-plus -v 0.2.0 -r pypi
   ```

2. **GitHub Release**: Delete the release from the GitHub Releases page

3. **Git Tag**: Delete the tag:
   ```bash
   git tag -d v0.2.0
   git push origin :refs/tags/v0.2.0
   ```

## Best Practices

1. **Always run tests locally** before creating a release tag
2. **Review the changelog** that will be auto-generated from git commits
3. **Use meaningful commit messages** (they appear in the release notes)
4. **Test in a staging environment** before tagging a stable release
5. **Create alpha/beta releases** for major changes
6. **Never force-push** to tags
7. **Keep versions synchronized** across `pyproject.toml` and `__init__.py`

## Quick Reference

```bash
# Update version
vim pyproject.toml src/django_testcontainers_plus/__init__.py

# Commit and tag
git add pyproject.toml src/django_testcontainers_plus/__init__.py
git commit -m "chore: bump version to X.Y.Z"
git push origin main
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin vX.Y.Z

# Watch the magic happen in GitHub Actions! 🚀
```
