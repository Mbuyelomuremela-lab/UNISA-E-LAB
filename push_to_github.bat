@echo off
REM Push the current project to GitHub.
REM 1. Install Git from https://git-scm.com if not installed.
REM 2. Create a GitHub repository on github.com.
REM 3. Set the REPO_URL below to your repository URL.

set REPO_URL=https://github.com/YOUR_USERNAME/YOUR_REPO.git

if not exist .git (
    git init
)
git add .
git commit -m "Initial commit"
git branch -M main
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git push -u origin main
pause
