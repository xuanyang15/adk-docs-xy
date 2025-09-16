from google.adk.tools.spanner import SpannerToolset
# TODO: Add credentials
# from google.auth import default
# credentials, project_id = default()

# Initialize the toolset
spanner_toolset = SpannerToolset(
    credentials=credentials,
)

# The toolset can be added to an agent's tools
# tools = spanner_toolset.get_tools()
