#!/bin/bash

# Script to load environment variables from a .env file
# Usage:
#   source ./load_env.sh
#   source ./load_env.sh /path/to/your/.env.custom

# Determine the .env file to use
ENV_FILE="${1:-.env}" # Use first argument or default to .env in current dir

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: Environment file '$ENV_FILE' not found." >&2
  # If sourced, 'return 1' will stop sourcing and return error to parent shell
  # If executed, 'exit 1' will exit the script
  if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    return 1 # Sourced
  else
    exit 1 # Executed
  fi
fi

echo "Loading environment variables from: $ENV_FILE"

# Read the file line by line
# Using a while loop is more robust for lines with spaces etc.
# IFS= prevents leading/trailing whitespace from being trimmed by `read`
# -r prevents backslash escapes from being interpreted
while IFS= read -r line || [[ -n "$line" ]]; do
  # Skip empty lines and comments (lines starting with #)
  if [[ -z "$line" || "$line" =~ ^\s*# ]]; then
    continue
  fi

  # Remove potential carriage returns (for files edited on Windows)
  line=$(echo "$line" | tr -d '\r')

  # Split the line into key and value at the first '='
  # This handles cases where the value itself might contain '='
  key="${line%%=*}"
  value="${line#*=}"

  # Remove leading/trailing whitespace from key (optional, but good practice)
  # key=$(echo "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  # For simplicity, assuming keys don't have surrounding whitespace in .env

  # Remove surrounding quotes from the value if present
  # Handles "value" or 'value'
  if [[ "$value" =~ ^\"(.*)\"$ || "$value" =~ ^\'(.*)\' ]]; then
    value="${BASH_REMATCH[1]}"
  fi

  # Export the variable
  # Using printf for safer handling of special characters in value
  if declare -p "$key" &>/dev/null && [[ "$(declare -p "$key")" == "declare -x "* ]]; then
    echo "  Overwriting existing exported variable: $key"
  elif declare -p "$key" &>/dev/null; then
    echo "  Overwriting existing (non-exported) variable and exporting: $key"
  else
    echo "  Setting: $key"
  fi

  export "$key=$value"

done < "$ENV_FILE"

echo "Environment variables loaded."
echo "Note: These variables are set for the current shell session if you 'source'd this script."
echo "If you ran it directly (./load_env.sh), they were set in a subshell and are now gone."

# If sourced, return 0 for success
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
  return 0
fi
