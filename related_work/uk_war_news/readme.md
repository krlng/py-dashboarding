# Dashboard for newspaper articles on ukraine war

[Visit the Dashboard](https://ukraine-war-news-dashboard.azurewebsites.net/VisualizeUkraine) (only properly working on desktop and it might take some time to load)

## Serve the Dashboard locally

**Locally**

```python -m panel serve dashboards/uk_war_news/VisualizeUkraine.ipynb --address 0.0.0.0 --port 8000 --allow-websocket-origin=0.0.0.0:8000 --allow-websocket-origin=ukraine-war-news-dashboard.azurewebsites.net```

## Todo

- [ ] Translate articles
- [ ] Create better hover menus