# XAI Urban Traffic Management Dashboard

## Overview
Backend: Django 5 + DRF + MySQL 8.0
Frontend: Vue 3 + Vite + ECharts + Tailwind CSS
XAI: SHAP (KernelExplainer) + LIME (LimeTabularExplainer)
Python 3.12

## Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py init_data  # Load and process CSV data
python manage.py runserver 0.0.0.0:8000 # 开发环境启动命令

# Frontend
cd frontend
npm install
npm run dev

# 缺api和功能：StatsView接口和对应的功能
```
