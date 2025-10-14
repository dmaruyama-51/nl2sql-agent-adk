from google.adk.tools.bigquery import BigQueryCredentialsConfig
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
import google.auth
import os

# Vertex AI API用の環境変数を設定
application_default_credentials, project_id = google.auth.default()
os.environ.setdefault('GOOGLE_CLOUD_PROJECT', project_id)
os.environ.setdefault('GOOGLE_CLOUD_LOCATION', 'us-central1')

credentials_config = BigQueryCredentialsConfig(
    credentials=application_default_credentials
)

tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config, 
    bigquery_tool_config=tool_config
)
