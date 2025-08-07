#!/bin/bash
# Deployment script for Nine Square web version

echo "🚀 Deploying Nine Square to GitHub Pages..."

# Create and switch to gh-pages branch
git checkout -b gh-pages 2>/dev/null || git checkout gh-pages

# Add web files
git add index.html ninesquare.js
git commit -m "Deploy web version of Nine Square game"

# Push to GitHub Pages
git push origin gh-pages

echo "✅ Deployment complete!"
echo "🌐 Your game will be available at: https://klemtek.github.io/ninesquare"
echo "📝 Don't forget to enable GitHub Pages in your repository settings!"

# Switch back to main branch
git checkout main
