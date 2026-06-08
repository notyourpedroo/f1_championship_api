# API Routes Mapping for Year Prefix

This document maps the current API routes to their new versions including the year prefix.

## Routes Mapping

| Current Route | New Route | Description |
| :--- | :--- | :--- |
| `/load/<file_type>` | `/load/<year>/<file_type>` | Loads data from a CSV file for a specific year. |

## Parameter Details

### `<year>`
The year of the data to be retrieved (e.g., `2025`). It corresponds to the folder name in `files/raw/<year>/`.

### `<file_type>`
The type of data file to load. Supported values:
- `races`: Race information
- `drivers`: Driver information
- `results`: Race results
- `teams`: Team information
- `scores`: Scores information

## Example Request

**Request:**
`GET /load/2025/races`

**Expected Response:**
A JSON list of race records for the year 2025.

## Implementation Details

- The `<year>` parameter is used to locate the corresponding directory in `files/raw/<year>/`.
- The `<file_type>` parameter identifies the specific CSV file to be loaded.
- The application verifies if the `file_type` is supported before attempting to read the file.
- For `races` data, the `race_date` field is automatically converted to a datetime object.
