from google.adk.tools.bigquery import BigQueryToolset

# Initialize the BigQuery toolset with a specific location
bigquery_toolset = BigQueryToolset(project_id="my-project", location="US")

# The agent can now use the BigQuery tools to query datasets in the specified location.
