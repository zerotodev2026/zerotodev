#!/bin/bash
# ============================================
# ZeroToDev 一键部署脚本
# 构建 + 发布到 Cloudflare Pages
# ============================================

set -e

echo "🚀 开始部署 ZeroToDev 个人网站..."
echo ""

# 1. 构建站点
echo "📦 构建静态站点..."
pelican content -o output -s publishconf.py
echo "✅ 构建完成"
echo ""

# 2. 部署到 Cloudflare Pages
echo "☁️  上传到 Cloudflare Pages..."
npx wrangler pages deploy output --project-name zerotodev --branch main
echo ""
echo "🎉 部署完成！访问 https://zerotodev-4jq.pages.dev"
