





## Serve

**Locally**

```python -m panel serve app.py --address 0.0.0.0 --port 8000 --allow-websocket-origin=app-name.azurewebsites.net```



**Azure Web Apps**

```bash
az webapp create \
    --name MY_WEBAPP_NAME \
    --plan MY_APP_SERVICE_PLAN \
    --resource-group MY_RESOURCE_GROUP \
    --runtime "python|3.8"
```